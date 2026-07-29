from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import pygame


@dataclass(kw_only=True)
class Item:
    SPRITE_DIRECTORY: ClassVar[Path] = (
        Path(__file__).resolve().parents[1] / "assets" / "images" / "items"
    )
    _sprite_cache: ClassVar[dict[str, pygame.Surface | None]] = {}

    item_code: str = ""
    max_stack: ClassVar[int] = 1

    @classmethod
    def get_sprite(cls, item_code: str) -> pygame.Surface | None:
        """아이템 코드에 해당하는 원본 스프라이트를 반환한다."""
        if not item_code:
            return None

        if item_code not in cls._sprite_cache:
            sprite_path = cls.SPRITE_DIRECTORY / f"{item_code}.png"
            cls._sprite_cache[item_code] = (
                pygame.image.load(str(sprite_path)).convert_alpha()
                if sprite_path.is_file()
                else None
            )

        return cls._sprite_cache[item_code]
