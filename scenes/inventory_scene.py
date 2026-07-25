import pygame

from .scene import Scene
from settings import ESCAPE, TAB, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import InventoryTabButton


class InventoryScene(Scene):
    TAB_LABELS = ("장비", "스킬", "영웅", "스탯")
    EQUIPMENT_SLOTS = (
        ("weapon", "무기"),
        ("sub_weapon", "보조 무기"),
        ("armor", "방어구"),
        ("accessory_1", "장신구 1"),
        ("accessory_2", "장신구 2"),
    )
    PANEL_WIDTH = 960
    PANEL_HEIGHT = 600

    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 24, bold=True)
        self.section_font = pygame.font.SysFont("malgungothic", 22, bold=True)
        self.slot_label_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.item_font = pygame.font.SysFont("malgungothic", 14)
        self.selected_tab = self.TAB_LABELS[0]
        self.tab_buttons = []

        tab_width = 180
        tab_height = 58
        tab_gap = 12
        total_tab_width = tab_width * len(self.TAB_LABELS) + tab_gap * (len(self.TAB_LABELS) - 1)
        first_tab_x = VIRTUAL_WIDTH // 2 - total_tab_width // 2 + tab_width // 2
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

    def select_tab(self, label):
        self.selected_tab = label

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[TAB]["keydown"] or game_events[ESCAPE]["keydown"]:
            self.exit_scene()
            return

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        screen = self.game.virtual_screen

        dim_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((4, 7, 11, 110))
        screen.blit(dim_surface, (0, 0))

        panel_surface = pygame.Surface(
            (self.PANEL_WIDTH, self.PANEL_HEIGHT),
            pygame.SRCALPHA,
        )
        panel_surface.fill((22, 28, 36, 225))
        panel_rect = panel_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))
        screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(screen, (132, 148, 164), panel_rect, width=2, border_radius=8)

        divider_y = panel_rect.top + 104
        pygame.draw.line(
            screen,
            (105, 119, 133),
            (panel_rect.left + 30, divider_y),
            (panel_rect.right - 30, divider_y),
            width=2,
        )

        if self.selected_tab == "장비":
            self.draw_equipment_tab(screen, panel_rect)

        super().scene_draw()

    def draw_equipment_tab(self, screen, panel_rect):
        dungeon_inventory = getattr(self.parent_scene, "dungeon_inventory", None)

        equipment_title = self.section_font.render("장비", True, (232, 238, 243))
        screen.blit(equipment_title, (panel_rect.left + 46, panel_rect.top + 122))

        slot_size = 96
        slot_gap = 22
        total_width = slot_size * len(self.EQUIPMENT_SLOTS) + slot_gap * (
            len(self.EQUIPMENT_SLOTS) - 1
        )
        first_slot_x = panel_rect.centerx - total_width // 2
        equipment_y = panel_rect.top + 158

        for index, (attribute_name, label) in enumerate(self.EQUIPMENT_SLOTS):
            slot_rect = pygame.Rect(
                first_slot_x + index * (slot_size + slot_gap),
                equipment_y,
                slot_size,
                slot_size,
            )
            item_instance = (
                getattr(dungeon_inventory, attribute_name, None)
                if dungeon_inventory is not None
                else None
            )
            self.draw_item_slot(screen, slot_rect, item_instance, label)

        inventory = (
            getattr(dungeon_inventory, "item_inventory", None)
            if dungeon_inventory is not None
            else None
        )
        inventory_items = getattr(inventory, "items", [])
        inventory_capacity = getattr(inventory, "capacity", 20)

        inventory_title = self.section_font.render(
            f"인벤토리  {len(inventory_items)} / {inventory_capacity}",
            True,
            (232, 238, 243),
        )
        screen.blit(inventory_title, (panel_rect.left + 46, panel_rect.top + 274))

        columns = 10
        inventory_slot_size = 72
        inventory_gap = 10
        inventory_width = (
            inventory_slot_size * columns + inventory_gap * (columns - 1)
        )
        inventory_x = panel_rect.centerx - inventory_width // 2
        inventory_y = panel_rect.top + 316

        for index in range(inventory_capacity):
            row, column = divmod(index, columns)
            slot_rect = pygame.Rect(
                inventory_x + column * (inventory_slot_size + inventory_gap),
                inventory_y + row * (inventory_slot_size + inventory_gap),
                inventory_slot_size,
                inventory_slot_size,
            )
            item_instance = (
                inventory_items[index] if index < len(inventory_items) else None
            )
            self.draw_item_slot(screen, slot_rect, item_instance)

    def draw_item_slot(self, screen, slot_rect, item_instance, slot_label=None):
        pygame.draw.rect(screen, (31, 39, 49), slot_rect, border_radius=5)
        pygame.draw.rect(
            screen,
            (103, 119, 135),
            slot_rect,
            width=2,
            border_radius=5,
        )

        if slot_label is not None:
            label_surface = self.slot_label_font.render(
                slot_label,
                True,
                (182, 195, 207),
            )
            label_rect = label_surface.get_rect(
                center=(slot_rect.centerx, slot_rect.top + 17)
            )
            screen.blit(label_surface, label_rect)

        if item_instance is None:
            return

        item = getattr(item_instance, "item", None)
        if item is None:
            return

        item_name = self.get_item_display_name(item)
        name_surface = self.item_font.render(item_name, True, (238, 241, 244))
        name_rect = name_surface.get_rect(center=slot_rect.center)
        screen.blit(name_surface, name_rect)

        stack = getattr(item_instance, "stack", 1)
        if stack > 1:
            stack_surface = self.item_font.render(
                str(stack),
                True,
                (246, 224, 148),
            )
            stack_rect = stack_surface.get_rect(
                bottomright=(slot_rect.right - 7, slot_rect.bottom - 5)
            )
            screen.blit(stack_surface, stack_rect)

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
