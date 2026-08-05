import pygame

from ui.renderer import Renderer


class MonsterMarkerRenderer(Renderer):
    draw_layer = -74

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.visible = True
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_visible(self, visible):
        self.visible = bool(visible)

    def draw(self, screen):
        if not self.visible:
            return
        radius = min(self.rect.width, self.rect.height) // 2
        pygame.draw.circle(screen, (8, 8, 8), self.rect.center, radius)
        pygame.draw.circle(screen, (52, 52, 52), self.rect.center, radius, width=2)
