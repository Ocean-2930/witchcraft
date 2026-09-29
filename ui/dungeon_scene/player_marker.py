import pygame
from units.character_definitions import load_character_motion_settings

from ui.renderer import ShiftRenderer
from .textures import get_character_textures


class PlayerMarkerRenderer(ShiftRenderer):
    draw_layer = -75
    IDLE_FRAME_COUNT = 8
    WALK_FRAME_COUNT = 8
    MOTION_FRAME_SECONDS = 0.05
    # Seconds keep motion timing independent of the display FPS setting.
    IDLE_FRAME_SECONDS = 0.15
    WALK_FRAME_SECONDS = (0.08,) * 8
    WALK_CONTACT_INDICES = (0, 4)
    FOOT_BASELINE_RATIO = 448 / 512
    TILE_BOTTOM_MARGIN = 6

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.facing_left = False
        self.flipped_texture_images = {}
        self.motion_settings = load_character_motion_settings(scene.dungeon_inventory.character_name)
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

    @property
    def is_playing_motion(self):
        return self.current not in (None, "idle", "walk")

    def play_motion(self, motion):
        """Play once, holding the standing pose when the requested sheet is absent."""
        if motion is None or motion in ("idle", "walk") or self.is_playing_motion:
            return False
        if motion not in self.animations:
            textures = get_character_textures(self.scene.dungeon_inventory.character_name)
            frames = textures.get_sheet_frames(f"character_{motion}", 8)
            if not frames:
                idle_frames = self.animations["idle"]["base_images"]
                if not idle_frames:
                    return False
                frames = (idle_frames[0],) * 8
                # Standing pixels must use standing alignment, not the missing motion's.
                config = dict(self.motion_settings.get("idle", {}))
                if config.get("frame_offsets"):
                    config["frame_offsets"] = [config["frame_offsets"][0]] * 8
                self.motion_settings[motion] = config
            self.add_animation(
                motion, frames,
                frame_lengths=[self.MOTION_FRAME_SECONDS / self.frame_duration] * len(frames),
                loop=False, next_animation="idle",
            )
        self.set_animation(motion, update_formal=False)
        return True

    def set_facing_left(self, facing_left):
        self.facing_left = facing_left

    def get_current_texture_image(self):
        if self.image is None:
            return None
        scale = self.motion_settings.get(self.current, {}).get("scale", 1.0)
        if not self.facing_left and scale == 1.0:
            return self.image

        cache_key = (self.current, self.index, self.image.get_size(), self.facing_left, scale)

        if cache_key not in self.flipped_texture_images:
            image = self.image
            if scale != 1.0:
                image = pygame.transform.smoothscale(image, (
                    max(1, round(image.get_width() * scale)),
                    max(1, round(image.get_height() * scale)),
                ))
            if self.facing_left:
                image = pygame.transform.flip(image, True, False)
            self.flipped_texture_images[cache_key] = image

        return self.flipped_texture_images[cache_key]

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        if self.is_playing_motion:
            self.animation_proceed(delta_time)
            return
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

    def get_texture_rect(self, texture_image):
        """Place each sheet's configured anchor at the shared tile foot position."""
        config = self.motion_settings.get(self.current, {})
        anchor_x, anchor_y = config.get("anchor", (256, 448))
        offset_x, offset_y = config.get("offset", (0, 0))
        frame_offsets = config.get("frame_offsets", ())
        if frame_offsets:
            frame_x, frame_y = frame_offsets[self.index]
            offset_x += frame_x
            offset_y += frame_y
        if self.facing_left:
            anchor_x = 512 - anchor_x
            offset_x = -offset_x
        foot_y = self.rect.centery + self.scene.FLOOR_TILE_HEIGHT / 2 - self.TILE_BOTTOM_MARGIN
        rect = texture_image.get_rect()
        rect.left = round(self.rect.centerx + (offset_x - anchor_x) * rect.width / 512)
        rect.top = round(foot_y + (offset_y - anchor_y) * rect.height / 512)
        return rect

    def draw(self, screen):
        texture_image = self.get_current_texture_image()

        if texture_image is not None:
            texture_rect = self.get_texture_rect(texture_image)
            screen.blit(texture_image, texture_rect)
        else:
            pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
            pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
