from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skill_effect import SkillEffect

if TYPE_CHECKING:
    from units.unit_base import UnitBase


@dataclass
class PassiveEffect(SkillEffect):
    is_active_effect: bool = False

    def apply_passive(
        self,
        owner: UnitBase,
        level: int = 1,
        stack: int = 1,
    ):
        return None


@dataclass
class StatIncreaseEffect(PassiveEffect):
    """레벨과 중첩에 비례해 UnitBase의 단일 능력치를 증가시킨다."""

    stat_name: str = ""
    amount_per_level: int | float = 0

    def apply_passive(self, owner: UnitBase, level: int = 1, stack: int = 1):
        current = getattr(owner, self.stat_name)
        setattr(
            owner,
            self.stat_name,
            current + self.amount_per_level * level * stack,
        )
        return owner
