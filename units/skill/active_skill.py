from __future__ import annotations

from typing import TYPE_CHECKING

from .skill_base import SkillBase

if TYPE_CHECKING:
    from random import Random

    from ..unit import AttackResult, DamageBlock, DamagePreview, Unit


class ActiveSkill(SkillBase):
    skill_coefficient: float = 1.0
    mp_cost: int = 0

    def __init__(self, name: str, mp_cost: int = 0, skill_coefficient: float = 1.0):
        super().__init__(name, mp_cost)
        self.skill_coefficient = skill_coefficient

    def can_use(self, caster: Unit, target: Unit | None = None):
        return target is not None and target.is_alive and super().can_use(caster, target)

    def make_damage_block(self, caster: Unit, target: Unit) -> DamageBlock:
        return caster.make_damage_block(target, skill_coefficient=self.skill_coefficient)

    def peek(self, caster: Unit, target: Unit) -> DamagePreview:
        return self.make_damage_block(caster, target).peek()

    def use(self, caster: Unit, target: Unit, rng: Random | None = None) -> AttackResult:
        if not self.can_use(caster, target):
            raise ValueError(f"{caster.name} cannot use {self.name}.")

        self.spend_cost(caster)
        return self.make_damage_block(caster, target).apply(rng)
