import pygame

from .scene import Scene
from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class Hud(Scene):
    def scene_initialize(self):
        self.font = pygame.font.Font(None, 24)
        self.skill_font = pygame.font.SysFont("malgungothic", 18, bold=True)
        self.text_color = (255, 255, 255)
        self.line_height = 22
        self.delta_time = 0.0
        self.game_events = {}
        self.mouse_position = None
        self.wheel_move = 0

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.delta_time = delta_time
        self.game_events = game_events
        self.mouse_position = mouse_position
        self.wheel_move = wheel_move

    def scene_draw(self):
        lines = [
            f"delta_time: {self.delta_time:.4f}",
            f"mouse_position: {self.mouse_position}",
            f"wheel_move: {self.wheel_move}",
            "game_events:",
        ]

        for key, value in self.game_events.items():
            lines.append(f"  {key}: {value}")

        for index, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            self.game.virtual_screen.blit(text_surface, (12, 12 + index * self.line_height))

        self.draw_skill_debug()

    def draw_skill_debug(self):
        scene = self.game.scene
        skill_call = getattr(scene, "last_skill_call", None)

        if skill_call is None:
            return

        text = self.get_skill_debug_text(scene, skill_call)
        text_surface = self.skill_font.render(text, True, (238, 234, 220))
        padding_x = 12
        padding_y = 8
        box_rect = text_surface.get_rect()
        box_rect.width += padding_x * 2
        box_rect.height += padding_y * 2
        box_rect.bottomright = (VIRTUAL_WIDTH - 16, VIRTUAL_HEIGHT - 16)

        pygame.draw.rect(self.game.virtual_screen, (18, 22, 25), box_rect, border_radius=4)
        pygame.draw.rect(self.game.virtual_screen, (126, 132, 134), box_rect, width=2, border_radius=4)
        self.game.virtual_screen.blit(text_surface, (box_rect.left + padding_x, box_rect.top + padding_y))

    def get_skill_debug_text(self, scene, skill_call):
        label = skill_call["label"]

        if skill_call.get("cancelled"):
            return f"스킬 {label}: 취소"

        direction = skill_call.get("direction")
        format_direction = getattr(scene, "format_direction", None)

        if format_direction is not None:
            direction_text = format_direction(direction)
        else:
            direction_text = str(direction)

        return f"스킬 {label}: {direction_text}"
