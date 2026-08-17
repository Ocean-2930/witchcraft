import pygame

from ui.renderer import ShiftRenderer
from .textures import DUNGEON_TEXTURES


class PlayerMarkerRenderer(ShiftRenderer):
    draw_layer = -75
    IDLE_FRAME_COUNT = 14
    WALK_FRAME_COUNT = 8
    IDLE_FRAME_LENGTH = 6
    WALK_FRAME_LENGTH = 3
    WALK_CONTACT_INDICES = (0, 4)
    flipped_texture_images = {}

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.facing_left = False
        self.walk_stop_index = None
        super().__init__(scene, pos_x, pos_y, width, height, background=True)

        idle_frames = DUNGEON_TEXTURES.get_sheet_frames(
            "character_idle",
            self.IDLE_FRAME_COUNT,
        )
        walk_frames = DUNGEON_TEXTURES.get_sheet_frames(
            "character_walk",
            self.WALK_FRAME_COUNT,
        )

        if not idle_frames:
            fallback = DUNGEON_TEXTURES.get_contained(
                "character",
                width,
                height,
                trim_alpha=True,
            )
            idle_frames = () if fallback is None else (fallback,)
        if not walk_frames:
            walk_frames = idle_frames

        self.add_animation(
            "idle",
            idle_frames,
            frame_lengths=[self.IDLE_FRAME_LENGTH] * len(idle_frames),
        )
        self.add_animation(
            "walk",
            walk_frames,
            frame_lengths=[self.WALK_FRAME_LENGTH] * len(walk_frames),
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

        if cache_key not in self.__class__.flipped_texture_images:
            self.__class__.flipped_texture_images[cache_key] = pygame.transform.flip(
                self.image,
                True,
                False,
            )

        return self.__class__.flipped_texture_images[cache_key]

    def shift_renderer_update(self, delta_time, game_events, mouse_position, wheel_move):
        if self.scene.should_continue_player_walk():
            self.walk_stop_index = None
            if self.current != "walk":
                self.set_animation("walk")
            return

        if self.current != "walk":
            if self.current != "idle":
                self.set_animation("idle")
            return

        if self.walk_stop_index is None:
            self.walk_stop_index = 4 if self.index < 4 else 0
            return

        if self.index == self.walk_stop_index:
            self.walk_stop_index = None
            self.set_animation("idle")

    def draw(self, screen):
        texture_image = self.get_current_texture_image()

        if texture_image is not None:
            texture_rect = texture_image.get_rect(center=self.rect.center)
            screen.blit(texture_image, texture_rect)
        else:
            pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
            pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
