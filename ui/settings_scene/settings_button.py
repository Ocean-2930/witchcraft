import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class SettingsButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, button):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.button = button

    def draw(self, screen):
        if self.button.is_pressed:
            color = (72, 119, 135)
            border_color = (225, 248, 255)
            offset_y = 2
        elif self.button.is_hovered:
            color = (60, 101, 122)
            border_color = (197, 235, 244)
            offset_y = 0
        else:
            color = (42, 67, 88)
            border_color = (117, 163, 184)
            offset_y = 0

        draw_rect = self.rect.move(0, offset_y)
        pygame.draw.rect(screen, color, draw_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, draw_rect, width=2, border_radius=8)

        text_surface = self.button.font.render(self.button.text, True, (245, 251, 255))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)


class SettingsButton(UIElement):
    def __init__(self, scene, text, pos_x, pos_y, width, height, on_click, font=None):
        self.text = text
        self.on_click = on_click
        self.is_hovered = False
        self.is_pressed = False
        self.font = font or scene.button_font

        renderer = SettingsButtonRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer)

    def set_text(self, text):
        self.text = text

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
