import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class InventoryPopupButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, button):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.button = button

    def draw(self, screen):
        if not self.button.visible:
            return

        color = (65, 82, 99) if self.button.is_hovered else (43, 55, 68)
        border_color = (
            (180, 199, 214)
            if self.button.is_hovered
            else (112, 130, 147)
        )
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(
            screen,
            border_color,
            self.rect,
            width=2,
            border_radius=6,
        )

        text_surface = self.button.font.render(
            self.button.text,
            True,
            (240, 244, 247),
        )
        screen.blit(
            text_surface,
            text_surface.get_rect(center=self.rect.center),
        )


class InventoryPopupButton(UIElement):
    def __init__(
        self,
        scene,
        text,
        pos_x,
        pos_y,
        width,
        height,
        on_click,
    ):
        self.text = text
        self.on_click = on_click
        self.visible = False
        self.is_hovered = False
        self.font = scene.slot_label_font
        renderer = InventoryPopupButtonRenderer(
            scene,
            pos_x,
            pos_y,
            width,
            height,
            self,
        )
        super().__init__(scene, renderer=renderer, background=False)

    def set_visible(self, visible):
        self.visible = visible
        if not visible:
            self.is_hovered = False
            if self.scene.ui_focus is self:
                self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def on_left_click(self):
        if self.visible:
            self.on_click()

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
