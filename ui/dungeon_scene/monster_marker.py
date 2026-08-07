import pygame

from ui.renderer import Renderer


class MonsterMarkerRenderer(Renderer):
    draw_layer = -74
    HEALTH_BAR_WIDTH = 34
    HEALTH_BAR_HEIGHT = 5
    HEALTH_BAR_GAP = 5
    HEALTH_COLOR = (46, 196, 74)
    LOST_HEALTH_COLOR = (172, 38, 38)
    HEALTH_BORDER_COLOR = (18, 18, 18)

    def __init__(self, scene, pos_x, pos_y, width, height, unit):
        self.unit = unit
        self.visible = True
        self.in_combat = False
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_visible(self, visible):
        self.visible = bool(visible)

    def set_combat(self, in_combat):
        self.in_combat = bool(in_combat)

    def draw(self, screen):
        if not self.visible or not self.unit.is_alive:
            return
        radius = min(self.rect.width, self.rect.height) // 2
        fill_color = (156, 28, 28) if self.in_combat else (8, 8, 8)
        border_color = (238, 72, 72) if self.in_combat else (52, 52, 52)
        pygame.draw.circle(screen, fill_color, self.rect.center, radius)
        pygame.draw.circle(screen, border_color, self.rect.center, radius, width=2)

        health_ratio = max(0.0, min(1.0, self.unit.hp / self.unit.max_hp))
        health_rect = pygame.Rect(
            0,
            0,
            self.HEALTH_BAR_WIDTH,
            self.HEALTH_BAR_HEIGHT,
        )
        health_rect.midbottom = (
            self.rect.centerx,
            self.rect.top - self.HEALTH_BAR_GAP,
        )
        pygame.draw.rect(screen, self.LOST_HEALTH_COLOR, health_rect)

        remaining_width = round(health_rect.width * health_ratio)
        if remaining_width > 0:
            remaining_rect = health_rect.copy()
            remaining_rect.width = remaining_width
            pygame.draw.rect(screen, self.HEALTH_COLOR, remaining_rect)
        pygame.draw.rect(screen, self.HEALTH_BORDER_COLOR, health_rect, width=1)
