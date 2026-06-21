from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..unit import Unit


@dataclass
class SkillBase:
    name: str
    level: int = 1
    max_level: int = 1

    def can_use(self, caster: Unit, target: Unit | None = None):
        return caster.is_alive and caster.mp >= self.mp_cost

    def spend_cost(self, caster: Unit):
        return caster.spend_mp(self.mp_cost)
