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
        if self.window.scrollable:
            self.window.draw_scrollable_contents(screen)
            return
        detail_rows = item_instance.get_detail_rows()
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
        detail_colors_getter=None,
        scrollable=False,
    ):
        self.item_instance_getter = item_instance_getter
        self.detail_colors_getter = detail_colors_getter
        self.scrollable = scrollable
        self.scroll_offset = 0
        self.max_scroll = 0
        self._scroll_item = None
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
        detail_rows = item_instance.get_detail_rows()
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
        return self.scrollable and self.visible and super().pos_check(mouse_pos)

    @staticmethod
    def wrap_lines(text, font, width):
        lines = []
        for paragraph in text.split("\n"):
            current = ""
            for character in paragraph:
                if current and font.size(current + character)[0] > width:
                    lines.append(current)
                    current = ""
                current += character
            lines.append(current)
        return lines

    def scroll_layout(self):
        item_instance = self.get_item_instance()
        if item_instance is not self._scroll_item:
            self.scroll_offset = 0
            self._scroll_item = item_instance
        viewport = pygame.Rect(self.rect.left + 12, self.rect.top + 48,
                               self.rect.width - 32, self.rect.height - 60)
        entries = []
        y = 0
        if item_instance is not None:
            item = item_instance.item
            for text, font, color in (
                (item.get_description(), self.description_font, (184, 195, 204)),
            ):
                if text:
                    for line in self.wrap_lines(text, font, viewport.width):
                        entries.append((0, y, line, font, color))
                        y += font.get_linesize()
                    y += 8
            colors = self.detail_colors_getter() if self.detail_colors_getter else []
            level_x = min(178, viewport.width - 70)
            for index, (name, level) in enumerate(item_instance.get_detail_rows()):
                color = colors[index] if index < len(colors) else (210, 220, 228)
                lines = self.wrap_lines(name, self.detail_font, level_x - 10)
                entries.append((level_x, y, level, self.detail_font, color))
                for line in lines:
                    entries.append((0, y, line, self.detail_font, color))
                    y += max(24, self.detail_font.get_linesize())
            flavor = item.get_flavor_text()
            if flavor:
                y += 12
                for line in self.wrap_lines(flavor, self.flavor_font, viewport.width):
                    entries.append((0, y, line, self.flavor_font, (137, 149, 159)))
                    y += self.flavor_font.get_linesize()
        self.max_scroll = max(0, y - viewport.height)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
        return viewport, entries, y

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        if self.scrollable and self.visible:
            self.scroll_layout()
            self.scroll_offset = max(0, min(self.max_scroll,
                                           self.scroll_offset - wheel_move * 32))

    def draw_scrollable_contents(self, screen):
        viewport, entries, content_height = self.scroll_layout()
        previous_clip = screen.get_clip()
        screen.set_clip(previous_clip.clip(viewport))
        try:
            for x, y, text, font, color in entries:
                screen.blit(font.render(text, True, color),
                            (viewport.left + x, viewport.top + y - self.scroll_offset))
        finally:
            screen.set_clip(previous_clip)
        if self.max_scroll:
            track = pygame.Rect(self.rect.right - 10, viewport.top, 4, viewport.height)
            thumb_height = max(18, int(track.height * viewport.height / content_height))
            thumb = pygame.Rect(track.left,
                                track.top + int((track.height - thumb_height)
                                                * self.scroll_offset / self.max_scroll),
                                track.width, thumb_height)
            pygame.draw.rect(screen, (45, 55, 66), track, border_radius=2)
            pygame.draw.rect(screen, (145, 177, 202), thumb, border_radius=2)

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
        colors = self.detail_colors_getter() if self.detail_colors_getter else []
        level_x = self.rect.left + 190
        for index, (name, level_text) in enumerate(detail_rows):
            row_y = start_y + index * 24
            name_surface = self.detail_font.render(
                name,
                True,
                colors[index] if index < len(colors) else (210, 220, 228),
            )
            level_surface = self.detail_font.render(
                level_text,
                True,
                colors[index] if index < len(colors) else (170, 193, 211),
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
