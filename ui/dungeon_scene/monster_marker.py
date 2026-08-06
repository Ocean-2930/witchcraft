import pygame

from ui.renderer import Renderer


class MonsterMarkerRenderer(Renderer):
    draw_layer = -74

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.visible = True
        self.in_combat = False
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_visible(self, visible):
        self.visible = bool(visible)

    def set_combat(self, in_combat):
        self.in_combat = bool(in_combat)

    def draw(self, screen):
        if not self.visible:
            return
        radius = min(self.rect.width, self.rect.height) // 2
        fill_color = (156, 28, 28) if self.in_combat else (8, 8, 8)
        border_color = (238, 72, 72) if self.in_combat else (52, 52, 52)
        pygame.draw.circle(screen, fill_color, self.rect.center, radius)
        pygame.draw.circle(screen, border_color, self.rect.center, radius, width=2)
