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
    ):
        self.label_text = label_text
        self.item_text = item_text
        self.label_font = scene.slot_label_font
        self.item_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_item_text(self, item_text):
        self.item_text = item_text
