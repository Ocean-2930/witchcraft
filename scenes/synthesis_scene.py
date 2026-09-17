import pygame

from items import EquipmentInstance
from settings import ESCAPE, TAB, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import InventoryTabButton, ItemSlot, SynthesisPanel
from .scene import Scene


class SynthesisScene(Scene):
    """인벤토리 위에 열리는 독립적인 장비 합성창."""

    def __init__(self, game, inventory, main_item):
        self.inventory = inventory
        self.main_item = main_item
        self.material_item = None
        self.result_item = main_item
        self.result_kinds = []
        self.selection_message = ""
        super().__init__(game)

    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 20, bold=True)
        self.slot_label_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.item_font = pygame.font.SysFont("malgungothic", 14)
        panel_rect = pygame.Rect(0, 0, 960, 600)
        panel_rect.center = (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2)
        self.panel = SynthesisPanel(
            self, panel_rect, lambda: self.main_item,
            lambda: self.material_item, self.clear_material,
            lambda: self.result_item, self.get_result_colors,
            lambda: self.selection_message,
        )
        self.panel.set_visible(True)
        self.back_button = InventoryTabButton(
            self, "돌아가기", panel_rect.right - 110, panel_rect.top + 56,
            140, 44, self.exit_scene, is_selected=lambda: False,
        )
        self.item_slots = []
        for index in range(20):
            row, column = divmod(index, 10)
            self.item_slots.append(ItemSlot(
                self, "", "", panel_rect.left + 111 + column * 82,
                panel_rect.top + 446 + row * 82, 72, 72,
                on_click=lambda index=index: self.select_material(index),
            ))
        self.refresh_slots()

    def select_material(self, index):
        if not 0 <= index < len(self.inventory.items):
            return
        item = self.inventory.items[index]
        if item is self.material_item:
            self.clear_material()
            return
        if not isinstance(self.main_item, EquipmentInstance):
            return
        try:
            result, kinds = self.main_item.synthesis_preview(item)
        except ValueError as error:
            self.selection_message = str(error)
            return
        self.material_item = item
        self.result_item = result
        self.result_kinds = kinds
        self.selection_message = ""

    def get_result_colors(self):
        palette = {
            "upgraded": (100, 230, 140),
            "lower": (255, 110, 110),
            "original": (240, 244, 247),
            "added": (255, 220, 90),
        }
        return [palette[kind] for kind in self.result_kinds]

    def clear_material(self):
        self.material_item = None
        self.result_item = self.main_item
        self.result_kinds = []
        self.selection_message = ""

    def refresh_slots(self):
        for index, slot in enumerate(self.item_slots):
            item = self.inventory.items[index] if index < len(self.inventory.items) else None
            stack_text = str(item.stack) if item is not None and item.max_stack != 1 else ""
            slot.set_text("", stack_text, item)
            slot.dimmed = item is self.main_item
            slot.selected = item is not None and item is self.material_item

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"] or game_events[TAB]["keydown"]:
            self.exit_scene()
            return
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def draw(self):
        self.refresh_slots()
        super().draw()
