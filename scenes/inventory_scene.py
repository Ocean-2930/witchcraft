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
    STAT_GROUPS = (
        (
            "기본 능력",
            (
                ("max_hp", "최대 체력", False),
                ("max_mp", "최대 마나", False),
                ("attack_power", "공격력", False),
                ("attack_speed", "공격 속도", False),
                ("move_speed", "이동 속도", False),
                ("overloaded", "과부화", False),
            ),
        ),
        (
            "공격 능력",
            (
                ("penetration", "관통력", False),
                ("accuracy", "명중", False),
                ("critical_chance", "치명타 확률", True),
                ("critical_damage", "치명타 피해", True),
                ("damage_increase", "피해 증가", True),
            ),
        ),
        (
            "방어 능력",
            (
                ("defense", "방어력", False),
                ("evasion", "회피", False),
                ("critical_evasion", "치명타 회피", True),
                ("critical_damage_reduction", "치명타 피해 감소", True),
                ("incoming_damage_reduction", "받는 피해 감소", True),
            ),
        ),
        (
            "수집 능력",
            (
                ("luck", "행운", False),
                ("equipment_drop_rate", "장비 드롭률", True),
                ("gold_drop_amount", "골드 획득량", True),
            ),
        ),
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
        elif self.selected_tab == "스탯":
            self.draw_stat_tab(screen, panel_rect)

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

    def draw_stat_tab(self, screen, panel_rect):
        dungeon_inventory = getattr(self.parent_scene, "dungeon_inventory", None)
        if dungeon_inventory is None:
            return

        try:
            calculated_stat = dungeon_inventory.get_stat()
        except ValueError:
            return

        name = getattr(calculated_stat, "name", "")
        title_text = f"스탯  ·  {name}" if name else "스탯"
        title_surface = self.section_font.render(
            title_text,
            True,
            (232, 238, 243),
        )
        screen.blit(title_surface, (panel_rect.left + 46, panel_rect.top + 112))

        column_gap = 22
        content_left = panel_rect.left + 46
        content_right = panel_rect.right - 46
        column_width = (
            content_right
            - content_left
            - column_gap * (len(self.STAT_GROUPS) - 1)
        ) // len(self.STAT_GROUPS)
        column_top = panel_rect.top + 158
        column_height = panel_rect.bottom - column_top - 38

        for index, (group_title, stat_rows) in enumerate(self.STAT_GROUPS):
            column_rect = pygame.Rect(
                content_left + index * (column_width + column_gap),
                column_top,
                column_width,
                column_height,
            )
            self.draw_stat_group(
                screen,
                column_rect,
                group_title,
                stat_rows,
                calculated_stat,
            )

    def draw_stat_group(
        self,
        screen,
        column_rect,
        group_title,
        stat_rows,
        calculated_stat,
    ):
        pygame.draw.rect(screen, (31, 39, 49), column_rect, border_radius=6)
        pygame.draw.rect(
            screen,
            (103, 119, 135),
            column_rect,
            width=2,
            border_radius=6,
        )

        group_surface = self.slot_label_font.render(
            group_title,
            True,
            (218, 228, 236),
        )
        screen.blit(
            group_surface,
            (column_rect.left + 18, column_rect.top + 15),
        )
        pygame.draw.line(
            screen,
            (82, 96, 110),
            (column_rect.left + 16, column_rect.top + 46),
            (column_rect.right - 16, column_rect.top + 46),
            width=1,
        )

        row_y = column_rect.top + 62
        row_gap = 43
        for attribute_name, label, is_percentage in stat_rows:
            value = getattr(calculated_stat, attribute_name, 0)
            value_text = self.format_stat_value(value, is_percentage)

            label_surface = self.item_font.render(
                label,
                True,
                (174, 187, 199),
            )
            value_surface = self.slot_label_font.render(
                value_text,
                True,
                (239, 243, 246),
            )
            screen.blit(label_surface, (column_rect.left + 18, row_y))
            value_rect = value_surface.get_rect(
                topright=(column_rect.right - 18, row_y - 2)
            )
            screen.blit(value_surface, value_rect)
            row_y += row_gap

    @staticmethod
    def format_stat_value(value, is_percentage):
        if isinstance(value, float):
            value_text = f"{value:.2f}".rstrip("0").rstrip(".")
        else:
            value_text = str(value)

        return f"{value_text}%" if is_percentage else value_text

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
