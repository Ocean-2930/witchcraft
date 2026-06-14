import pygame

from .scene import Scene
from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import TitleButton


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

        title_surface = self.title_font.render("Witchcraft", True, (246, 239, 255))
        title_rect = title_surface.get_rect(center=(VIRTUAL_WIDTH // 2, 168))
        screen.blit(title_surface, title_rect)

        subtitle_surface = self.notice_font.render("마법의 밤을 시작하세요", True, (184, 174, 208))
        subtitle_rect = subtitle_surface.get_rect(center=(VIRTUAL_WIDTH // 2, 228))
        screen.blit(subtitle_surface, subtitle_rect)

        super().scene_draw()

        if self.notice_text:
            notice_surface = self.notice_font.render(self.notice_text, True, (220, 214, 238))
            notice_rect = notice_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 118))
            screen.blit(notice_surface, notice_rect)
