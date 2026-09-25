from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .unit import Unit
from .enemy_definitions import get_enemy_definition


class EnemyMode(Enum):
    GUARD = "guard"
    COMBAT = "combat"


@dataclass
class Enemy(Unit):
    drop_gold: int = 0
    drop_harmony_stones: int = 0
    drop_items: tuple[tuple[str | int, float], ...] = ()
    ai_mode: EnemyMode = EnemyMode.GUARD
    patrol_target: tuple[int, int] | None = None
    last_known_player_position: tuple[int, int] | None = None

    @classmethod
    def from_code(cls, code: str, *, tile_x: int = 0, tile_y: int = 0) -> Enemy:
        """JSON 기본 능력치로 독립적인 새 적을 생성한다. 이어하기에는 사용하지 않는다."""
        return cls(**get_enemy_definition(code), tile_x=tile_x, tile_y=tile_y)

    def set_ai_mode(self, mode: EnemyMode) -> None:
        self.ai_mode = mode
        if mode is EnemyMode.COMBAT:
            self.patrol_target = None

    def remember_player_position(self, position: tuple[int, int]) -> None:
        self.last_known_player_position = position
        self.set_ai_mode(EnemyMode.COMBAT)

    def forget_player_position(self) -> None:
        self.last_known_player_position = None
        self.set_ai_mode(EnemyMode.GUARD)

    @property
    def is_in_combat(self) -> bool:
        return self.ai_mode is EnemyMode.COMBAT
