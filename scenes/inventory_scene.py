import pygame

from .scene import Scene
from settings import ESCAPE, TAB, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import EquipmentSlot, InventoryTabButton, ItemSlot, SkillEquipSlot


class InventoryScene(Scene):
    TAB_LABELS = ("장비", "스킬", "영웅", "스탯")
    SKILL_SLOT_LABELS = ("1", "2", "3", "4", "Q", "W", "E", "R")
    EQUIPMENT_SLOTS = (
        ("weapon", "무기"),
        ("sub_weapon", "보조 무기"),
        ("armor", "방어구"),
        ("accessory_1", "장신구 1"),
        ("accessory_2", "장신구 2"),
    )
    ITEM_SLOT_COUNT = 20
    PANEL_WIDTH = 960
    PANEL_HEIGHT = 600

    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.section_font = pygame.font.SysFont("malgungothic", 22, bold=True)
        self.slot_label_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.item_font = pygame.font.SysFont("malgungothic", 14)
        self.selected_tab = self.TAB_LABELS[0]
        self.tab_buttons = []
        self.equipment_slots = []
        self.item_slots = []
        self.skill_equip_slots = []

        self.create_tab_buttons()
        self.create_equipment_slots()
        self.create_item_slots()
        self.create_skill_equip_slots()
        self.update_slot_visibility()

    def create_tab_buttons(self):
        tab_width = 180
        tab_height = 58
        tab_gap = 12
        total_tab_width = (
            tab_width * len(self.TAB_LABELS)
            + tab_gap * (len(self.TAB_LABELS) - 1)
        )
        first_tab_x = (
            VIRTUAL_WIDTH // 2 - total_tab_width // 2 + tab_width // 2
        )
        tab_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 56

        for index, label in enumerate(self.TAB_LABELS):
            button = InventoryTabButton(
                self,
                label,
                first_tab_x + index * (tab_width + tab_gap),
                tab_y,
                tab_width,
                tab_height,
                lambda selected_label=label: self.select_tab(selected_label),
            )
            self.tab_buttons.append(button)

    def create_equipment_slots(self):
        slot_size = 96
        slot_gap = 22
        total_width = (
            slot_size * len(self.EQUIPMENT_SLOTS)
            + slot_gap * (len(self.EQUIPMENT_SLOTS) - 1)
        )
        first_slot_x = VIRTUAL_WIDTH // 2 - total_width // 2
        slot_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 158

        for index, (_, label_text) in enumerate(self.EQUIPMENT_SLOTS):
            slot_rect = pygame.Rect(
                first_slot_x + index * (slot_size + slot_gap),
                slot_y,
                slot_size,
                slot_size,
            )
            self.equipment_slots.append(
                EquipmentSlot(
                    self,
                    label_text,
                    "",
                    slot_rect.centerx,
                    slot_rect.centery,
                    slot_size,
                    slot_size,
                )
            )

    def create_item_slots(self):
        columns = 10
        slot_size = 72
        slot_gap = 10
        total_width = slot_size * columns + slot_gap * (columns - 1)
        first_slot_x = VIRTUAL_WIDTH // 2 - total_width // 2
        first_slot_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 316

        for index in range(self.ITEM_SLOT_COUNT):
            row, column = divmod(index, columns)
            slot_rect = pygame.Rect(
                first_slot_x + column * (slot_size + slot_gap),
                first_slot_y + row * (slot_size + slot_gap),
                slot_size,
                slot_size,
            )
            self.item_slots.append(
                ItemSlot(
                    self,
                    "",
                    "",
                    slot_rect.centerx,
                    slot_rect.centery,
                    slot_size,
                    slot_size,
                )
            )

    def create_skill_equip_slots(self):
        columns = 4
        slot_size = 72
        slot_gap = 8
        total_width = slot_size * columns + slot_gap * (columns - 1)
        first_slot_x = VIRTUAL_WIDTH // 2 - total_width // 2
        first_slot_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 148

        for index, key_text in enumerate(self.SKILL_SLOT_LABELS):
            row, column = divmod(index, columns)
            slot_rect = pygame.Rect(
                first_slot_x + column * (slot_size + slot_gap),
                first_slot_y + row * (slot_size + slot_gap),
                slot_size,
                slot_size,
            )
            self.skill_equip_slots.append(
                SkillEquipSlot(
                    self,
                    key_text,
                    "",
                    slot_rect.centerx,
                    slot_rect.centery,
                    slot_size,
                    slot_size,
                )
            )

    def select_tab(self, label):
        self.selected_tab = label
        self.update_slot_visibility()

    def update_slot_visibility(self):
        equipment_visible = self.selected_tab == "장비"
        skill_visible = self.selected_tab == "스킬"

        for slot in (*self.equipment_slots, *self.item_slots):
            slot.set_visible(equipment_visible)

        for slot in self.skill_equip_slots:
            slot.set_visible(skill_visible)

    def refresh_inventory_texts(self):
        dungeon_inventory = getattr(self.parent_scene, "dungeon_inventory", None)

        for slot, (attribute_name, _) in zip(
            self.equipment_slots,
            self.EQUIPMENT_SLOTS,
        ):
            item_instance = (
                getattr(dungeon_inventory, attribute_name, None)
                if dungeon_inventory is not None
                else None
            )
            slot.set_item_text(self.get_item_instance_text(item_instance))

        inventory = (
            getattr(dungeon_inventory, "item_inventory", None)
            if dungeon_inventory is not None
            else None
        )
        inventory_items = getattr(inventory, "items", [])

        for index, slot in enumerate(self.item_slots):
            item_instance = (
                inventory_items[index] if index < len(inventory_items) else None
            )
            item_text = self.get_item_instance_text(item_instance)
            stack = getattr(item_instance, "stack", 1)
            stack_text = str(stack) if item_instance is not None and stack > 1 else ""
            slot.set_text(item_text, stack_text)

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[TAB]["keydown"] or game_events[ESCAPE]["keydown"]:
            self.exit_scene()
            return

        self.refresh_inventory_texts()
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        screen = self.game.virtual_screen
        self.refresh_inventory_texts()

        dim_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((4, 7, 11, 110))
        screen.blit(dim_surface, (0, 0))

        panel_surface = pygame.Surface(
            (self.PANEL_WIDTH, self.PANEL_HEIGHT),
            pygame.SRCALPHA,
        )
        panel_surface.fill((22, 28, 36, 225))
        panel_rect = panel_surface.get_rect(
            center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2)
        )
        screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(
            screen,
            (132, 148, 164),
            panel_rect,
            width=2,
            border_radius=8,
        )

        divider_y = panel_rect.top + 104
        pygame.draw.line(
            screen,
            (105, 119, 133),
            (panel_rect.left + 30, divider_y),
            (panel_rect.right - 30, divider_y),
            width=2,
        )

        if self.selected_tab == "장비":
            self.draw_equipment_titles(screen, panel_rect)
        elif self.selected_tab == "스킬":
            self.draw_skill_title(screen, panel_rect)

        super().scene_draw()

    def draw_equipment_titles(self, screen, panel_rect):
        equipment_title = self.section_font.render(
            "장비",
            True,
            (232, 238, 243),
        )
        screen.blit(equipment_title, (panel_rect.left + 46, panel_rect.top + 112))

        dungeon_inventory = getattr(self.parent_scene, "dungeon_inventory", None)
        inventory = (
            getattr(dungeon_inventory, "item_inventory", None)
            if dungeon_inventory is not None
            else None
        )
        item_count = len(getattr(inventory, "items", []))
        capacity = getattr(inventory, "capacity", self.ITEM_SLOT_COUNT)
        inventory_title = self.section_font.render(
            f"인벤토리  {item_count} / {capacity}",
            True,
            (232, 238, 243),
        )
        screen.blit(inventory_title, (panel_rect.left + 46, panel_rect.top + 274))

    def draw_skill_title(self, screen, panel_rect):
        title_surface = self.section_font.render(
            "장착 스킬",
            True,
            (232, 238, 243),
        )
        screen.blit(title_surface, (panel_rect.left + 46, panel_rect.top + 112))

    @classmethod
    def get_item_instance_text(cls, item_instance):
        item = getattr(item_instance, "item", None)
        return cls.get_item_display_name(item) if item is not None else ""

    @staticmethod
    def get_item_display_name(item):
        for attribute_name in ("name", "item_name", "item_code"):
            value = getattr(item, attribute_name, None)
            if value:
                return str(value)

        type_labels = {
            "weapon": "무기",
            "sub_weapon": "보조 무기",
            "armor": "방어구",
            "accessory": "장신구",
        }
        item_type = getattr(item, "type", None)
        return type_labels.get(item_type, item.__class__.__name__)
