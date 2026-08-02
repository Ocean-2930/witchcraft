import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class ShortcutSlotRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, slot):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.slot = slot

    def draw(self, screen):
        if not self.slot.visible:
            return

        is_active = self.slot.is_active()
        pygame.draw.rect(
            screen,
            (78, 66, 54) if is_active else (31, 39, 49),
            self.rect,
            border_radius=5,
        )
        pygame.draw.rect(
            screen,
            (236, 200, 124) if is_active else (103, 119, 135),
            self.rect,
            width=2,
            border_radius=5,
        )

        item_instance = self.slot.get_item()
        item = getattr(item_instance, "item", None)
        item_image = (
            item.get_sprite(item.item_code) if item is not None else None
        )
        if item_image is not None:
            padding = max(7, round(min(self.rect.size) * 0.125))
            image = pygame.transform.smoothscale(
                item_image,
                (
                    self.rect.width - padding * 2,
                    self.rect.height - padding * 2,
                ),
            )
            screen.blit(image, image.get_rect(center=self.rect.center))
        else:
            skill = self.slot.get_skill()
            skill_base = getattr(skill, "skill", skill)
            get_icon = getattr(skill_base, "get_icon", None)
            has_icon = getattr(skill_base, "has_icon", lambda: False)()
            skill_icon = (
                get_icon()
                if get_icon is not None
                and (has_icon or self.slot.use_skill_fallback())
                else None
            )
            if skill_icon is not None:
                padding = max(7, round(min(self.rect.size) * 0.125))
                image = pygame.transform.smoothscale(
                    skill_icon,
                    (
                        self.rect.width - padding * 2,
                        self.rect.height - padding * 2,
                    ),
                )
                screen.blit(image, image.get_rect(center=self.rect.center))
            else:
                skill_name = getattr(skill_base, "name", "")
                if skill_name:
                    skill_surface = self.slot.content_font.render(
                        skill_name,
                        True,
                        (
                            (255, 238, 190)
                            if is_active
                            else (238, 241, 244)
                        ),
                    )
                    screen.blit(
                        skill_surface,
                        skill_surface.get_rect(center=self.rect.center),
                    )

        if item_instance is not None:
            stack_surface = self.slot.content_font.render(
                str(item_instance.stack),
                True,
                (246, 224, 148),
            )
            stack_rect = stack_surface.get_rect(
                bottomright=(self.rect.right - 7, self.rect.bottom - 5)
            )
            screen.blit(stack_surface, stack_rect)

        key_surface = self.slot.key_font.render(
            self.slot.label,
            True,
            (255, 238, 190) if is_active else (230, 234, 232),
        )
        screen.blit(
            key_surface,
            key_surface.get_rect(
                topleft=(self.rect.left + 6, self.rect.top + 4)
            ),
        )


class ShortcutSlot(UIElement):
    def __init__(
        self,
        scene,
        label,
        pos_x,
        pos_y,
        width,
        height,
        item_getter,
        skill_getter,
        active_label_getter,
        skill_fallback_getter,
        on_click=None,
    ):
        self.label = label
        self.item_getter = item_getter
        self.skill_getter = skill_getter
        self.active_label_getter = active_label_getter
        self.skill_fallback_getter = skill_fallback_getter
        self.on_click = on_click
        self.visible = True
        self.key_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.content_font = pygame.font.SysFont("malgungothic", 14)
        renderer = ShortcutSlotRenderer(
            scene, pos_x, pos_y, width, height, self
        )
        super().__init__(scene, renderer=renderer, background=False)

    def get_item(self):
        return self.item_getter(self.label) if self.item_getter else None

    def get_skill(self):
        return self.skill_getter(self.label) if self.skill_getter else None

    def is_active(self):
        return (
            self.active_label_getter is not None
            and self.active_label_getter() == self.label
        )

    def use_skill_fallback(self):
        return (
            self.skill_fallback_getter is not None
            and self.skill_fallback_getter(self.label)
        )

    def set_visible(self, visible):
        self.visible = visible
        if not visible and self.scene.ui_focus is self:
            self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def on_left_click(self):
        if self.on_click is not None:
            self.on_click(self.label)

    def destroy(self):
        super().destroy()
        self.renderer.destroy()


class ShortcutBarRenderer(Renderer):
    def draw(self, screen):
        pass


class ShortcutBar(UIElement):
    def __init__(
        self,
        scene,
        labels,
        pos_x,
        pos_y,
        columns,
        slot_width,
        slot_height,
        horizontal_gap,
        vertical_gap,
        item_getter=None,
        skill_getter=None,
        skill_fallback_getter=None,
        on_slot_click=None,
    ):
        self.labels = tuple(labels)
        self.columns = columns
        self.slot_width = slot_width
        self.slot_height = slot_height
        self.horizontal_gap = horizontal_gap
        self.vertical_gap = vertical_gap
        self.item_getter = item_getter
        self.skill_getter = skill_getter
        self.skill_fallback_getter = skill_fallback_getter
        self.on_slot_click = on_slot_click
        self.active_label = None
        self.visible = True
        width, height = self.get_layout_size()
        renderer = ShortcutBarRenderer(
            scene, pos_x, pos_y, width, height
        )
        super().__init__(scene, renderer=renderer, background=False)
        self.slots = [
            ShortcutSlot(
                scene,
                label,
                pos_x,
                pos_y,
                slot_width,
                slot_height,
                item_getter,
                skill_getter,
                lambda: self.active_label,
                skill_fallback_getter,
                on_slot_click,
            )
            for label in self.labels
        ]
        self.position_slots()

    def get_layout_size(self):
        rows = (len(self.labels) + self.columns - 1) // self.columns
        return (
            self.columns * self.slot_width
            + max(0, self.columns - 1) * self.horizontal_gap,
            rows * self.slot_height
            + max(0, rows - 1) * self.vertical_gap,
        )

    def set_layout(
        self,
        pos_x,
        pos_y,
        columns=None,
        slot_width=None,
        slot_height=None,
        horizontal_gap=None,
        vertical_gap=None,
    ):
        if columns is not None:
            self.columns = columns
        if slot_width is not None:
            self.slot_width = slot_width
        if slot_height is not None:
            self.slot_height = slot_height
        if horizontal_gap is not None:
            self.horizontal_gap = horizontal_gap
        if vertical_gap is not None:
            self.vertical_gap = vertical_gap
        width, height = self.get_layout_size()
        self.set_transform(pos_x, pos_y, width, height)
        self.position_slots()

    def position_slots(self):
        for index, slot in enumerate(self.slots):
            row, column = divmod(index, self.columns)
            slot.set_transform(
                self.rect.left
                + column * (self.slot_width + self.horizontal_gap)
                + self.slot_width // 2,
                self.rect.top
                + row * (self.slot_height + self.vertical_gap)
                + self.slot_height // 2,
                self.slot_width,
                self.slot_height,
            )

    def set_active_label(self, label):
        self.active_label = label

    def set_visible(self, visible):
        self.visible = visible
        for slot in self.slots:
            slot.set_visible(visible)

    def pos_check(self, mouse_pos):
        return False

    def destroy(self):
        for slot in self.slots:
            slot.destroy()
        self.slots.clear()
        super().destroy()
        self.renderer.destroy()
