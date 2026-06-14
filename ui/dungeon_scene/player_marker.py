import pygame

from ui.renderer import Renderer


class PlayerMarkerRenderer(Renderer):
    draw_layer = -75

    def draw(self, screen):
        pygame.draw.circle(screen, (198, 42, 42), self.rect.center, self.rect.width // 2)
        pygame.draw.circle(screen, (88, 18, 18), self.rect.center, self.rect.width // 2, width=2)
