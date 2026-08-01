import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class InventoryTabButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, button):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.button = button

    def draw(self, screen):
        if not self.button.visible:
            return

        is_selected = self.button.is_selected()

        if is_selected:
            color = (72, 102, 128)
            border_color = (218, 235, 245)
        elif self.button.is_hovered:
            color = (50, 67, 84)
            border_color = (155, 181, 201)
        else:
            color = (35, 45, 57)
            border_color = (92, 109, 126)

        pygame.draw.rect(screen, color, self.rect, border_radius=7)
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=7)

        text_surface = self.button.font.render(self.button.label, True, (242, 246, 249))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class InventoryTabButton(UIElement):
    def __init__(
        self,
        scene,
        label,
        pos_x,
        pos_y,
        width,
        height,
        on_click,
        is_selected=None,
    ):
        self.label = label
        self.on_click = on_click
        self.is_selected = is_selected or (
            lambda: scene.selected_tab == self.label
        )
        self.is_hovered = False
        self.visible = True
        self.font = scene.button_font

        renderer = InventoryTabButtonRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer, background=False)

    def on_left_click(self):
        self.on_click()

    def set_visible(self, visible):
        self.visible = visible
        if not visible and self.scene.ui_focus is self:
            self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False
