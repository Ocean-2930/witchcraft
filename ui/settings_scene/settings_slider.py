import pygame

from settings import MOUSE_LEFT
from ui.renderer import Renderer
from ui.ui import UIElement


class SettingsSliderRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, slider):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.slider = slider

    def draw(self, screen):
        track_rect = pygame.Rect(0, 0, self.rect.width, 10)
        track_rect.center = self.rect.center
        fill_rect = track_rect.copy()
        fill_rect.width = max(0, int(track_rect.width * self.slider.get_value()))

        pygame.draw.rect(screen, (34, 48, 62), track_rect, border_radius=5)
        if fill_rect.width > 0:
            pygame.draw.rect(screen, (119, 205, 217), fill_rect, border_radius=5)
        pygame.draw.rect(screen, (138, 178, 192), track_rect, width=2, border_radius=5)

        knob_x = track_rect.left + fill_rect.width
        knob_radius = 15 if self.slider.is_dragging else 13
        knob_color = (232, 252, 255) if self.slider.is_hovered else (198, 235, 241)
        pygame.draw.circle(screen, (25, 35, 45), (knob_x, track_rect.centery + 2), knob_radius)
        pygame.draw.circle(screen, knob_color, (knob_x, track_rect.centery), knob_radius)
        pygame.draw.circle(screen, (92, 143, 161), (knob_x, track_rect.centery), knob_radius, width=2)


class SettingsSlider(UIElement):
    def __init__(self, scene, pos_x, pos_y, width, height, get_value, set_value):
        self.get_value = get_value
        self.set_value = set_value
        self.is_hovered = False
        self.is_dragging = False
        self.mouse_position = None

        renderer = SettingsSliderRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer)

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        if self.is_dragging:
            if game_events[MOUSE_LEFT]["status"] and mouse_position is not None:
                self.update_value(mouse_position)
            else:
                self.is_dragging = False

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        self.mouse_position = mouse_position
        if game_events[MOUSE_LEFT]["status"] and mouse_position is not None:
            self.update_value(mouse_position)

    def on_left_click(self):
        self.is_dragging = True
        if self.mouse_position is not None:
            self.update_value(self.mouse_position)

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False

    def update_value(self, mouse_position):
        track_left = self.rect.left
        raw_value = (mouse_position[0] - track_left) / self.rect.width
        self.set_value(max(0.0, min(1.0, raw_value)))

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
