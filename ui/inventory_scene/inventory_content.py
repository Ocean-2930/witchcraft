import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class InventoryContentRenderer(Renderer):
    draw_layer = -10

    def __init__(self, scene, panel_width, panel_height):
        self.panel_width = panel_width
        self.panel_height = panel_height
        super().__init__(
            scene,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            panel_width,
            panel_height,
        )

    def draw(self, screen):
        panel_rect = self.rect

        if self.scene.selected_tab == "장비":
            self.draw_equipment_titles(screen, panel_rect)
        elif self.scene.selected_tab == "스킬":
            self.draw_section_title(screen, panel_rect, "장착 스킬")
        elif self.scene.selected_tab == "영웅":
            self.draw_section_title(screen, panel_rect, "스킬 목록")
        elif self.scene.selected_tab == "스탯":
            self.draw_stat_tab(screen, panel_rect)

    def draw_equipment_titles(self, screen, panel_rect):
        self.draw_section_title(screen, panel_rect, "장비")

        inventory = self.scene.get_item_inventory()
        item_count = len(getattr(inventory, "items", []))
        capacity = getattr(
            inventory,
            "capacity",
            self.scene.ITEM_SLOT_COUNT,
        )
        title_surface = self.scene.section_font.render(
            f"인벤토리  {item_count} / {capacity}",
            True,
            (232, 238, 243),
        )
        screen.blit(
            title_surface,
            (panel_rect.left + 46, panel_rect.top + 274),
        )

    def draw_section_title(self, screen, panel_rect, text):
        title_surface = self.scene.section_font.render(
            text,
            True,
            (232, 238, 243),
        )
        screen.blit(
            title_surface,
            (panel_rect.left + 46, panel_rect.top + 112),
        )

    def draw_stat_tab(self, screen, panel_rect):
        if self.scene.selected_stat_tab != "플레이어":
            return

        dungeon_inventory = getattr(
            self.scene.parent_scene,
            "dungeon_inventory",
            None,
        )
        if dungeon_inventory is None:
            return

        try:
            calculated_stat = dungeon_inventory.get_stat()
        except ValueError:
            return

        column_gap = 22
        content_left = panel_rect.left + 46
        content_right = panel_rect.right - 46
        column_width = (
            content_right
            - content_left
            - column_gap * (len(self.scene.STAT_GROUPS) - 1)
        ) // len(self.scene.STAT_GROUPS)
        column_top = panel_rect.top + 178
        column_height = panel_rect.bottom - column_top - 38

        for index, (group_title, stat_rows) in enumerate(
            self.scene.STAT_GROUPS
        ):
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

        group_surface = self.scene.slot_label_font.render(
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
        for attribute_name, label, is_percentage in stat_rows:
            value = getattr(calculated_stat, attribute_name, 0)
            value_text = self.format_stat_value(value, is_percentage)

            label_surface = self.scene.item_font.render(
                label,
                True,
                (174, 187, 199),
            )
            value_surface = self.scene.slot_label_font.render(
                value_text,
                True,
                (239, 243, 246),
            )
            screen.blit(label_surface, (column_rect.left + 18, row_y))
            screen.blit(
                value_surface,
                value_surface.get_rect(
                    topright=(column_rect.right - 18, row_y - 2)
                ),
            )
            row_y += 43

    @staticmethod
    def format_stat_value(value, is_percentage):
        if isinstance(value, float):
            value_text = f"{value:.2f}".rstrip("0").rstrip(".")
        else:
            value_text = str(value)

        return f"{value_text}%" if is_percentage else value_text
