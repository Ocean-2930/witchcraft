from math import hypot

import pygame

from ui.renderer import Renderer


class SkillDirectionCompassRenderer(Renderer):
    draw_layer = 50

    def __init__(self, scene, pos_x, pos_y, width, height, direction_getter):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.direction_getter = direction_getter

    def draw(self, screen):
        center = self.rect.center
        radius = min(self.rect.width, self.rect.height) // 2

        pygame.draw.circle(screen, (28, 32, 35), center, radius)
        pygame.draw.circle(screen, (140, 146, 148), center, radius, width=2)

        for direction_x, direction_y in (
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ):
            length = hypot(direction_x, direction_y)
            unit_x = direction_x / length
            unit_y = direction_y / length
            start = (
                round(center[0] + unit_x * (radius - 7)),
                round(center[1] + unit_y * (radius - 7)),
            )
            end = (
                round(center[0] + unit_x * (radius - 3)),
                round(center[1] + unit_y * (radius - 3)),
            )
            pygame.draw.line(screen, (104, 111, 114), start, end, width=1)

        direction = self.direction_getter()
        if direction is None:
            pygame.draw.circle(screen, (104, 111, 114), center, 3)
            return

        direction_x, direction_y = direction
        length = hypot(direction_x, direction_y)
        unit_x = direction_x / length
        unit_y = direction_y / length
        tip = pygame.Vector2(
            center[0] + unit_x * (radius - 7),
            center[1] + unit_y * (radius - 7),
        )
        tail = pygame.Vector2(
            center[0] - unit_x * 7,
            center[1] - unit_y * 7,
        )
        perpendicular = pygame.Vector2(-unit_y, unit_x)
        head_base = tip - pygame.Vector2(unit_x, unit_y) * 8
        arrow_color = (246, 202, 104)

        pygame.draw.line(screen, arrow_color, tail, head_base, width=3)
        pygame.draw.polygon(
            screen,
            arrow_color,
            (
                tip,
                head_base + perpendicular * 5,
                head_base - perpendicular * 5,
            ),
        )
