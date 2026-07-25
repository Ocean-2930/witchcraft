import pygame

from .scene import Scene
from settings import ESCAPE, TAB, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import InventoryTabButton


class InventoryScene(Scene):
    TAB_LABELS = ("장비", "스킬", "영웅", "스탯")
    PANEL_WIDTH = 960
    PANEL_HEIGHT = 600

    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.selected_tab = self.TAB_LABELS[0]
        self.tab_buttons = []

        tab_width = 180
        tab_height = 58
        tab_gap = 12
        total_tab_width = tab_width * len(self.TAB_LABELS) + tab_gap * (len(self.TAB_LABELS) - 1)
        first_tab_x = VIRTUAL_WIDTH // 2 - total_tab_width // 2 + tab_width // 2
        tab_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 56

        for index, label in enumerate(self.TAB_LABELS):
            button = InventoryTabButton(
                self,
                label,
                first_tab_x + index * (tab_width + tab_gap),
                tab_y,
                tab_width,
                tab_height,
                lambda selected_label=label: self.select_tab(selected_label),
            )
            self.tab_buttons.append(button)

    def select_tab(self, label):
        self.selected_tab = label

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[TAB]["keydown"] or game_events[ESCAPE]["keydown"]:
            self.exit_scene()
            return

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        screen = self.game.virtual_screen

        dim_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((4, 7, 11, 110))
        screen.blit(dim_surface, (0, 0))

        panel_surface = pygame.Surface(
            (self.PANEL_WIDTH, self.PANEL_HEIGHT),
            pygame.SRCALPHA,
        )
        panel_surface.fill((22, 28, 36, 225))
        panel_rect = panel_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))
        screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(screen, (132, 148, 164), panel_rect, width=2, border_radius=8)

        divider_y = panel_rect.top + 104
        pygame.draw.line(
            screen,
            (105, 119, 133),
            (panel_rect.left + 30, divider_y),
            (panel_rect.right - 30, divider_y),
            width=2,
        )

        super().scene_draw()
