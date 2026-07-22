import pygame

from ui.renderer import Renderer


class MonsterMarkerRenderer(Renderer):
    draw_layer = -74

    def draw(self, screen):
        radius = min(self.rect.width, self.rect.height) // 2
        pygame.draw.circle(screen, (8, 8, 8), self.rect.center, radius)
        pygame.draw.circle(screen, (52, 52, 52), self.rect.center, radius, width=2)
