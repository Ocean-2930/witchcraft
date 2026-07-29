import pygame

from .slot_base import InventorySlot, InventorySlotRenderer


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
    ):
        self.item_text = item_text
        self.stack_text = stack_text
        self.item = None
        self.item_image = None
        self.on_click = on_click
        self.on_right_click_callback = on_right_click
        self.item_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_text(self, item_text, stack_text="", item=None):
        self.item_text = item_text
        self.stack_text = stack_text

        if item is self.item:
            return

        self.item = item
        self.item_image = (
            item.get_sprite(item.item_code)
            if item is not None
            else None
        )

    def on_left_click(self):
        if self.on_click is not None:
            self.on_click()

    def on_right_click(self):
        if self.on_right_click_callback is not None:
            self.on_right_click_callback()
