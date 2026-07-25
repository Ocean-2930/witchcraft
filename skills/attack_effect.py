from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skill_effect import SkillEffect

if TYPE_CHECKING:
    from random import Random

    from units import Unit


@dataclass
class AttackEffect(SkillEffect):
    skill_coefficient: float = 1.0
    is_active_effect: bool = True

    def can_apply(self, caster: Unit, target: Unit | None = None) -> bool:
        return target is not None and target.is_alive

    def make_damage_block(self, caster: Unit, target: Unit):
        return caster.make_damage_block(target, skill_coefficient=self.skill_coefficient)

    def peek(self, caster: Unit, target: Unit | None = None):
        if target is None:
            return None

        return self.make_damage_block(caster, target).peek()

    def apply(self, caster: Unit, target: Unit | None = None, rng: Random | None = None):
        if target is None:
            return None

        return self.make_damage_block(caster, target).apply(rng)
