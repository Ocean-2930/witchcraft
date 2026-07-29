import pygame

from .slot_base import InventorySlot, InventorySlotRenderer


class EquipmentSlotRenderer(InventorySlotRenderer):
    def draw_contents(self, screen):
        slot = self.slot

        label_surface = slot.label_font.render(
            slot.label_text,
            True,
            (182, 195, 207),
        )
        label_rect = label_surface.get_rect(
            center=(self.rect.centerx, self.rect.top + 17)
        )
        screen.blit(label_surface, label_rect)

        if slot.item_image is not None:
            image = pygame.transform.smoothscale(slot.item_image, (62, 62))
            image_rect = image.get_rect(
                midbottom=(self.rect.centerx, self.rect.bottom - 5)
            )
            screen.blit(image, image_rect)
            return

        if not slot.item_text:
            return

        item_surface = slot.item_font.render(
            slot.item_text,
            True,
            (238, 241, 244),
        )
        item_rect = item_surface.get_rect(center=self.rect.center)
        screen.blit(item_surface, item_rect)


class EquipmentSlot(InventorySlot):
    renderer_class = EquipmentSlotRenderer

    def __init__(
        self,
        scene,
        label_text,
        item_text,
        pos_x,
        pos_y,
        width,
        height,
        on_right_click=None,
    ):
        self.label_text = label_text
        self.item_text = item_text
        self.item = None
        self.item_image = None
        self.on_right_click_callback = on_right_click
        self.label_font = scene.slot_label_font
        self.item_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_item(self, item_text, item=None):
        self.item_text = item_text

        if item is self.item:
            return

        self.item = item
        self.item_image = (
            item.get_sprite(item.item_code)
            if item is not None
            else None
        )

    def on_right_click(self):
        if self.on_right_click_callback is not None:
            self.on_right_click_callback()
