import pygame

import settings
from .scene import Scene
from settings import VIRTUAL_WIDTH
from ui import SettingsButton, SettingsContentRenderer, SettingsSlider


class SettingsScene(Scene):
    RESOLUTIONS = (
        (1280, 720),
        (1600, 900),
    )

    def __init__(self, game, previous_scene=None):
        self.previous_scene = previous_scene
        super().__init__(game)

    def scene_initialize(self):
        self.title_font = pygame.font.SysFont("malgungothic", 56, bold=True)
        self.label_font = pygame.font.SysFont("malgungothic", 28, bold=True)
        self.value_font = pygame.font.SysFont("malgungothic", 26)
        self.button_font = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.small_button_font = pygame.font.SysFont("malgungothic", 22, bold=True)

        center_x = VIRTUAL_WIDTH // 2
        self.bgm_slider = SettingsSlider(self, center_x + 160, 242, 360, 48, self.get_bgm, self.set_bgm)
        self.sfx_slider = SettingsSlider(self, center_x + 160, 318, 360, 48, self.get_sfx, self.set_sfx)

        self.resolution_buttons = []
        resolution_start_x = center_x - 220
        for index, resolution in enumerate(self.RESOLUTIONS):
            width, height = resolution
            button = SettingsButton(
                self,
                f"{width} x {height}",
                resolution_start_x + index * 220,
                438,
                180,
                50,
                lambda size=resolution: self.set_resolution(size),
                self.small_button_font,
            )
            self.resolution_buttons.append(button)

        self.fullscreen_button = SettingsButton(
            self,
            "전체 화면",
            resolution_start_x + len(self.RESOLUTIONS) * 220,
            438,
            180,
            50,
            self.set_fullscreen,
            self.small_button_font,
        )
        self.resolution_buttons.append(self.fullscreen_button)

        self.back_button = SettingsButton(self, "뒤로가기", center_x, 568, 220, 58, self.go_back)
        self.content_renderer = SettingsContentRenderer(self)

    def get_bgm(self):
        return settings.BGM

    def set_bgm(self, value):
        settings.BGM = self.clamp_volume(value)
        self.game.change_volume()

    def get_sfx(self):
        return settings.SFX

    def set_sfx(self, value):
        settings.SFX = self.clamp_volume(value)

    def set_resolution(self, size):
        width, height = size
        self.game.set_screen_size(width, height)

    def set_fullscreen(self):
        self.game.set_fullscreen()

    def go_back(self):
        from .title_scene import TitleScene

        if self.previous_scene is None:
            self.switch_scene(TitleScene(self.game))
            return

        self.switch_scene(self.previous_scene)

    def scene_draw(self):
        screen = self.game.virtual_screen
        screen.fill((18, 25, 34))
        super().scene_draw()

    @staticmethod
    def clamp_volume(value):
        return max(0.0, min(1.0, round(value, 2)))

    @staticmethod
    def format_volume(value):
        return f"{round(value * 100):3d}%"
