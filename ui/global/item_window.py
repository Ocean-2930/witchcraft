import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer
from ui.ui import UIElement


class ItemWindowRenderer(Renderer):
    draw_layer = 200

    def __init__(self, scene, pos_x, pos_y, width, height, window):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.window = window

    def draw(self, screen):
        item_instance = self.window.get_item_instance()
        if not self.window.visible or item_instance is None:
            return

        pygame.draw.rect(screen, (12, 15, 19), self.rect, border_radius=6)
        pygame.draw.rect(
            screen, (115, 129, 142), self.rect, 2, border_radius=6
        )
        item = item_instance.item
        stack_text = (
            f"  ×{item_instance.stack}" if item_instance.stack > 1 else ""
        )
        title = self.window.title_font.render(
            f"{item.get_name()}{stack_text}",
            True,
            (240, 244, 247),
        )
        screen.blit(title, (self.rect.left + 12, self.rect.top + 10))
        line_y = self.rect.top + 39
        pygame.draw.line(
            screen,
            (79, 91, 102),
            (self.rect.left + 10, line_y),
            (self.rect.right - 10, line_y),
        )
        detail_rows = item.get_detail_rows()
        content_y = line_y + 9
        if item.get_description():
            content_y = self.window.draw_description(
                screen,
                item.get_description(),
                content_y,
            ) + 8
        if detail_rows:
            self.window.draw_detail_rows(screen, detail_rows, content_y)
        self.window.draw_flavor_text(screen, item.get_flavor_text())


class ItemWindow(UIElement):
    def __init__(
        self,
        scene,
        item_instance_getter,
        width=280,
        height=142,
    ):
        self.item_instance_getter = item_instance_getter
        self.visible = False
        self.title_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.description_font = pygame.font.SysFont("malgungothic", 14)
        self.detail_font = pygame.font.SysFont("malgungothic", 14)
        self.flavor_font = pygame.font.SysFont(
            "malgungothic", 13, italic=True
        )
        renderer = ItemWindowRenderer(scene, 0, 0, width, height, self)
        super().__init__(scene, renderer=renderer, background=False)

    def get_item_instance(self):
        return self.item_instance_getter()

    def show_at(self, mouse_position):
        if mouse_position is None or self.get_item_instance() is None:
            self.hide()
            return
        item_instance = self.get_item_instance()
        detail_rows = item_instance.item.get_detail_rows()
        height = (
            150
            if not detail_rows
            else 113 + len(detail_rows) * 24
        )
        self.set_transform(width=self.rect.width, height=height)
        left = min(mouse_position[0] + 16, VIRTUAL_WIDTH - self.rect.width - 8)
        top = min(mouse_position[1] + 16, VIRTUAL_HEIGHT - self.rect.height - 8)
        self.set_transform(
            max(8, left) + self.rect.width // 2,
            max(8, top) + self.rect.height // 2,
        )
        self.visible = True

    def hide(self):
        self.visible = False

    def pos_check(self, mouse_pos):
        return False

    def draw_description(self, screen, text, start_y):
        color = (184, 195, 204)
        available_width = self.rect.width - 24
        lines = []
        current = ""
        for character in text:
            candidate = current + character
            if (
                current
                and self.description_font.size(candidate)[0] > available_width
            ):
                lines.append(current)
                current = character
            else:
                current = candidate
        if current:
            lines.append(current)

        line_height = self.description_font.get_linesize()
        maximum_lines = 2
        visible_lines = lines[:maximum_lines]
        if len(lines) > maximum_lines and visible_lines:
            last = visible_lines[-1]
            while (
                last
                and self.description_font.size(last + "…")[0]
                > available_width
            ):
                last = last[:-1]
            visible_lines[-1] = last + "…"
        for index, line in enumerate(visible_lines):
            surface = self.description_font.render(line, True, color)
            screen.blit(
                surface,
                (self.rect.left + 12, start_y + index * line_height),
            )
        return start_y + len(visible_lines) * line_height

    def draw_detail_rows(self, screen, detail_rows, start_y):
        level_x = self.rect.left + 190
        for index, (name, level_text) in enumerate(detail_rows):
            row_y = start_y + index * 24
            name_surface = self.detail_font.render(
                name,
                True,
                (210, 220, 228),
            )
            level_surface = self.detail_font.render(
                level_text,
                True,
                (170, 193, 211),
            )
            screen.blit(name_surface, (self.rect.left + 12, row_y))
            screen.blit(level_surface, (level_x, row_y))

    def draw_flavor_text(self, screen, flavor_text):
        if not flavor_text:
            return
        separator_y = self.rect.bottom - 48
        pygame.draw.line(
            screen,
            (60, 70, 79),
            (self.rect.left + 10, separator_y),
            (self.rect.right - 10, separator_y),
        )
        flavor_surface = self.flavor_font.render(
            flavor_text,
            True,
            (137, 149, 159),
        )
        screen.blit(
            flavor_surface,
            (self.rect.left + 12, separator_y + 12),
        )

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
