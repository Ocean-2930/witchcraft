import pygame
import settings

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class SettingsContentRenderer(Renderer):
    draw_layer = -10

    def __init__(self, scene):
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    def draw(self, screen):
        title = self.scene.title_font.render("설정", True, (239, 249, 252))
        screen.blit(title, title.get_rect(center=(VIRTUAL_WIDTH // 2, 112)))
        self.draw_row(screen, "배경음", self.scene.format_volume(settings.BGM), 242)
        self.draw_row(screen, "효과음", self.scene.format_volume(settings.SFX), 318)

        label = self.scene.label_font.render("화면 크기", True, (218, 237, 242))
        screen.blit(label, label.get_rect(center=(VIRTUAL_WIDTH // 2, 374)))
        current_size = settings.get_screen_size()
        for button in self.scene.resolution_buttons:
            selected = (
                settings.FULLSCREEN and button.text == "전체 화면"
            ) or (
                not settings.FULLSCREEN
                and button.text == f"{current_size[0]} x {current_size[1]}"
            )
            if selected:
                pygame.draw.rect(screen, (178, 226, 236), button.rect.inflate(8, 8), width=3, border_radius=10)

    def draw_row(self, screen, label, value, center_y):
        label_surface = self.scene.label_font.render(label, True, (218, 237, 242))
        screen.blit(label_surface, label_surface.get_rect(midleft=(360, center_y)))
        value_surface = self.scene.value_font.render(value, True, (245, 251, 255))
        screen.blit(value_surface, value_surface.get_rect(midleft=(VIRTUAL_WIDTH // 2 + 380, center_y)))
