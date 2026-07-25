from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .skill_effect import SkillEffect

if TYPE_CHECKING:
    from ..unit import Unit


@dataclass
class PassiveEffect(SkillEffect):
    is_active_effect: bool = False

    def apply_passive(self, owner: Unit):
        return None
