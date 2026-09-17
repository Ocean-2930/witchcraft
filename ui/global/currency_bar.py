from pathlib import Path

import pygame

from ui.renderer import Renderer
from utilities import load_code_sprite


class CurrencyBar(Renderer):
    """인벤토리 getter를 통해 두 재화의 현재 보유량을 표시한다."""

    SPRITE_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "images" / "currencies"
    _sprite_cache = {}

    def __init__(self, scene, right, center_y, inventory_getter, visible_getter=lambda: True,
                 entry_centers=None):
        super().__init__(scene, right - 300, center_y, 600, 26)
        self.inventory_getter = inventory_getter
        self.visible_getter = visible_getter
        self.entry_centers = entry_centers
        self.font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.minimum_box_width = max(120, self.font.size("10,000,000")[0] + 24)
        self.icons = [self.get_icon(code) for code in ("gold", "harmony_stone")]

    @classmethod
    def get_icon(cls, code, size=24):
        sprite = load_code_sprite(cls.SPRITE_DIRECTORY, code, cls._sprite_cache)
        bounds = sprite.get_bounding_rect()
        cropped = sprite.subsurface(bounds) if bounds.width and bounds.height else sprite
        return pygame.transform.smoothscale_by(cropped, size / max(cropped.get_size()))

    def draw(self, screen):
        if not self.visible_getter():
            return
        inventory = self.inventory_getter()
        if inventory is None:
            return
        entries = [
            (icon, self.font.render(f"{amount:,}", True, (235, 240, 245)))
            for icon, amount in (
                (self.icons[0], inventory.gold),
                (self.icons[1], inventory.harmony_stones),
            )
        ]
        box_widths = [max(self.minimum_box_width, text.get_width() + 24) for _, text in entries]
        total_width = sum(32 + width for width in box_widths) + 32
        x = self.rect.right - total_width
        for index, (icon, text) in enumerate(entries):
            box_width = box_widths[index]
            if self.entry_centers is not None:
                x = self.entry_centers[index] - (32 + box_width) // 2
            screen.blit(icon, icon.get_rect(center=(x + 12, self.rect.centery)))
            box = pygame.Rect(x + 32, self.rect.centery - 13, box_width, 26)
            pygame.draw.rect(screen, (12, 19, 27), box)
            pygame.draw.rect(screen, (103, 119, 135), box, 1)
            screen.blit(text, text.get_rect(center=box.center))
            x += 32 + box_width + 32
