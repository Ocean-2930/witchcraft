import pygame

from .scene import Scene
from settings import ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import PausePanelRenderer, SettingsButton


class PauseScene(Scene):
    def scene_initialize(self):
        self.title_font = pygame.font.SysFont("malgungothic", 48, bold=True)
        self.button_font = pygame.font.SysFont("malgungothic", 26, bold=True)
        self.panel_renderer = PausePanelRenderer(self)

        center_x = VIRTUAL_WIDTH // 2
        button_width = 240
        button_height = 54
        button_gap = 14
        first_button_y = VIRTUAL_HEIGHT // 2 - 54

        self.resume_button = SettingsButton(
            self,
            "계속하기",
            center_x,
            first_button_y,
            button_width,
            button_height,
            self.resume,
        )
        self.settings_button = SettingsButton(
            self,
            "설정",
            center_x,
            first_button_y + (button_height + button_gap),
            button_width,
            button_height,
            self.open_settings,
        )
        self.main_button = SettingsButton(
            self,
            "메인으로",
            center_x,
            first_button_y + (button_height + button_gap) * 2,
            button_width,
            button_height,
            self.go_main,
        )
        self.quit_button = SettingsButton(
            self,
            "게임 종료",
            center_x,
            first_button_y + (button_height + button_gap) * 3,
            button_width,
            button_height,
            self.game.quit,
        )

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.resume()

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def resume(self):
        self.exit_scene()

    def open_settings(self):
        from .settings_scene import SettingsScene

        return_scene = self.parent_scene

        if return_scene is not None:
            return_scene.overlay_scene = None

        self.switch_scene(SettingsScene(self.game, return_scene))

    def go_main(self):
        from .title_scene import TitleScene

        if self.parent_scene is not None:
            self.parent_scene.overlay_scene = None

        self.switch_scene(TitleScene(self.game))
