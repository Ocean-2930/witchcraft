import pygame
from importlib import import_module

from .slot_base import InventorySlot, InventorySlotRenderer

ItemWindow = import_module("ui.global").ItemWindow


class ItemSlotRenderer(InventorySlotRenderer):
    IMAGE_PADDING = 7

    def draw_contents(self, screen):
        slot = self.slot

        if slot.item_image is not None:
            image_size = (
                self.rect.width - self.IMAGE_PADDING * 2,
                self.rect.height - self.IMAGE_PADDING * 2,
            )
            image = pygame.transform.smoothscale(slot.item_image, image_size)
            image_rect = image.get_rect(center=self.rect.center)
            screen.blit(image, image_rect)
        elif slot.item_text:
            item_surface = slot.item_font.render(
                slot.item_text,
                True,
                (238, 241, 244),
            )
            item_rect = item_surface.get_rect(center=self.rect.center)
            screen.blit(item_surface, item_rect)

        if not slot.stack_text:
            return

        stack_surface = slot.item_font.render(
            slot.stack_text,
            True,
            (246, 224, 148),
        )
        stack_rect = stack_surface.get_rect(
            bottomright=(self.rect.right - 7, self.rect.bottom - 5)
        )
        screen.blit(stack_surface, stack_rect)


class ItemSlot(InventorySlot):
    renderer_class = ItemSlotRenderer

    def __init__(
        self,
        scene,
        item_text,
        stack_text,
        pos_x,
        pos_y,
        width,
        height,
        on_click=None,
        on_right_click=None,
        item_window_enabled_getter=None,
    ):
        self.item_text = item_text
        self.stack_text = stack_text
        self.item = None
        self.item_instance = None
        self.item_image = None
        self.on_click = on_click
        self.on_right_click_callback = on_right_click
        self.item_window_enabled_getter = item_window_enabled_getter
        self.item_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)
        self.item_window = ItemWindow(
            scene,
            lambda: self.item_instance,
        )

    def set_text(self, item_text, stack_text="", item_instance=None):
        self.item_text = item_text
        self.stack_text = stack_text
        self.item_instance = item_instance
        item = getattr(item_instance, "item", None)

        if item is self.item:
            return

        self.item = item
        self.item_image = (
            item.get_sprite(item.item_code)
            if item is not None
            else None
        )

    def set_visible(self, visible):
        super().set_visible(visible)
        if not visible:
            self.item_window.hide()

    def on_enter(self):
        self.show_item_window(self.rect.bottomright)

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        self.show_item_window(mouse_position)

    def on_exit(self):
        self.item_window.hide()

    def show_item_window(self, mouse_position):
        if (
            self.item_window_enabled_getter is not None
            and not self.item_window_enabled_getter()
        ):
            self.item_window.hide()
            return
        self.item_window.show_at(mouse_position)

    def on_left_click(self):
        if self.on_click is not None:
            self.on_click()

    def on_right_click(self):
        if self.on_right_click_callback is not None:
            self.on_right_click_callback()

    def destroy(self):
        self.item_window.destroy()
        super().destroy()
