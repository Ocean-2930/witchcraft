from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skill_effect import SkillEffect

if TYPE_CHECKING:
    from random import Random

    from units import Unit


@dataclass
class BuffEffect(SkillEffect):
    buff: object
    target_self: bool = False
    is_active_effect: bool = True

    def can_apply(self, caster: Unit, target: Unit | None = None) -> bool:
        buff_target = self.get_buff_target(caster, target)
        return buff_target is not None and buff_target.is_alive

    def apply(self, caster: Unit, target: Unit | None = None, rng: Random | None = None):
        buff_target = self.get_buff_target(caster, target)

        if buff_target is None:
            return None

        return buff_target.add_buff(self.buff)

    def get_buff_target(self, caster: Unit, target: Unit | None = None):
        if self.target_self:
            return caster

        return target
