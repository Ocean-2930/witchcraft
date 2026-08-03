import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer
from ui.ui import UIElement


class SeedStatusMarkerRenderer(Renderer):
    draw_layer = 120

    def __init__(self, scene, pos_x, pos_y, size, marker):
        super().__init__(scene, pos_x, pos_y, size, size)
        self.marker = marker

    def draw(self, screen):
        seed = self.marker.seed_getter()
        center_x, center_y = self.rect.center
        radius = self.rect.width // 2 - 3
        points = [
            (center_x, center_y - radius),
            (center_x + radius, center_y),
            (center_x, center_y + radius),
            (center_x - radius, center_y),
        ]
        fill_color = (164, 119, 225) if seed is not None else (27, 28, 38)
        border_color = (235, 217, 255) if self.marker.is_hovered else (146, 128, 171)
        pygame.draw.polygon(screen, fill_color, points)
        pygame.draw.polygon(screen, border_color, points, width=2)

        if self.marker.is_hovered and seed is not None:
            self.draw_tooltip(screen, seed)

    def draw_tooltip(self, screen, seed):
        marker = self.marker
        title = marker.title_font.render("시드 저장됨", True, (240, 231, 252))
        value = marker.value_font.render(marker.format_seed(seed), True, (196, 181, 216))
        tooltip_width = max(title.get_width(), value.get_width()) + 28
        tooltip_rect = pygame.Rect(0, 0, tooltip_width, 72)
        tooltip_rect.midbottom = (self.rect.centerx, self.rect.top - 10)
        tooltip_rect.clamp_ip(pygame.Rect(8, 8, VIRTUAL_WIDTH - 16, VIRTUAL_HEIGHT - 16))
        pygame.draw.rect(screen, (11, 13, 19), tooltip_rect, border_radius=7)
        pygame.draw.rect(
            screen,
            (137, 119, 163),
            tooltip_rect,
            width=2,
            border_radius=7,
        )
        screen.blit(
            title,
            title.get_rect(centerx=tooltip_rect.centerx, top=tooltip_rect.top + 10),
        )
        screen.blit(
            value,
            value.get_rect(centerx=tooltip_rect.centerx, top=tooltip_rect.top + 39),
        )


class SeedStatusMarker(UIElement):
    def __init__(self, scene, seed_getter, on_clear, pos_x, pos_y, size=28):
        self.seed_getter = seed_getter
        self.on_clear_callback = on_clear
        self.is_hovered = False
        self.title_font = pygame.font.SysFont("malgungothic", 15, bold=True)
        self.value_font = pygame.font.SysFont("consolas", 15)
        renderer = SeedStatusMarkerRenderer(scene, pos_x, pos_y, size, self)
        super().__init__(scene, renderer=renderer, background=False)

    @staticmethod
    def format_seed(seed):
        digits = str(seed).zfill(16)
        return "-".join(digits[index : index + 4] for index in range(0, 16, 4))

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False

    def on_left_click(self):
        if self.seed_getter() is not None:
            self.on_clear_callback()

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
