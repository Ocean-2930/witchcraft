from __future__ import annotations

from typing import TYPE_CHECKING

from .effect_classes import AttackEffect
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
        max_level: int | None = 1,
        allow_negative_level: bool = False,
        skill_code: str | None = None,
        description: str = "",
        hit_rate_calculator=None,
        critical_rate_calculator=None,
        defense_modifier_calculator=None,
        excess_penetration_modifier_calculator=None,
        critical_modifier_calculator=None,
        damage_increase_modifier_calculator=None,
        final_damage_calculator=None,
    ):
        super().__init__(
            name=name,
            skill_code=skill_code or name,
            description=description,
            max_level=max_level,
            allow_negative_level=allow_negative_level,
            mp_cost=mp_cost,
            range_vectors=[(0, -1)] if range_vectors is None else range_vectors,
            requires_direction=requires_direction,
            allow_diagonal=allow_diagonal,
            effects=[AttackEffect(skill_coefficient=skill_coefficient)],
            hit_rate_calculator=hit_rate_calculator,
            critical_rate_calculator=critical_rate_calculator,
            defense_modifier_calculator=defense_modifier_calculator,
            excess_penetration_modifier_calculator=excess_penetration_modifier_calculator,
            critical_modifier_calculator=critical_modifier_calculator,
            damage_increase_modifier_calculator=damage_increase_modifier_calculator,
            final_damage_calculator=final_damage_calculator,
        )
        self.skill_coefficient = skill_coefficient

    def can_use(self, caster: Unit, target: Unit | None = None, level: int = 1):
        return super().can_use(caster, target, level)

    def make_damage_block(self, caster: Unit, target: Unit, level: int = 1) -> DamageBlock:
        from .skill_base import SkillCastContext

        context = SkillCastContext(self, level, caster, target)
        return self.effects[0].make_damage_block(caster, target, context)

    def peek(self, caster: Unit, target: Unit, level: int = 1) -> DamagePreview:
        return self.make_damage_block(caster, target, level).peek()

    def use(self, caster: Unit, target: Unit, rng: Random | None = None, level: int = 1) -> AttackResult:
        if not self.can_use(caster, target, level):
            raise ValueError(f"{caster.name} cannot use {self.name}.")

        return super().use(caster, target, rng, level)[0]


Skill = ActiveSkill
