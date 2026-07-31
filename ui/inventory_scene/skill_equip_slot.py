import pygame

from .slot_base import InventorySlot, InventorySlotRenderer


class SkillEquipSlotRenderer(InventorySlotRenderer):
    IMAGE_PADDING = 9

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
        elif slot.skill_text:
            skill_surface = slot.skill_font.render(
                slot.skill_text,
                True,
                (238, 241, 244),
            )
            skill_rect = skill_surface.get_rect(center=self.rect.center)
            screen.blit(skill_surface, skill_rect)

        if slot.stack_text:
            stack_surface = slot.skill_font.render(
                slot.stack_text,
                True,
                (246, 224, 148),
            )
            stack_rect = stack_surface.get_rect(
                bottomright=(self.rect.right - 7, self.rect.bottom - 5)
            )
            screen.blit(stack_surface, stack_rect)

        key_surface = slot.key_font.render(
            slot.key_text,
            True,
            (230, 234, 232),
        )
        key_rect = key_surface.get_rect(
            topleft=(self.rect.left + 6, self.rect.top + 4)
        )
        screen.blit(key_surface, key_rect)


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
        on_click=None,
    ):
        self.key_text = key_text
        self.skill_text = skill_text
        self.item_image = None
        self.stack_text = ""
        self.on_click = on_click
        self.key_font = scene.slot_label_font
        self.skill_font = scene.item_font
        super().__init__(scene, pos_x, pos_y, width, height)

    def set_skill_text(self, skill_text):
        self.skill_text = skill_text
        self.item_image = None
        self.stack_text = ""

    def set_item(self, item_instance):
        item = item_instance.item
        self.skill_text = item.item_code
        self.item_image = item.get_sprite(item.item_code)
        self.stack_text = str(item_instance.stack)

    def on_left_click(self):
        if self.on_click is not None:
            self.on_click()
