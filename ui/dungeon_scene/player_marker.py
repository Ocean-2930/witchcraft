import pygame

from ui.renderer import ShiftRenderer
from .textures import get_character_textures


class PlayerMarkerRenderer(ShiftRenderer):
    draw_layer = -75
    IDLE_FRAME_COUNT = 8
    WALK_FRAME_COUNT = 8
    # Seconds keep motion timing independent of the display FPS setting.
    IDLE_FRAME_SECONDS = 0.15
    WALK_FRAME_SECONDS = (0.08,) * 8
    WALK_CONTACT_INDICES = (0, 4)
    FOOT_BASELINE_RATIO = 448 / 512
    TILE_BOTTOM_MARGIN = 6

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.facing_left = False
        self.flipped_texture_images = {}
        super().__init__(scene, pos_x, pos_y, width, height, background=True)

        idle_frames = get_character_textures(scene.dungeon_inventory.character_name).get_sheet_frames(
            "character_idle",
            self.IDLE_FRAME_COUNT,
        )
        walk_frames = get_character_textures(scene.dungeon_inventory.character_name).get_sheet_frames(
            "character_walk",
            self.WALK_FRAME_COUNT,
        )

        if not idle_frames:
            fallback = get_character_textures(scene.dungeon_inventory.character_name).get_contained(
                "character",
                width,
                height,
                trim_alpha=True,
            )
            idle_frames = () if fallback is None else (fallback,)
        if not walk_frames:
            walk_frames = idle_frames

        self.frame_duration = 0.01
        walk_seconds = (
            self.WALK_FRAME_SECONDS
            if len(walk_frames) == self.WALK_FRAME_COUNT
            else (self.IDLE_FRAME_SECONDS,) * len(walk_frames)
        )

        self.add_animation(
            "idle",
            idle_frames,
            frame_lengths=[self.IDLE_FRAME_SECONDS / self.frame_duration] * len(idle_frames),
        )
        self.add_animation(
            "walk",
            walk_frames,
            frame_lengths=[seconds / self.frame_duration for seconds in walk_seconds],
        )
        self.set_start("idle")

    def set_facing_left(self, facing_left):
        self.facing_left = facing_left

    def get_current_texture_image(self):
        if self.image is None:
            return None
        if not self.facing_left:
            return self.image

        cache_key = (self.current, self.index, self.image.get_size())

        if cache_key not in self.flipped_texture_images:
            self.flipped_texture_images[cache_key] = pygame.transform.flip(
                self.image,
                True,
                False,
            )

        return self.flipped_texture_images[cache_key]

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        if self.scene.should_continue_player_walk():
            if self.current != "walk":
                self.set_animation("walk")
            self.animation_proceed(delta_time)
            return

        if self.current == "walk":
            animation = self.animations["walk"]
            frame_count = len(animation["images"])
            if frame_count != self.WALK_FRAME_COUNT or self.index in self.WALK_CONTACT_INDICES:
                self.set_animation("idle")
            else:
                # Stop exactly at the next contact even when a slow update skips it.
                remaining = (
                    self.frame_duration * animation["frame_lengths"][self.index]
                    - self.delta_time
                )
                next_index = (self.index + 1) % frame_count
                while next_index not in self.WALK_CONTACT_INDICES:
                    remaining += self.frame_duration * animation["frame_lengths"][next_index]
                    next_index = (next_index + 1) % frame_count
                if delta_time < remaining:
                    self.animation_proceed(delta_time)
                    return
                self.set_animation("idle")
                delta_time -= remaining

        self.animation_proceed(delta_time)

    def draw(self, screen):
        texture_image = self.get_current_texture_image()

        if texture_image is not None:
            # Keep the sheet's fixed foot baseline above the current tile bottom.
            foot_y = self.rect.centery + self.scene.FLOOR_TILE_HEIGHT / 2 - self.TILE_BOTTOM_MARGIN
            texture_rect = texture_image.get_rect()
            texture_rect.centerx = self.rect.centerx
            texture_rect.top = round(foot_y - texture_image.get_height() * self.FOOT_BASELINE_RATIO)
            screen.blit(texture_image, texture_rect)
        else:
            pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
            pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
