import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


class StairTileRenderer(Renderer):
    draw_layer = -99
    texture_images = {}

    def __init__(self, scene, pos_x, pos_y, width, height, texture_key):
        texture_size = (texture_key, int(width), int(height))

        if texture_size not in self.__class__.texture_images:
            self.__class__.texture_images[texture_size] = DUNGEON_TEXTURES.get_scaled(
                texture_key,
                width,
                height,
            )

        self.texture_image = self.__class__.texture_images[texture_size]
        super().__init__(scene, pos_x, pos_y, width, height)

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(screen.get_rect())
        if self.texture_image is not None:
            screen.blit(self.texture_image, self.rect)
        else:
            pygame.draw.rect(screen, (206, 179, 137), self.rect, border_radius=4)
            pygame.draw.rect(screen, (128, 95, 58), self.rect, width=3, border_radius=4)

        screen.set_clip(previous_clip)
