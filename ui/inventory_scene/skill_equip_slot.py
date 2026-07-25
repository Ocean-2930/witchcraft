from .slot_base import InventorySlot, InventorySlotRenderer


class SkillEquipSlotRenderer(InventorySlotRenderer):
    def draw_contents(self, screen):
        slot = self.slot

        key_surface = slot.key_font.render(
            slot.key_text,
            True,
            (230, 234, 232),
        )
        key_rect = key_surface.get_rect(
            topleft=(self.rect.left + 6, self.rect.top + 4)
        )
        screen.blit(key_surface, key_rect)

        if not slot.skill_text:
            return

        skill_surface = slot.skill_font.render(
            slot.skill_text,
            True,
            (238, 241, 244),
        )
        skill_rect = skill_surface.get_rect(center=self.rect.center)
        screen.blit(skill_surface, skill_rect)


class SkillEquipSlot(InventorySlot):
    renderer_class = SkillEquipSlotRenderer

    def __init__(
        self,
        scene,
        key_text,
        skill_text,
        pos_x,
        pos_y,
        width,
        height,
    ):
        self.key_text = key_text
        self.skill_text = skill_text
        self.key_font = scene.slot_label_font
        self.skill_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_skill_text(self, skill_text):
        self.skill_text = skill_text
