from __future__ import annotations

from typing import TYPE_CHECKING

from .attack_effect import AttackEffect
from .skill_base import SkillBase

if TYPE_CHECKING:
    from random import Random

    from units import AttackResult, DamageBlock, DamagePreview, Unit


class ActiveSkill(SkillBase):
    skill_coefficient: float = 1.0
    mp_cost: int = 0

    def __init__(
        self,
        name: str,
        mp_cost: int = 0,
        skill_coefficient: float = 1.0,
        range_vectors: list[tuple[int, int]] | None = None,
        requires_direction: bool = True,
        allow_diagonal: bool = False,
        max_level: int = 1,
        skill_code: str | None = None,
    ):
        super().__init__(
            name=name,
            skill_code=skill_code or name,
            max_level=max_level,
            mp_cost=mp_cost,
            range_vectors=[(0, -1)] if range_vectors is None else range_vectors,
            requires_direction=requires_direction,
            allow_diagonal=allow_diagonal,
            effects=[AttackEffect(skill_coefficient=skill_coefficient)],
        )
        self.skill_coefficient = skill_coefficient

    def can_use(self, caster: Unit, target: Unit | None = None):
        return super().can_use(caster, target)

    def make_damage_block(self, caster: Unit, target: Unit) -> DamageBlock:
        return self.effects[0].make_damage_block(caster, target)

    def peek(self, caster: Unit, target: Unit) -> DamagePreview:
        return self.make_damage_block(caster, target).peek()

    def use(self, caster: Unit, target: Unit, rng: Random | None = None) -> AttackResult:
        if not self.can_use(caster, target):
            raise ValueError(f"{caster.name} cannot use {self.name}.")

        return super().use(caster, target, rng)[0]


Skill = ActiveSkill
