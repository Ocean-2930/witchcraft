from hashlib import sha256
from pathlib import Path

import pygame


FALLBACK_COLORS = (
    (184, 76, 76),
    (76, 132, 184),
    (91, 163, 105),
    (157, 101, 190),
    (196, 139, 63),
    (65, 164, 165),
)


def load_code_sprite(
    directory: Path,
    code: str,
    cache: dict[str, pygame.Surface],
    fallback_size: int = 128,
) -> pygame.Surface | None:
    if not code:
        return None
    if code in cache:
        return cache[code]

    sprite_path = directory / f"{code}.png"
    if sprite_path.is_file():
        sprite = pygame.image.load(str(sprite_path))
        if pygame.display.get_surface() is not None:
            sprite = sprite.convert_alpha()
    else:
        sprite = create_fallback_sprite(code, fallback_size)

    cache[code] = sprite
    return sprite


def create_fallback_sprite(code: str, size: int) -> pygame.Surface:
    color_index = sha256(code.encode("utf-8")).digest()[0]
    color = FALLBACK_COLORS[color_index % len(FALLBACK_COLORS)]
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill((*color, 255))
    border_width = max(2, size // 16)
    pygame.draw.rect(
        surface,
        (225, 232, 238),
        surface.get_rect(),
        width=border_width,
    )
    pygame.draw.rect(
        surface,
        tuple(max(0, channel - 45) for channel in color),
        surface.get_rect().inflate(-size // 3, -size // 3),
        width=border_width,
    )
    return surface
