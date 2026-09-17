import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class InventorySlotRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, slot):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.slot = slot

    def draw(self, screen):
        if not self.slot.visible:
            return

        hovered = self.slot.scene.ui_focus is self.slot
        pygame.draw.rect(screen, (40, 53, 66) if hovered else (31, 39, 49), self.rect, border_radius=5)
        pygame.draw.rect(
            screen,
            (145, 177, 201) if hovered else (82, 98, 114),
            self.rect,
            width=2,
            border_radius=5,
        )
        self.draw_contents(screen)

    def draw_contents(self, screen):
        pass


class InventorySlot(UIElement):
    renderer_class = InventorySlotRenderer

    def __init__(self, scene, pos_x, pos_y, width, height):
        self.visible = True
        renderer = self.renderer_class(
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

        if not visible and self.scene.ui_focus is self:
            self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
