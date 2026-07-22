import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


class PlayerMarkerRenderer(Renderer):
    draw_layer = -75
    texture_images = {}
    flipped_texture_images = {}

    def __init__(self, scene, pos_x, pos_y, width, height):
        texture_size = (int(width), int(height))

        if texture_size not in self.__class__.texture_images:
            self.__class__.texture_images[texture_size] = DUNGEON_TEXTURES.get_contained(
                "character",
                width,
                height,
                trim_alpha=True,
            )

        self.texture_image = self.__class__.texture_images[texture_size]
        self.facing_left = False
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_facing_left(self, facing_left):
        self.facing_left = facing_left

    def get_current_texture_image(self):
        if self.texture_image is None:
            return None
        if not self.facing_left:
            return self.texture_image

        texture_size = self.texture_image.get_size()

        if texture_size not in self.__class__.flipped_texture_images:
            self.__class__.flipped_texture_images[texture_size] = pygame.transform.flip(
                self.texture_image,
                True,
                False,
            )

        return self.__class__.flipped_texture_images[texture_size]

    def draw(self, screen):
        texture_image = self.get_current_texture_image()

        if texture_image is not None:
            texture_rect = texture_image.get_rect(center=self.rect.center)
            screen.blit(texture_image, texture_rect)
        else:
            pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
            pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
