from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .unit import Unit


class EnemyMode(Enum):
    GUARD = "guard"
    COMBAT = "combat"


@dataclass
class Enemy(Unit):
    ai_mode: EnemyMode = EnemyMode.GUARD
    patrol_target: tuple[int, int] | None = None
    last_known_player_position: tuple[int, int] | None = None

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
