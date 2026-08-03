import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class TitleContentRenderer(Renderer):
    draw_layer = -10

    def __init__(self, scene):
        self.title_font = pygame.font.SysFont("malgungothic", 72, bold=True)
        self.subtitle_font = pygame.font.SysFont("malgungothic", 22)
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    def draw(self, screen):
        title = self.title_font.render("Witchcraft", True, (246, 239, 255))
        screen.blit(title, title.get_rect(center=(VIRTUAL_WIDTH // 2, 168)))
        subtitle = self.subtitle_font.render("마법의 밤을 시작하세요", True, (184, 174, 208))
        screen.blit(subtitle, subtitle.get_rect(center=(VIRTUAL_WIDTH // 2, 228)))
