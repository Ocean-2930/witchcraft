from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import pygame

from utilities import load_code_sprite


@dataclass(kw_only=True)
class Item:
    SPRITE_DIRECTORY: ClassVar[Path] = (
        Path(__file__).resolve().parents[1] / "assets" / "images" / "items"
    )
    _sprite_cache: ClassVar[dict[str, pygame.Surface]] = {}

    item_code: str = ""
    max_stack: ClassVar[int] = 1

    @classmethod
    def get_sprite(cls, item_code: str) -> pygame.Surface | None:
        """아이템 코드에 해당하는 원본 스프라이트를 반환한다."""
        return load_code_sprite(
            cls.SPRITE_DIRECTORY,
            item_code,
            cls._sprite_cache,
        )

    def get_name(self) -> str:
        return self.item_code

    def get_description(self) -> str:
        return ""

    def get_detail_rows(self) -> list[tuple[str, str]]:
        return []

    def get_flavor_text(self) -> str:
        return ""
