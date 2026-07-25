from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from .equip import Equip

if TYPE_CHECKING:
    from units.skill import SkillInstance


@dataclass
class SkilledEquip(Equip):
    MAX_SKILLS: ClassVar[int] = 7

    skills: list[SkillInstance] = field(default_factory=list)

    def __post_init__(self):
        if len(self.skills) > self.MAX_SKILLS:
            raise ValueError(f"스킬은 최대 {self.MAX_SKILLS}개까지 장착할 수 있습니다.")

    def add_skill(self, skill: SkillInstance):
        if len(self.skills) >= self.MAX_SKILLS:
            return False

        self.skills.append(skill)
        return True

    def remove_skill(self, skill: SkillInstance):
        if skill not in self.skills:
            return False

        self.skills.remove(skill)
        return True

    def getstar(self) -> int:
        return len(self.skills)

    def mergecheck(self, equip: Equip) -> bool:
        return (
            isinstance(equip, SkilledEquip)
            and self.type == equip.type
            and self.getstar() + equip.getstar() <= self.MAX_SKILLS
        )
