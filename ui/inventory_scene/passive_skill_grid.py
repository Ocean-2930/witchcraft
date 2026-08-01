from importlib import import_module

import pygame

from ui.renderer import Renderer
from ui.ui import UIElement

SkillCard = import_module("ui.global").SkillCard


class PassiveSkillGridRenderer(Renderer):
    draw_layer = -5

    def __init__(self, scene, pos_x, pos_y, width, height, grid):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.grid = grid

    def draw(self, screen):
        if not self.grid.visible:
            return
        pygame.draw.rect(screen, (25, 32, 41), self.rect, border_radius=7)
        pygame.draw.rect(screen, (87, 102, 116), self.rect, 2, border_radius=7)
        if not self.grid.skill_widgets:
            empty = self.scene.item_font.render(
                "적용 중인 패시브 스킬이 없습니다.",
                True,
                (127, 140, 151),
            )
            screen.blit(empty, empty.get_rect(center=self.rect.center))
        self.grid.draw_scrollbar(screen)


class PassiveSkillGrid(UIElement):
    COLUMNS = 3
    CARD_WIDTH = 228
    CARD_HEIGHT = 68
    COLUMN_GAP = 18
    ROW_GAP = 14
    PADDING = 16
    SCROLL_STEP = 54

    def __init__(self, scene, pos_x, pos_y, width, height, inventory_getter):
        self.visible = False
        self.inventory_getter = inventory_getter
        self.scroll_offset = 0
        self.skill_widgets = {}
        renderer = PassiveSkillGridRenderer(
            scene,
            pos_x,
            pos_y,
            width,
            height,
            self,
        )
        super().__init__(scene, renderer=renderer, background=False)

    def set_visible(self, visible):
        self.visible = visible
        for card in self.skill_widgets.values():
            card.set_visible(visible)
        if not visible and self.scene.ui_focus is self:
            self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def get_inventory(self):
        return self.inventory_getter()

    def get_clip_rect(self):
        return self.rect.inflate(-self.PADDING, -self.PADDING)

    def get_passive_skills(self):
        inventory = self.get_inventory()
        return [] if inventory is None else inventory.passive_skills()

    def get_display_max_level(self, skill_instance):
        inventory = self.get_inventory()
        if inventory is None:
            return skill_instance.max_level
        matching = next(
            (
                learnable_skill
                for learnable_skill in inventory.learnable_skills
                if learnable_skill.skill.skill.skill_code
                == skill_instance.skill.skill_code
            ),
            None,
        )
        if matching is None:
            return skill_instance.max_level
        return max(skill_instance.level, matching.max_level)

    def sync_widgets(self):
        passive_skills = self.get_passive_skills()
        active_codes = {
            skill_instance.skill.skill_code for skill_instance in passive_skills
        }
        for skill_code in tuple(self.skill_widgets):
            if skill_code not in active_codes:
                self.skill_widgets.pop(skill_code).destroy()

        for skill_instance in passive_skills:
            skill_code = skill_instance.skill.skill_code
            max_level = self.get_display_max_level(skill_instance)
            card = self.skill_widgets.get(skill_code)
            if card is None:
                card = SkillCard(
                    self.scene,
                    skill_instance,
                    0,
                    0,
                    self.CARD_WIDTH,
                    self.CARD_HEIGHT,
                    clip_rect_getter=self.get_clip_rect,
                    on_icon_hover=self.on_child_hover,
                    max_level=max_level,
                )
                card.set_visible(self.visible)
                self.skill_widgets[skill_code] = card
            else:
                card.skill_instance = skill_instance
                card.max_level = max_level
                card.info_window.skill_instance = skill_instance
                card.info_window.max_level = max_level
        self.clamp_scroll()
        self.position_widgets(passive_skills)

    def get_content_height(self, skill_count=None):
        if skill_count is None:
            skill_count = len(self.skill_widgets)
        rows = (skill_count + self.COLUMNS - 1) // self.COLUMNS
        return (
            rows * self.CARD_HEIGHT
            + max(0, rows - 1) * self.ROW_GAP
            + self.PADDING * 2
        )

    def get_max_scroll(self):
        return max(0, self.get_content_height() - self.rect.height)

    def clamp_scroll(self):
        self.scroll_offset = max(0, min(self.get_max_scroll(), self.scroll_offset))

    def position_widgets(self, passive_skills=None):
        passive_skills = passive_skills or self.get_passive_skills()
        total_width = (
            self.COLUMNS * self.CARD_WIDTH
            + (self.COLUMNS - 1) * self.COLUMN_GAP
        )
        first_left = self.rect.centerx - total_width // 2
        first_top = self.rect.top + self.PADDING - self.scroll_offset
        for index, skill_instance in enumerate(passive_skills):
            row, column = divmod(index, self.COLUMNS)
            card = self.skill_widgets[skill_instance.skill.skill_code]
            card.set_transform(
                first_left + column * (self.CARD_WIDTH + self.COLUMN_GAP)
                + self.CARD_WIDTH // 2,
                first_top + row * (self.CARD_HEIGHT + self.ROW_GAP)
                + self.CARD_HEIGHT // 2,
            )

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.sync_widgets()

    def on_child_hover(self, mouse_position, wheel_move):
        if wheel_move:
            self.apply_scroll(wheel_move)

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        if wheel_move:
            self.apply_scroll(wheel_move)

    def apply_scroll(self, wheel_move):
        self.scroll_offset -= wheel_move * self.SCROLL_STEP
        self.clamp_scroll()
        self.position_widgets()

    def draw_scrollbar(self, screen):
        maximum = self.get_max_scroll()
        if maximum <= 0:
            return
        track = pygame.Rect(
            self.rect.right - 8,
            self.rect.top + self.PADDING,
            4,
            self.rect.height - self.PADDING * 2,
        )
        ratio = self.rect.height / self.get_content_height()
        bar_height = max(36, round(track.height * ratio))
        travel = track.height - bar_height
        bar_y = track.top + round(travel * self.scroll_offset / maximum)
        pygame.draw.rect(
            screen,
            (126, 151, 173),
            (track.left, bar_y, track.width, bar_height),
            border_radius=2,
        )

    def destroy(self):
        for card in tuple(self.skill_widgets.values()):
            card.destroy()
        self.skill_widgets.clear()
        super().destroy()
        self.renderer.destroy()
