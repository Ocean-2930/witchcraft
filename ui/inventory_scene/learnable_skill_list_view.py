import pygame
from importlib import import_module

from ui.renderer import Renderer
from ui.ui import UIElement
from .skill_invest_button import SkillInvestButton

SkillCard = import_module("ui.global").SkillCard


class LearnableSkillListViewRenderer(Renderer):
    draw_layer = -5

    def __init__(self, scene, pos_x, pos_y, width, height, view):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.view = view

    def draw(self, screen):
        if not self.view.visible:
            return
        previous_clip = screen.get_clip()
        screen.set_clip(self.rect)
        self.view.draw_tier_boxes(screen)
        screen.set_clip(previous_clip)


class LearnableSkillListView(UIElement):
    TIER_WIDTH = 207
    TIER_GAP = 18
    HEADER_HEIGHT = 64
    HEADER_BODY_GAP = 8
    CARD_HEIGHT = 68
    CARD_GAP = 12
    BOTTOM_SCROLL_HEIGHT = 28
    SCROLL_STEP = 54

    def __init__(self, scene, pos_x, pos_y, width, height, inventory_getter):
        self.visible = False
        self.inventory_getter = inventory_getter
        self.horizontal_offset = 0
        self.vertical_offsets = {}
        self.skill_widgets = {}
        renderer = LearnableSkillListViewRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer, background=False)

    def set_visible(self, visible):
        self.visible = visible
        for card, button in self.skill_widgets.values():
            card.set_visible(visible)
            button.set_visible(visible)
        if not visible and self.scene.ui_focus is self:
            self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        return self.visible and super().pos_check(mouse_pos)

    def get_inventory(self):
        return self.inventory_getter()

    def get_tiers(self):
        inventory = self.get_inventory()
        if inventory is None:
            return []
        populated = sorted(
            set(inventory.tier_skill_points)
            | {learnable_skill.tier for learnable_skill in inventory.learnable_skills}
        )
        return list(range(1, populated[-1] + 1)) if populated else []

    def get_header_rect(self, tier_index):
        left = self.get_tier_left(tier_index)
        return pygame.Rect(left, self.rect.top, self.TIER_WIDTH, self.HEADER_HEIGHT)

    def get_body_rect(self, tier_index):
        left = self.get_tier_left(tier_index)
        top = self.rect.top + self.HEADER_HEIGHT + self.HEADER_BODY_GAP
        return pygame.Rect(
            left,
            top,
            self.TIER_WIDTH,
            self.rect.bottom - self.BOTTOM_SCROLL_HEIGHT - top,
        )

    def get_tier_left(self, tier_index):
        return (
            self.rect.left + tier_index * (self.TIER_WIDTH + self.TIER_GAP)
            - self.horizontal_offset
        )

    def sync_widgets(self):
        inventory = self.get_inventory()
        learnable_skills = [] if inventory is None else inventory.learnable_skills
        active_ids = {id(learnable_skill) for learnable_skill in learnable_skills}
        for skill_id in tuple(self.skill_widgets):
            if skill_id not in active_ids:
                card, button = self.skill_widgets.pop(skill_id)
                card.destroy()
                button.destroy()

        for learnable_skill in learnable_skills:
            if id(learnable_skill) in self.skill_widgets:
                continue
            card = SkillCard(
                self.scene,
                learnable_skill.skill,
                0,
                0,
                self.TIER_WIDTH - 20,
                self.CARD_HEIGHT,
                clip_rect_getter=lambda owned_skill=learnable_skill: self.get_skill_clip_rect(owned_skill),
                on_icon_hover=self.on_child_hover,
                max_level=learnable_skill.max_level,
            )
            button = SkillInvestButton(
                self.scene,
                learnable_skill,
                0,
                0,
                self.inventory_getter,
                lambda owned_skill=learnable_skill: self.get_skill_clip_rect(owned_skill),
            )
            card.set_visible(self.visible)
            button.set_visible(self.visible)
            self.skill_widgets[id(learnable_skill)] = (card, button)
        self.position_widgets()

    def get_skill_clip_rect(self, learnable_skill):
        tiers = self.get_tiers()
        if learnable_skill.tier not in tiers:
            return pygame.Rect(0, 0, 0, 0)
        return self.get_body_rect(tiers.index(learnable_skill.tier)).clip(self.rect)

    def position_widgets(self):
        inventory = self.get_inventory()
        if inventory is None:
            return
        tiers = self.get_tiers()
        for tier_index, tier in enumerate(tiers):
            body_rect = self.get_body_rect(tier_index)
            card_y = body_rect.top + 10 - self.vertical_offsets.get(tier, 0)
            for learnable_skill in (
                skill for skill in inventory.learnable_skills
                if skill.tier == tier
            ):
                card, button = self.skill_widgets[id(learnable_skill)]
                card.set_transform(body_rect.centerx, card_y + self.CARD_HEIGHT // 2)
                button.set_transform(
                    card.rect.right - 21,
                    card.level_center_y,
                )
                card_y += self.CARD_HEIGHT + self.CARD_GAP

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.sync_widgets()

    def on_child_hover(self, mouse_position, wheel_move):
        if wheel_move:
            self.apply_scroll(mouse_position, wheel_move)

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        if wheel_move:
            self.apply_scroll(mouse_position, wheel_move)

    def apply_scroll(self, mouse_position, wheel_move):
        tiers = self.get_tiers()
        inventory = self.get_inventory()
        hovered_index = next(
            (
                index for index in range(len(tiers))
                if self.get_body_rect(index).collidepoint(mouse_position)
            ),
            None,
        )
        if hovered_index is not None and inventory is not None:
            tier = tiers[hovered_index]
            count = sum(
                learnable_skill.tier == tier
                for learnable_skill in inventory.learnable_skills
            )
            content_height = 20 + count * self.CARD_HEIGHT + max(0, count - 1) * self.CARD_GAP
            maximum = max(0, content_height - self.get_body_rect(hovered_index).height)
            if maximum > 0:
                current = self.vertical_offsets.get(tier, 0)
                self.vertical_offsets[tier] = max(
                    0, min(maximum, current - wheel_move * self.SCROLL_STEP)
                )
                self.position_widgets()
                return

        content_width = len(tiers) * (self.TIER_WIDTH + self.TIER_GAP)
        maximum = max(0, content_width - self.rect.width - self.TIER_GAP)
        self.horizontal_offset = max(
            0,
            min(maximum, self.horizontal_offset - wheel_move * self.SCROLL_STEP),
        )
        self.position_widgets()

    def draw_tier_boxes(self, screen):
        self.sync_widgets()
        inventory = self.get_inventory()
        if inventory is None:
            return
        tiers = self.get_tiers()
        for index, tier in enumerate(tiers):
            header_rect = self.get_header_rect(index)
            body_rect = self.get_body_rect(index)
            if not header_rect.colliderect(self.rect):
                continue
            pygame.draw.rect(screen, (35, 45, 56), header_rect, border_radius=7)
            pygame.draw.rect(screen, (111, 132, 151), header_rect, 2, border_radius=7)
            pygame.draw.rect(screen, (25, 32, 41), body_rect, border_radius=7)
            pygame.draw.rect(screen, (75, 89, 103), body_rect, 1, border_radius=7)
            title = self.scene.section_font.render(f"Tier {tier}", True, (235, 241, 246))
            points = inventory.tier_skill_points.get(tier, 0)
            point_text = self.scene.item_font.render(
                f"Skill Point  {points}", True, (153, 205, 245)
            )
            screen.blit(title, (header_rect.left + 14, header_rect.top + 7))
            screen.blit(point_text, (header_rect.left + 14, header_rect.top + 40))

        content_width = len(tiers) * (self.TIER_WIDTH + self.TIER_GAP)
        if content_width > self.rect.width:
            ratio = self.rect.width / content_width
            bar_width = max(40, round(self.rect.width * ratio))
            maximum = content_width - self.rect.width
            travel = self.rect.width - bar_width
            bar_x = self.rect.left + round(travel * self.horizontal_offset / maximum)
            pygame.draw.rect(
                screen,
                (126, 151, 173),
                (bar_x, self.rect.bottom - 5, bar_width, 5),
                border_radius=3,
            )

    def destroy(self):
        for card, button in tuple(self.skill_widgets.values()):
            card.destroy()
            button.destroy()
        self.skill_widgets.clear()
        super().destroy()
        self.renderer.destroy()
