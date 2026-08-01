import pygame

from items import Equip
from .scene import Scene
from settings import ESCAPE, MOUSE_LEFT, TAB, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import (
    EquipmentSlot,
    InventoryContentRenderer,
    InventoryPanelRenderer,
    InventoryPopupButton,
    InventoryPopupRenderer,
    InventoryTabButton,
    ItemSlot,
    SkillEquipSlot,
    SkillNodeListView,
)


class InventoryScene(Scene):
    TAB_LABELS = ("장비", "스킬", "영웅", "스탯")
    STAT_TAB_LABELS = ("플레이어", "패시브")
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
        self.selected_stat_tab = self.STAT_TAB_LABELS[0]
        self.tab_buttons = []
        self.stat_tab_buttons = []
        self.equipment_slots = []
        self.item_slots = []
        self.skill_equip_slots = []
        self.skill_slot_default_transforms = []
        self.popup_buttons = {}
        self.popup_mode = None
        self.popup_rect = None
        self.popup_interacted_this_frame = False
        self.selected_item_index = None
        self.discard_amount = 1

        self.panel_renderer = InventoryPanelRenderer(
            self,
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
        )
        self.content_renderer = InventoryContentRenderer(
            self,
            self.PANEL_WIDTH,
            self.PANEL_HEIGHT,
        )
        self.popup_renderer = InventoryPopupRenderer(self)
        self.create_tab_buttons()
        self.create_stat_tab_buttons()
        self.create_equipment_slots()
        self.create_item_slots()
        self.create_skill_equip_slots()
        self.create_skill_node_list_view()
        self.create_popup_buttons()
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

        for index, (attribute_name, label_text) in enumerate(
            self.EQUIPMENT_SLOTS
        ):
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
                    lambda equipment_attribute=attribute_name: (
                        self.unequip_item(equipment_attribute)
                    ),
                )
            )

    def create_stat_tab_buttons(self):
        button_width = 150
        button_height = 42
        button_gap = 10
        panel_left = (VIRTUAL_WIDTH - self.PANEL_WIDTH) // 2
        first_button_x = panel_left + 46 + button_width // 2
        button_y = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2 + 137

        for index, label in enumerate(self.STAT_TAB_LABELS):
            button = InventoryTabButton(
                self,
                label,
                first_button_x + index * (button_width + button_gap),
                button_y,
                button_width,
                button_height,
                lambda selected_label=label: self.select_stat_tab(
                    selected_label
                ),
                lambda selected_label=label: (
                    self.selected_stat_tab == selected_label
                ),
            )
            button.set_visible(False)
            self.stat_tab_buttons.append(button)

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
                    lambda selected_index=index: self.open_item_actions(
                        selected_index
                    ),
                    lambda selected_index=index: self.equip_item_at_index(
                        selected_index
                    ),
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
                    lambda selected_key=key_text: self.assign_item_to_hotbar(
                        selected_key
                    ),
                )
            )
            self.skill_slot_default_transforms.append(
                (
                    slot_rect.centerx,
                    slot_rect.centery,
                    slot_size,
                    slot_size,
                )
            )

    def create_skill_node_list_view(self):
        panel_left = (VIRTUAL_WIDTH - self.PANEL_WIDTH) // 2
        panel_top = (VIRTUAL_HEIGHT - self.PANEL_HEIGHT) // 2
        content_rect = pygame.Rect(
            panel_left + 38,
            panel_top + 118,
            self.PANEL_WIDTH - 76,
            self.PANEL_HEIGHT - 146,
        )
        self.skill_node_list_view = SkillNodeListView(
            self,
            content_rect.centerx,
            content_rect.centery,
            content_rect.width,
            content_rect.height,
            lambda: getattr(self.parent_scene, "dungeon_inventory", None),
        )

    def create_popup_buttons(self):
        button_specs = (
            (
                "equip",
                "장착",
                VIRTUAL_WIDTH // 2,
                280,
                200,
                44,
                self.equip_selected_item,
            ),
            ("use", "사용", VIRTUAL_WIDTH // 2, 320, 200, 44, self.use_selected_item),
            (
                "shortcut",
                "단축키",
                VIRTUAL_WIDTH // 2,
                374,
                200,
                44,
                self.assign_selected_item_shortcut,
            ),
            (
                "discard",
                "버리기",
                VIRTUAL_WIDTH // 2,
                428,
                200,
                44,
                self.open_discard_popup,
            ),
            (
                "decrease",
                "<",
                VIRTUAL_WIDTH // 2 - 80,
                350,
                48,
                48,
                lambda: self.change_discard_amount(-1),
            ),
            (
                "increase",
                ">",
                VIRTUAL_WIDTH // 2 + 80,
                350,
                48,
                48,
                lambda: self.change_discard_amount(1),
            ),
            (
                "confirm_discard",
                "버리기",
                VIRTUAL_WIDTH // 2 - 62,
                430,
                112,
                44,
                self.discard_selected_item,
            ),
            (
                "cancel",
                "취소",
                VIRTUAL_WIDTH // 2 + 62,
                430,
                112,
                44,
                self.close_item_popup,
            ),
        )

        for key, text, pos_x, pos_y, width, height, on_click in button_specs:
            self.popup_buttons[key] = InventoryPopupButton(
                self,
                text,
                pos_x,
                pos_y,
                width,
                height,
                on_click,
            )

    def select_tab(self, label):
        self.close_item_popup()
        self.selected_tab = label
        self.update_slot_visibility()

    def select_stat_tab(self, label):
        if label not in self.STAT_TAB_LABELS:
            return

        self.selected_stat_tab = label

    def open_item_actions(self, item_index):
        if self.selected_tab != "장비":
            return

        inventory_items = self.get_inventory_items()
        if item_index >= len(inventory_items):
            return

        self.selected_item_index = item_index
        self.popup_mode = "actions"
        self.popup_interacted_this_frame = True
        self.position_action_buttons()
        self.update_popup_visibility()

    def open_discard_popup(self):
        item_instance = self.get_selected_item()
        if item_instance is None:
            self.close_item_popup()
            return

        self.discard_amount = 1
        self.popup_mode = "discard"
        self.popup_interacted_this_frame = True
        self.position_discard_popup()
        self.update_popup_visibility()

    def close_item_popup(self):
        self.popup_mode = None
        self.popup_rect = None
        self.selected_item_index = None
        self.discard_amount = 1
        self.restore_skill_equip_slot_positions()
        self.update_popup_visibility()
        self.update_slot_visibility()

    def update_popup_visibility(self):
        item = getattr(self.get_selected_item(), "item", None)
        can_use = callable(getattr(item, "use", None))
        can_equip = isinstance(item, Equip)

        action_visibility = {
            "equip": self.popup_mode == "actions" and can_equip,
            "use": self.popup_mode == "actions" and can_use,
            "shortcut": self.popup_mode == "actions" and can_use,
            "discard": self.popup_mode == "actions",
        }
        discard_keys = ("decrease", "increase", "confirm_discard", "cancel")

        for key, visible in action_visibility.items():
            self.popup_buttons[key].set_visible(visible)
        for key in discard_keys:
            self.popup_buttons[key].set_visible(self.popup_mode == "discard")

    def position_action_buttons(self):
        item_instance = self.get_selected_item()
        item = getattr(item_instance, "item", None)
        can_use = callable(getattr(item, "use", None))
        can_equip = isinstance(item, Equip)
        if can_equip:
            visible_keys = ("equip", "discard")
        elif can_use:
            visible_keys = ("use", "shortcut", "discard")
        else:
            visible_keys = ("discard",)
        selected_slot = self.item_slots[self.selected_item_index]
        button_width = 104
        button_height = 36
        button_gap = 4
        total_height = (
            button_height * len(visible_keys)
            + button_gap * (len(visible_keys) - 1)
        )
        popup_left = self.get_context_popup_left(
            selected_slot.rect,
            button_width,
        )
        panel_bottom = (VIRTUAL_HEIGHT + self.PANEL_HEIGHT) // 2
        popup_top = min(
            selected_slot.rect.top,
            panel_bottom - total_height - 12,
        )

        for index, key in enumerate(visible_keys):
            self.popup_buttons[key].set_transform(
                popup_left + button_width // 2,
                popup_top + button_height // 2 + index * (
                    button_height + button_gap
                ),
                button_width,
                button_height,
            )

        self.popup_rect = pygame.Rect(
            popup_left,
            popup_top,
            button_width,
            total_height,
        )

    def position_discard_popup(self):
        selected_slot = self.item_slots[self.selected_item_index]
        popup_width = 164
        popup_height = 118
        popup_left = self.get_context_popup_left(
            selected_slot.rect,
            popup_width,
        )
        panel_bottom = (VIRTUAL_HEIGHT + self.PANEL_HEIGHT) // 2
        popup_top = min(
            selected_slot.rect.top,
            panel_bottom - popup_height - 12,
        )
        self.popup_rect = pygame.Rect(
            popup_left,
            popup_top,
            popup_width,
            popup_height,
        )

        self.popup_buttons["decrease"].set_transform(
            popup_left + 34,
            popup_top + 50,
            34,
            30,
        )
        self.popup_buttons["increase"].set_transform(
            popup_left + popup_width - 34,
            popup_top + 50,
            34,
            30,
        )
        self.popup_buttons["confirm_discard"].set_transform(
            popup_left + 42,
            popup_top + 94,
            72,
            30,
        )
        self.popup_buttons["cancel"].set_transform(
            popup_left + popup_width - 42,
            popup_top + 94,
            72,
            30,
        )

    def position_shortcut_popup(self):
        popup_width = 352
        popup_height = 220
        popup_left = VIRTUAL_WIDTH // 2 - popup_width // 2
        popup_top = VIRTUAL_HEIGHT // 2 - popup_height // 2
        self.popup_rect = pygame.Rect(
            popup_left,
            popup_top,
            popup_width,
            popup_height,
        )

        columns = 4
        slot_size = 72
        slot_gap = 8
        slots_width = slot_size * columns + slot_gap * (columns - 1)
        first_left = self.popup_rect.centerx - slots_width // 2
        first_top = popup_top + 48

        for index, slot in enumerate(self.skill_equip_slots):
            row, column = divmod(index, columns)
            slot.set_transform(
                first_left + column * (slot_size + slot_gap) + slot_size // 2,
                first_top + row * (slot_size + slot_gap) + slot_size // 2,
                slot_size,
                slot_size,
            )
            slot.renderer.draw_layer = 110

    def restore_skill_equip_slot_positions(self):
        for slot, transform in zip(
            self.skill_equip_slots,
            self.skill_slot_default_transforms,
        ):
            slot.set_transform(*transform)
            slot.renderer.draw_layer = 0

    def get_context_popup_left(self, selected_rect, popup_width):
        panel_right = (VIRTUAL_WIDTH + self.PANEL_WIDTH) // 2
        right_side = selected_rect.right + 8
        if right_side + popup_width <= panel_right - 12:
            return right_side

        return selected_rect.left - popup_width - 8

    def change_discard_amount(self, amount):
        self.popup_interacted_this_frame = True
        item_instance = self.get_selected_item()
        if item_instance is None:
            self.close_item_popup()
            return

        self.discard_amount = max(
            1,
            min(item_instance.stack, self.discard_amount + amount),
        )

    def discard_selected_item(self):
        item_instance = self.get_selected_item()
        inventory = self.get_item_inventory()
        if item_instance is not None and inventory is not None:
            inventory.remove_amount(item_instance, self.discard_amount)

        self.close_item_popup()

    def use_selected_item(self):
        item_instance = self.get_selected_item()
        inventory = self.get_item_inventory()
        player = getattr(self.parent_scene, "player", None)
        use = getattr(getattr(item_instance, "item", None), "use", None)

        if item_instance is None or inventory is None or player is None or use is None:
            self.close_item_popup()
            return

        result = use(player)
        if result:
            inventory.remove_amount(item_instance, 1)

        self.close_item_popup()

    def equip_selected_item(self):
        item_instance = self.get_selected_item()
        dungeon_inventory = getattr(
            self.parent_scene,
            "dungeon_inventory",
            None,
        )
        player = getattr(self.parent_scene, "player", None)

        if (
            item_instance is None
            or dungeon_inventory is None
            or player is None
        ):
            self.close_item_popup()
            return

        dungeon_inventory.equip_item(item_instance, player)
        self.close_item_popup()

    def equip_item_at_index(self, item_index):
        inventory_items = self.get_inventory_items()
        if item_index >= len(inventory_items):
            return
        if not isinstance(inventory_items[item_index].item, Equip):
            return

        self.selected_item_index = item_index
        self.equip_selected_item()

    def unequip_item(self, equipment_attribute):
        dungeon_inventory = getattr(
            self.parent_scene,
            "dungeon_inventory",
            None,
        )
        player = getattr(self.parent_scene, "player", None)
        if dungeon_inventory is None or player is None:
            return

        if dungeon_inventory.unequip_item(equipment_attribute, player):
            self.close_item_popup()

    def assign_selected_item_shortcut(self):
        if self.get_selected_item() is None:
            self.close_item_popup()
            return

        self.popup_mode = "shortcut"
        self.popup_interacted_this_frame = True
        self.position_shortcut_popup()
        self.update_popup_visibility()
        self.update_slot_visibility()

    def assign_item_to_hotbar(self, key_label):
        if self.popup_mode != "shortcut":
            return

        item_instance = self.get_selected_item()
        dungeon_inventory = getattr(
            self.parent_scene,
            "dungeon_inventory",
            None,
        )
        if item_instance is not None and dungeon_inventory is not None:
            dungeon_inventory.assign_hotbar_item(key_label, item_instance)

        self.close_item_popup()

    def get_item_inventory(self):
        dungeon_inventory = getattr(self.parent_scene, "dungeon_inventory", None)
        return (
            getattr(dungeon_inventory, "item_inventory", None)
            if dungeon_inventory is not None
            else None
        )

    def get_inventory_items(self):
        return getattr(self.get_item_inventory(), "items", [])

    def get_selected_item(self):
        if self.selected_item_index is None:
            return None

        inventory_items = self.get_inventory_items()
        if self.selected_item_index >= len(inventory_items):
            return None

        return inventory_items[self.selected_item_index]

    def update_slot_visibility(self):
        equipment_visible = self.selected_tab == "장비"
        skill_visible = (
            self.selected_tab == "스킬"
            or self.popup_mode == "shortcut"
        )

        for slot in (*self.equipment_slots, *self.item_slots):
            slot.set_visible(equipment_visible)

        for slot in self.skill_equip_slots:
            slot.set_visible(skill_visible)

        for button in self.stat_tab_buttons:
            button.set_visible(self.selected_tab == "스탯")

        self.skill_node_list_view.set_visible(self.selected_tab == "영웅")

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
            item = getattr(item_instance, "item", None)
            slot.set_item(
                self.get_item_instance_text(item_instance),
                item,
            )

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
            max_stack = getattr(item_instance, "max_stack", 1)
            stack_text = (
                str(stack)
                if item_instance is not None and max_stack != 1
                else ""
            )
            item = getattr(item_instance, "item", None)
            slot.set_text(item_text, stack_text, item)

        dungeon_inventory = getattr(
            self.parent_scene,
            "dungeon_inventory",
            None,
        )
        hotbar_skills = getattr(self.parent_scene, "hotbar_skills", {})
        for slot, key_label in zip(
            self.skill_equip_slots,
            self.SKILL_SLOT_LABELS,
        ):
            item_instance = (
                dungeon_inventory.get_hotbar_item(key_label)
                if dungeon_inventory is not None
                else None
            )
            if item_instance is not None:
                slot.set_item(item_instance)
                continue

            skill = hotbar_skills.get(key_label)
            slot.set_skill_text(getattr(skill, "name", ""))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[TAB]["keydown"]:
            self.exit_scene()
            return
        if game_events[ESCAPE]["keydown"]:
            if self.popup_mode is not None:
                self.close_item_popup()
            else:
                self.exit_scene()
            return

        if self.popup_mode is not None and game_events[MOUSE_LEFT]["keydown"]:
            if self.popup_interacted_this_frame:
                self.popup_interacted_this_frame = False
            elif (
                mouse_position is None
                or self.popup_rect is None
                or not self.popup_rect.collidepoint(mouse_position)
            ):
                self.close_item_popup()
        else:
            self.popup_interacted_this_frame = False

        self.refresh_inventory_texts()
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def draw(self):
        self.refresh_inventory_texts()
        super().draw()

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
