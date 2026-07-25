from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .equip import Equip

if TYPE_CHECKING:
    from units.skill import Skill


@dataclass
class SkilledEquip(Equip):
    skills: list[Skill] = field(default_factory=list)

    def getstar(self) -> int:
        return len(self.skills)

    def mergecheck(self, equip: Equip) -> bool:
        return (
            isinstance(equip, SkilledEquip)
            and self.type == equip.type
            and self.getstar() + equip.getstar() <= 7
        )
