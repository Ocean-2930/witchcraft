import pygame

from .slot_base import InventorySlot, InventorySlotRenderer


class EquipmentSlotRenderer(InventorySlotRenderer):
    IMAGE_PADDING = 6

    def draw(self, screen):
        if not self.slot.visible:
            return

        self.draw_label(screen)
        super().draw(screen)

    def draw_label(self, screen):
        slot = self.slot
        label_surface = slot.label_font.render(
            slot.label_text,
            True,
            (182, 195, 207),
        )
        label_rect = label_surface.get_rect(
            midbottom=(self.rect.centerx, self.rect.top - 7)
        )
        screen.blit(label_surface, label_rect)

    def draw_contents(self, screen):
        slot = self.slot

        if slot.item_image is not None:
            available_size = self.rect.width - self.IMAGE_PADDING * 2
            source_width, source_height = slot.item_image.get_size()
            scale = min(
                available_size / source_width,
                available_size / source_height,
            )
            image_size = (
                max(1, round(source_width * scale)),
                max(1, round(source_height * scale)),
            )
            image = pygame.transform.smoothscale(slot.item_image, image_size)
            image_rect = image.get_rect(center=self.rect.center)
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
