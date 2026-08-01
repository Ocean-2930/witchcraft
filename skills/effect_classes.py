from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skill_effect import SkillEffect

if TYPE_CHECKING:
    from random import Random

    from units import Unit
    from units.unit_base import UnitBase


@dataclass
class AttackEffect(SkillEffect):
    skill_coefficient: float = 1.0
    is_active_effect: bool = True

    def can_apply(self, caster: Unit, target: Unit | None = None) -> bool:
        return target is not None and target.is_alive

    def make_damage_block(self, caster: Unit, target: Unit):
        return caster.make_damage_block(
            target,
            skill_coefficient=self.skill_coefficient,
        )

    def peek(self, caster: Unit, target: Unit | None = None):
        if target is None:
            return None
        return self.make_damage_block(caster, target).peek()

    def apply(
        self,
        caster: Unit,
        target: Unit | None = None,
        rng: Random | None = None,
    ):
        if target is None:
            return None
        return self.make_damage_block(caster, target).apply(rng)


@dataclass
class BuffEffect(SkillEffect):
    buff: object
    target_self: bool = False
    is_active_effect: bool = True

    def can_apply(self, caster: Unit, target: Unit | None = None) -> bool:
        buff_target = self.get_buff_target(caster, target)
        return buff_target is not None and buff_target.is_alive

    def apply(
        self,
        caster: Unit,
        target: Unit | None = None,
        rng: Random | None = None,
    ):
        buff_target = self.get_buff_target(caster, target)
        if buff_target is None:
            return None
        return buff_target.add_buff(self.buff)

    def get_buff_target(self, caster: Unit, target: Unit | None = None):
        if self.target_self:
            return caster
        return target


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

    def apply_passive(
        self,
        owner: UnitBase,
        level: int = 1,
        stack: int = 1,
    ):
        current = getattr(owner, self.stat_name)
        setattr(
            owner,
            self.stat_name,
            current + self.amount_per_level * level * stack,
        )
        return owner
