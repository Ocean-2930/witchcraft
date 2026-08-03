import pygame

from settings import ARROW_DOWN, ARROW_UP, ENTER, VIRTUAL_WIDTH
from ui.renderer import Renderer
from ui.ui import UIElement


class ChoiceBoxRenderer(Renderer):
    draw_layer = 110

    def __init__(self, scene, pos_x, pos_y, width, height, choice_box):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.choice_box = choice_box

    def draw(self, screen):
        choice_box = self.choice_box
        if not choice_box.visible:
            return

        active_index = choice_box.get_active_index()
        for index, choice in enumerate(choice_box.choices):
            choice_rect = choice_box.get_choice_rect(index)
            is_active = index == active_index
            fill_color = (68, 55, 94) if is_active else (23, 25, 35)
            border_color = (195, 171, 230) if is_active else (105, 96, 124)
            text_color = (251, 247, 255) if is_active else (218, 212, 228)

            pygame.draw.rect(screen, fill_color, choice_rect, border_radius=8)
            pygame.draw.rect(
                screen,
                border_color,
                choice_rect,
                width=2,
                border_radius=8,
            )
            text_surface = choice_box.font.render(choice, True, text_color)
            screen.blit(
                text_surface,
                text_surface.get_rect(center=choice_rect.center),
            )


class ChoiceBox(UIElement):
    def __init__(
        self,
        scene,
        choices,
        on_select=None,
        pos_x=VIRTUAL_WIDTH // 2,
        pos_y=300,
        width=520,
        choice_height=56,
        gap=12,
    ):
        self.choices = list(choices)
        self.on_select_callback = on_select
        self.choice_height = choice_height
        self.gap = gap
        self.selected_index = 0 if self.choices else None
        self.hovered_index = None
        self.visible = True
        self.font = pygame.font.SysFont("malgungothic", 22, bold=True)
        height = self.get_required_height()
        renderer = ChoiceBoxRenderer(
            scene,
            pos_x,
            pos_y,
            width,
            height,
            self,
        )
        super().__init__(scene, renderer=renderer, background=False)

    def get_required_height(self):
        if not self.choices:
            return 0
        return len(self.choices) * self.choice_height + (len(self.choices) - 1) * self.gap

    def set_choices(self, choices):
        center_x, center_y, width, _ = self.get_transform()
        self.choices = list(choices)
        self.selected_index = 0 if self.choices else None
        self.hovered_index = None
        self.set_transform(
            center_x,
            center_y,
            width,
            self.get_required_height(),
        )

    def set_on_select(self, on_select):
        self.on_select_callback = on_select

    def get_choice_rect(self, index):
        top = self.rect.top + index * (self.choice_height + self.gap)
        return pygame.Rect(self.rect.left, top, self.rect.width, self.choice_height)

    def get_active_index(self):
        if self.hovered_index is not None:
            return self.hovered_index
        return self.selected_index

    def get_selected_choice(self):
        if self.selected_index is None:
            return None
        return self.choices[self.selected_index]

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        self.hovered_index = None

    def pos_check(self, mouse_pos):
        return self.visible and bool(self.choices) and self.rect.collidepoint(mouse_pos)

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        self.hovered_index = None
        if mouse_position is None:
            return

        for index in range(len(self.choices)):
            if self.get_choice_rect(index).collidepoint(mouse_position):
                self.hovered_index = index
                break

    def on_exit(self):
        self.hovered_index = None

    def on_left_click(self):
        if self.hovered_index is None:
            return
        self.selected_index = self.hovered_index
        self.select_current()

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        if not self.visible or not self.choices:
            return

        if game_events[ARROW_UP]["keydown"]:
            self.move_selection(-1)
        elif game_events[ARROW_DOWN]["keydown"]:
            self.move_selection(1)
        elif game_events[ENTER]["keydown"]:
            self.select_current()

    def move_selection(self, direction):
        if not self.choices:
            return
        if self.selected_index is None:
            self.selected_index = 0
            return
        self.selected_index = (self.selected_index + direction) % len(self.choices)
        self.hovered_index = None

    def select_current(self):
        choice = self.get_selected_choice()
        if choice is None or self.on_select_callback is None:
            return
        self.on_select_callback(self.selected_index, choice)

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
