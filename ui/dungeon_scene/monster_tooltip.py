import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class MonsterTooltipRenderer(Renderer):
    draw_layer = 100

    def __init__(self, scene):
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    def draw(self, screen):
        monster = self.scene.hovered_monster
        if monster is None:
            return

        unit = monster["unit"]
        preview = self.scene.player.make_damage_block(unit).peek()
        lines = (
            unit.name,
            f"일반 {preview.normal_damage} / 치명 {preview.critical_damage}",
            f"명중 {preview.hit_rate:.0f}% / 치명 {preview.critical_rate:.0f}%",
            f"기대 {preview.expected_damage:.1f}",
        )
        surfaces = [self.scene.peek_font.render(line, True, (238, 234, 220)) for line in lines]
        padding = 10
        gap = 4
        rect = pygame.Rect(
            0,
            0,
            max(surface.get_width() for surface in surfaces) + padding * 2,
            sum(surface.get_height() for surface in surfaces) + gap * (len(surfaces) - 1) + padding * 2,
        )
        rect.midbottom = (monster["renderer"].rect.centerx, monster["renderer"].rect.top - 8)
        rect.clamp_ip(screen.get_rect())
        pygame.draw.rect(screen, (18, 22, 25), rect, border_radius=4)
        pygame.draw.rect(screen, (126, 132, 134), rect, width=2, border_radius=4)

        text_y = rect.top + padding
        for surface in surfaces:
            screen.blit(surface, (rect.left + padding, text_y))
            text_y += surface.get_height() + gap
