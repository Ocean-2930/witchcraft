from .slot_base import InventorySlot, InventorySlotRenderer


class ItemSlotRenderer(InventorySlotRenderer):
    def draw_contents(self, screen):
        slot = self.slot

        if slot.item_text:
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
    ):
        self.item_text = item_text
        self.stack_text = stack_text
        self.item_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_text(self, item_text, stack_text=""):
        self.item_text = item_text
        self.stack_text = stack_text
