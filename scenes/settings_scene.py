import pygame

import settings
from .scene import Scene
from settings import VIRTUAL_WIDTH
from ui import SettingsButton, SettingsSlider


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

        title_surface = self.title_font.render("설정", True, (239, 249, 252))
        title_rect = title_surface.get_rect(center=(VIRTUAL_WIDTH // 2, 112))
        screen.blit(title_surface, title_rect)

        self.draw_setting_row(screen, "배경음", self.format_volume(settings.BGM), 242)
        self.draw_setting_row(screen, "효과음", self.format_volume(settings.SFX), 318)
        self.draw_resolution_row(screen)

        super().scene_draw()

    def draw_setting_row(self, screen, label, value, center_y):
        label_surface = self.label_font.render(label, True, (218, 237, 242))
        label_rect = label_surface.get_rect(midleft=(360, center_y))
        screen.blit(label_surface, label_rect)

        value_surface = self.value_font.render(value, True, (245, 251, 255))
        value_rect = value_surface.get_rect(midleft=(VIRTUAL_WIDTH // 2 + 380, center_y))
        screen.blit(value_surface, value_rect)

    def draw_resolution_row(self, screen):
        label_surface = self.label_font.render("화면 크기", True, (218, 237, 242))
        label_rect = label_surface.get_rect(center=(VIRTUAL_WIDTH // 2, 374))
        screen.blit(label_surface, label_rect)

        current_size = settings.get_screen_size()
        for button in self.resolution_buttons:
            if settings.FULLSCREEN and button.text == "전체 화면":
                pygame.draw.rect(screen, (178, 226, 236), button.rect.inflate(8, 8), width=3, border_radius=10)
            elif not settings.FULLSCREEN and button.text == f"{current_size[0]} x {current_size[1]}":
                pygame.draw.rect(screen, (178, 226, 236), button.rect.inflate(8, 8), width=3, border_radius=10)

    @staticmethod
    def clamp_volume(value):
        return max(0.0, min(1.0, round(value, 2)))

    @staticmethod
    def format_volume(value):
        return f"{round(value * 100):3d}%"
