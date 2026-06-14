import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class GameEntryStartButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, button):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.button = button

    def draw(self, screen):
        if self.button.is_pressed:
            color = (34, 103, 112)
            border_color = (223, 250, 248)
            offset_y = 2
        elif self.button.is_hovered:
            color = (31, 130, 137)
            border_color = (197, 244, 242)
            offset_y = 0
        else:
            color = (24, 88, 98)
            border_color = (130, 208, 211)
            offset_y = 0

        draw_rect = self.rect.move(0, offset_y)
        pygame.draw.rect(screen, color, draw_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, draw_rect, width=2, border_radius=8)

        text_surface = self.button.font.render(self.button.text, True, (244, 252, 252))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        screen.blit(text_surface, text_rect)


class GameEntryStartButton(UIElement):
    def __init__(self, scene, text, pos_x, pos_y, width, height, on_click):
        self.text = text
        self.on_click = on_click
        self.is_hovered = False
        self.is_pressed = False
        self.font = scene.button_font

        renderer = GameEntryStartButtonRenderer(scene, pos_x, pos_y, width, height, self)
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
