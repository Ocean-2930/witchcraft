import pygame

from .scene import Scene
from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import TitleButton, TitleContentRenderer


class TitleScene(Scene):
    def scene_initialize(self):
        center_x = VIRTUAL_WIDTH // 2
        button_width = 280
        button_height = 64
        button_gap = 18
        first_button_y = VIRTUAL_HEIGHT // 2 - 30

        self.title_font = pygame.font.SysFont("malgungothic", 72, bold=True)
        self.button_font = pygame.font.SysFont("malgungothic", 30, bold=True)
        self.notice_font = pygame.font.SysFont("malgungothic", 22)
        self.notice_text = ""
        self.content_renderer = TitleContentRenderer(self)

        self.start_button = TitleButton(
            self,
            "게임 시작",
            center_x,
            first_button_y,
            button_width,
            button_height,
            self.start_game,
        )
        self.settings_button = TitleButton(
            self,
            "설정",
            center_x,
            first_button_y + button_height + button_gap,
            button_width,
            button_height,
            self.open_settings,
        )
        self.quit_button = TitleButton(
            self,
            "게임 종료",
            center_x,
            first_button_y + (button_height + button_gap) * 2,
            button_width,
            button_height,
            self.game.quit,
        )

    def start_game(self):
        from .game_entry_scene import GameEntryScene

        self.switch_scene(GameEntryScene(self.game))

    def open_settings(self):
        from .settings_scene import SettingsScene

        self.switch_scene(SettingsScene(self.game, self))

    def scene_draw(self):
        screen = self.game.virtual_screen
        screen.fill((20, 18, 28))
        super().scene_draw()
