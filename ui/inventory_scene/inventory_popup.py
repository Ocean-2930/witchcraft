import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class InventoryPopupRenderer(Renderer):
    draw_layer = 100

    def __init__(self, scene):
        super().__init__(
            scene,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            VIRTUAL_WIDTH,
            VIRTUAL_HEIGHT,
        )

    def draw(self, screen):
        if (
            self.scene.popup_mode not in ("discard", "shortcut")
            or self.scene.popup_rect is None
        ):
            return

        popup_rect = self.scene.popup_rect
        pygame.draw.rect(screen, (25, 32, 41), popup_rect, border_radius=8)
        pygame.draw.rect(
            screen,
            (135, 151, 166),
            popup_rect,
            width=2,
            border_radius=8,
        )

        title_text = (
            "단축키 선택"
            if self.scene.popup_mode == "shortcut"
            else "버릴 수량"
        )
        title_surface = self.scene.section_font.render(
            title_text,
            True,
            (237, 242, 245),
        )
        screen.blit(
            title_surface,
            title_surface.get_rect(
                center=(popup_rect.centerx, popup_rect.top + 18)
            ),
        )

        if self.scene.popup_mode == "shortcut":
            return

        amount_surface = self.scene.button_font.render(
            str(self.scene.discard_amount),
            True,
            (244, 226, 166),
        )
        screen.blit(
            amount_surface,
            amount_surface.get_rect(
                center=(popup_rect.centerx, popup_rect.top + 50)
            ),
        )
