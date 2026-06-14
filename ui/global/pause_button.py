import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class PauseButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, button):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.button = button

    def draw(self, screen):
        if self.button.is_pressed:
            color = (56, 61, 66)
            border_color = (238, 238, 230)
            offset_y = 2
        elif self.button.is_hovered:
            color = (70, 77, 82)
            border_color = (230, 226, 210)
            offset_y = 0
        else:
            color = (45, 50, 55)
            border_color = (174, 169, 150)
            offset_y = 0

        draw_rect = self.rect.move(0, offset_y)
        pygame.draw.rect(screen, color, draw_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, draw_rect, width=2, border_radius=8)

        bar_width = max(4, draw_rect.width // 8)
        bar_height = draw_rect.height // 2
        bar_gap = draw_rect.width // 8
        left_bar = pygame.Rect(0, 0, bar_width, bar_height)
        right_bar = pygame.Rect(0, 0, bar_width, bar_height)
        left_bar.centery = draw_rect.centery
        right_bar.centery = draw_rect.centery
        left_bar.right = draw_rect.centerx - bar_gap // 2
        right_bar.left = draw_rect.centerx + bar_gap // 2

        pygame.draw.rect(screen, (245, 241, 226), left_bar, border_radius=2)
        pygame.draw.rect(screen, (245, 241, 226), right_bar, border_radius=2)


class PauseButton(UIElement):
    def __init__(self, scene, pos_x, pos_y, width, height, on_click):
        self.on_click = on_click
        self.is_hovered = False
        self.is_pressed = False

        renderer = PauseButtonRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer)

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.is_pressed = False

    def on_left_click(self):
        self.is_pressed = True
        self.on_click()

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False
        self.is_pressed = False

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
