import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class SkillInvestButtonRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, size, button):
        super().__init__(scene, pos_x, pos_y, size, size)
        self.button = button

    def draw(self, screen):
        if not self.button.visible or not self.button.is_in_clip():
            return
        previous_clip = screen.get_clip()
        screen.set_clip(previous_clip.clip(self.button.get_clip_rect()))
        pygame.draw.rect(
            screen,
            (61, 111, 145) if self.button.can_invest() else (55, 62, 69),
            self.rect,
            border_radius=4,
        )
        center_x, center_y = self.rect.center
        plus_color = (242, 247, 250)
        pygame.draw.line(
            screen,
            plus_color,
            (center_x - 5, center_y),
            (center_x + 5, center_y),
            width=2,
        )
        pygame.draw.line(
            screen,
            plus_color,
            (center_x, center_y - 5),
            (center_x, center_y + 5),
            width=2,
        )
        if self.button.is_hovered and self.button.can_invest():
            pygame.draw.rect(screen, (205, 230, 245), self.rect, 2, border_radius=4)
        screen.set_clip(previous_clip)


class SkillInvestButton(UIElement):
    def __init__(self, scene, learnable_skill, pos_x, pos_y, inventory_getter, clip_rect_getter):
        self.learnable_skill = learnable_skill
        self.inventory_getter = inventory_getter
        self.clip_rect_getter = clip_rect_getter
        self.visible = True
        self.is_hovered = False
        renderer = SkillInvestButtonRenderer(scene, pos_x, pos_y, 20, self)
        super().__init__(scene, renderer=renderer, background=False)

    def get_clip_rect(self):
        return self.clip_rect_getter()

    def is_in_clip(self):
        return self.rect.colliderect(self.get_clip_rect())

    def can_invest(self):
        inventory = self.inventory_getter()
        return (
            inventory is not None
            and self.learnable_skill.skill.level < self.learnable_skill.max_level
            and inventory.tier_skill_points.get(self.learnable_skill.tier, 0) > 0
        )

    def set_visible(self, visible):
        self.visible = visible

    def pos_check(self, mouse_pos):
        return (
            self.visible
            and self.is_in_clip()
            and self.get_clip_rect().collidepoint(mouse_pos)
            and super().pos_check(mouse_pos)
        )

    def on_left_click(self):
        inventory = self.inventory_getter()
        if inventory is not None:
            inventory.invest_skill(self.learnable_skill)

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
