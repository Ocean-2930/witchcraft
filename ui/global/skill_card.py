import pygame

from ui.renderer import Renderer
from ui.ui import UIElement
from .skill_info_window import SkillInfoWindow


class SkillCardRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, card):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.card = card

    def draw(self, screen):
        if not self.card.visible or not self.card.is_in_clip():
            return
        previous_clip = screen.get_clip()
        clip_rect = self.card.get_clip_rect()
        if clip_rect is not None:
            screen.set_clip(previous_clip.clip(clip_rect))
        pygame.draw.rect(screen, (42, 53, 65), self.rect, border_radius=6)
        pygame.draw.rect(screen, (112, 130, 147), self.rect, 1, border_radius=6)
        icon = self.card.icon_rect
        pygame.draw.rect(screen, (24, 31, 39), icon, border_radius=5)
        pygame.draw.rect(screen, (94, 119, 139), icon, 1, border_radius=5)
        initial = self.card.skill_instance.skill.name[:1]
        icon_text = self.card.name_font.render(initial, True, (219, 231, 240))
        screen.blit(icon_text, icon_text.get_rect(center=icon.center))
        name = self.card.name_font.render(
            self.card.skill_instance.skill.name, True, (238, 242, 246)
        )
        screen.blit(name, (icon.right + 10, self.rect.top + 10))
        pygame.draw.line(
            screen,
            (82, 99, 114),
            (icon.right + 10, self.rect.top + 34),
            (self.rect.right - 10, self.rect.top + 34),
        )
        level = self.card.level_font.render(
            f"Lv.{self.card.skill_instance.level}/{self.card.max_level}",
            True,
            (193, 204, 213),
        )
        screen.blit(level, (icon.right + 10, self.rect.top + 42))
        screen.set_clip(previous_clip)


class SkillCard(UIElement):
    """투자 동작 없이 스킬 인스턴스의 요약을 표시하는 공용 카드."""

    def __init__(
        self,
        scene,
        skill_instance,
        pos_x,
        pos_y,
        width=190,
        height=76,
        clip_rect_getter=None,
        on_icon_hover=None,
        max_level=None,
    ):
        self.skill_instance = skill_instance
        self.max_level = (
            skill_instance.max_level if max_level is None else max_level
        )
        if self.max_level < self.skill_instance.level:
            raise ValueError("max_level은 현재 스킬 레벨 이상이어야 합니다.")
        self.visible = True
        self.clip_rect_getter = clip_rect_getter
        self.on_icon_hover_callback = on_icon_hover
        self.name_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.level_font = pygame.font.SysFont("malgungothic", 14)
        self.info_window = SkillInfoWindow(
            scene,
            skill_instance,
            max_level=self.max_level,
        )
        renderer = SkillCardRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer, background=False)

    @property
    def icon_rect(self):
        return pygame.Rect(self.rect.left + 10, self.rect.top + 10, 48, 48)

    def get_clip_rect(self):
        return self.clip_rect_getter() if self.clip_rect_getter else None

    def is_in_clip(self):
        clip_rect = self.get_clip_rect()
        return clip_rect is None or self.rect.colliderect(clip_rect)

    def set_visible(self, visible):
        self.visible = visible
        if not visible:
            self.info_window.hide()
            if self.scene.ui_focus is self:
                self.scene.ui_focus = None

    def pos_check(self, mouse_pos):
        clip_rect = self.get_clip_rect()
        return (
            self.visible
            and self.is_in_clip()
            and self.icon_rect.collidepoint(mouse_pos)
            and (clip_rect is None or clip_rect.collidepoint(mouse_pos))
        )

    def on_enter(self):
        self.info_window.show_at(self.icon_rect.bottomright)

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        self.info_window.show_at(mouse_position)
        if self.on_icon_hover_callback is not None:
            self.on_icon_hover_callback(mouse_position, wheel_move)

    def on_exit(self):
        self.info_window.hide()

    def destroy(self):
        self.info_window.destroy()
        super().destroy()
        self.renderer.destroy()
