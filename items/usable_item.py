from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .item import Item

if TYPE_CHECKING:
    from random import Random

    from skills.skill_base import SkillBase
    from units import Unit


@dataclass
class UsableItem(Item):
    skillbase: SkillBase | None = None

    def use(self, user: Unit, target: Unit | None = None, rng: Random | None = None):
        if self.skillbase is None:
            return None

        return self.skillbase.use(user, target, rng)

    def get_use_log(self, result) -> str | None:
        """사용 결과에 따른 추가 로그를 반환한다."""
        return None
