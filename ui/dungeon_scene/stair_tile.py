import pygame

from ui.renderer import Renderer


class StairTileRenderer(Renderer):
    draw_layer = -99

    def __init__(self, scene, pos_x, pos_y, width, height, color):
        self.color = color
        super().__init__(scene, pos_x, pos_y, width, height)

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(screen.get_rect())
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        border_color = (92, 92, 92) if self.color == (0, 0, 0) else (205, 205, 205)
        pygame.draw.rect(screen, border_color, self.rect, width=3, border_radius=4)
        screen.set_clip(previous_clip)
