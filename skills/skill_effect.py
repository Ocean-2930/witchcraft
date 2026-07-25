from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random

    from units import Unit


class SkillEffect:
    is_active_effect: bool = False

    def can_apply(self, caster: Unit, target: Unit | None = None) -> bool:
        return True

    def peek(self, caster: Unit, target: Unit | None = None):
        return None

    def apply(self, caster: Unit, target: Unit | None = None, rng: Random | None = None):
        return None
