import pygame

from ui.renderer import Renderer


class FloorTileRenderer(Renderer):
    draw_layer = -100

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(screen.get_rect())

        pygame.draw.rect(screen, (206, 179, 137), self.rect, border_radius=4)
        pygame.draw.rect(screen, (128, 95, 58), self.rect, width=3, border_radius=4)

        screen.set_clip(previous_clip)
