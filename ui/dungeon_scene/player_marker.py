import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


class PlayerMarkerRenderer(Renderer):
    draw_layer = -75
    IDLE_FRAME_COUNT = 14
    IDLE_FRAME_DURATION = 0.1
    texture_images = {}
    flipped_texture_images = {}

    def __init__(self, scene, pos_x, pos_y, width, height):
        texture_size = (int(width), int(height))

        if texture_size not in self.__class__.texture_images:
            idle_frames = DUNGEON_TEXTURES.get_sheet_frames(
                "character_idle",
                self.IDLE_FRAME_COUNT,
            )
            self.__class__.texture_images[texture_size] = tuple(
                pygame.transform.smoothscale(frame, texture_size)
                for frame in idle_frames
            )

            if not self.__class__.texture_images[texture_size]:
                fallback = DUNGEON_TEXTURES.get_contained(
                    "character",
                    width,
                    height,
                    trim_alpha=True,
                )
                self.__class__.texture_images[texture_size] = (
                    () if fallback is None else (fallback,)
                )

        self.texture_frames = self.__class__.texture_images[texture_size]
        self.frame_index = 0
        self.frame_elapsed = 0.0
        self.facing_left = False
        super().__init__(scene, pos_x, pos_y, width, height)
        self.scene.background_listeners.append(self)

    def set_facing_left(self, facing_left):
        self.facing_left = facing_left

    def get_current_texture_image(self):
        if not self.texture_frames:
            return None
        texture_image = self.texture_frames[self.frame_index]
        if not self.facing_left:
            return texture_image

        cache_key = (texture_image.get_size(), self.frame_index)

        if cache_key not in self.__class__.flipped_texture_images:
            self.__class__.flipped_texture_images[cache_key] = pygame.transform.flip(
                texture_image,
                True,
                False,
            )

        return self.__class__.flipped_texture_images[cache_key]

    def renderer_update(self, delta_time, game_events, mouse_position, wheel_move):
        if len(self.texture_frames) <= 1:
            return

        self.frame_elapsed += delta_time
        while self.frame_elapsed >= self.IDLE_FRAME_DURATION:
            self.frame_elapsed -= self.IDLE_FRAME_DURATION
            self.frame_index = (self.frame_index + 1) % len(self.texture_frames)

    def draw(self, screen):
        texture_image = self.get_current_texture_image()

        if texture_image is not None:
            texture_rect = texture_image.get_rect(center=self.rect.center)
            screen.blit(texture_image, texture_rect)
        else:
            pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
            pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
