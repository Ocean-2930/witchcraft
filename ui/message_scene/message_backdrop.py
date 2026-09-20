import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class MessageBackdropRenderer(Renderer):
    draw_layer = -10

    def __init__(self, scene):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 9, 16, 235))
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2,
                         VIRTUAL_WIDTH, VIRTUAL_HEIGHT, image_route=overlay)
