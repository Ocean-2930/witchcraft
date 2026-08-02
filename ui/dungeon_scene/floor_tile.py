import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


class FloorTileRenderer(Renderer):
    draw_layer = -100
    texture_key = "floor"
    texture_images = {}
    filter_images = {}
    FILTER_ALPHA = 96
    FILTER_YELLOW = (255, 220, 40)
    FILTER_RED = (230, 45, 45)

    def __init__(self, scene, pos_x, pos_y, width, height):
        texture_size = (int(width), int(height))

        if texture_size not in self.__class__.texture_images:
            self.__class__.texture_images[texture_size] = DUNGEON_TEXTURES.get_scaled(
                self.texture_key,
                width,
                height,
            )

        self.texture_image = self.__class__.texture_images[texture_size]
        self.filter_color = None
        super().__init__(scene, pos_x, pos_y, width, height)

    def filter_yellow(self):
        self.filter_color = self.FILTER_YELLOW

    def filter_red(self):
        self.filter_color = self.FILTER_RED

    def filter_clean(self):
        self.filter_color = None

    @classmethod
    def get_filter_image(cls, color, width, height):
        cache_key = (color, int(width), int(height))

        if cache_key not in cls.filter_images:
            filter_image = pygame.Surface(cache_key[1:], pygame.SRCALPHA)
            filter_image.fill((*color, cls.FILTER_ALPHA))
            cls.filter_images[cache_key] = filter_image

        return cls.filter_images[cache_key]

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(screen.get_rect())

        if self.texture_image is not None:
            screen.blit(self.texture_image, self.rect)
        else:
            pygame.draw.rect(screen, (206, 179, 137), self.rect, border_radius=4)
            pygame.draw.rect(screen, (128, 95, 58), self.rect, width=3, border_radius=4)

        if self.filter_color is not None:
            screen.blit(
                self.get_filter_image(
                    self.filter_color,
                    self.rect.width,
                    self.rect.height,
                ),
                self.rect,
            )

        screen.set_clip(previous_clip)
