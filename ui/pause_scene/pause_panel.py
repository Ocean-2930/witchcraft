import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class PausePanelRenderer(Renderer):
    draw_layer = -10

    def __init__(self, scene, width=360, height=390):
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, width, height)

    def draw(self, screen):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 12, 150))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (24, 29, 34), self.rect, border_radius=8)
        pygame.draw.rect(screen, (142, 151, 158), self.rect, width=2, border_radius=8)
        title = self.scene.title_font.render("일시 정지", True, (242, 240, 230))
        screen.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 62)))
