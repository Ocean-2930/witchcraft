import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer
from ui.ui import UIElement


class SkillInfoWindowRenderer(Renderer):
    draw_layer = 200

    def __init__(self, scene, pos_x, pos_y, width, height, window):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.window = window

    def draw(self, screen):
        if not self.window.visible:
            return
        pygame.draw.rect(screen, (12, 15, 19), self.rect, border_radius=6)
        pygame.draw.rect(screen, (115, 129, 142), self.rect, 2, border_radius=6)
        title = self.window.title_font.render(
            f"{self.window.skill_instance.skill.name}  "
            f"Lv.{self.window.skill_instance.level}/{self.window.max_level}",
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
        self.window.draw_description(screen, line_y + 9)


class SkillInfoWindow(UIElement):
    """스킬 인스턴스의 이름, 레벨과 설명을 표시하는 공용 정보창."""

    def __init__(
        self,
        scene,
        skill_instance,
        max_level=None,
        width=280,
        height=142,
    ):
        self.skill_instance = skill_instance
        self.max_level = (
            skill_instance.max_level if max_level is None else max_level
        )
        if self.max_level < self.skill_instance.level:
            raise ValueError("max_level은 현재 스킬 레벨 이상이어야 합니다.")
        self.visible = False
        self.title_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.description_font = pygame.font.SysFont("malgungothic", 14)
        renderer = SkillInfoWindowRenderer(scene, 0, 0, width, height, self)
        super().__init__(scene, renderer=renderer, background=False)

    def show_at(self, mouse_position):
        if mouse_position is None:
            return
        left = min(mouse_position[0] + 16, VIRTUAL_WIDTH - self.rect.width - 8)
        top = min(mouse_position[1] + 16, VIRTUAL_HEIGHT - self.rect.height - 8)
        left = max(8, left)
        top = max(8, top)
        self.set_transform(
            left + self.rect.width // 2,
            top + self.rect.height // 2,
        )
        self.visible = True

    def hide(self):
        self.visible = False

    def pos_check(self, mouse_pos):
        return False

    def draw_description(self, screen, start_y):
        text = self.skill_instance.skill.description or "설명 없음"
        color = (184, 195, 204) if self.skill_instance.skill.description else (105, 115, 124)
        available_width = self.rect.width - 24
        lines = []
        current = ""
        for character in text:
            candidate = current + character
            if current and self.description_font.size(candidate)[0] > available_width:
                lines.append(current)
                current = character
            else:
                current = candidate
        if current:
            lines.append(current)

        line_height = self.description_font.get_linesize()
        maximum_lines = max(1, (self.rect.bottom - 10 - start_y) // line_height)
        visible_lines = lines[:maximum_lines]
        if len(lines) > maximum_lines and visible_lines:
            last = visible_lines[-1]
            while last and self.description_font.size(last + "…")[0] > available_width:
                last = last[:-1]
            visible_lines[-1] = last + "…"
        for index, line in enumerate(visible_lines):
            surface = self.description_font.render(line, True, color)
            screen.blit(surface, (self.rect.left + 12, start_y + index * line_height))

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
