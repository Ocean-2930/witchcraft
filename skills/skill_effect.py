from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random

    from units import Unit


class SkillEffect:
    is_active_effect: bool = False

    def can_apply(self, caster: Unit, target: Unit | None = None, context=None) -> bool:
        return True

    def peek(self, caster: Unit, target: Unit | None = None, context=None):
        return None

    def apply(self, caster: Unit, target: Unit | None = None, rng: Random | None = None, context=None):
        return None

    def apply_targets(self, caster, contexts, rng=None):
        return [
            self.apply(caster, context.target, rng, context)
            for context in contexts
        ]
