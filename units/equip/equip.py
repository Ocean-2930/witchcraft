from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from ..skill.skill_base import SkillBase
    from ..unit import Player


@dataclass
class Equip:
    TYPE_WEAPON: ClassVar[str] = "weapon"
    TYPE_SUB_WEAPON: ClassVar[str] = "sub_weapon"
    TYPE_ARMOR: ClassVar[str] = "armor"
    TYPE_ACCESSORY: ClassVar[str] = "accessory"

    type: str
    baseskill: SkillBase | None = None

    def equipcheck(self, player: Player, target: Equip | None) -> bool:
        return target is None or target.unequipcheck(player)

    def unequipcheck(self, player: Player) -> bool:
        return True

    def mergecheck(self, equip: Equip) -> bool:
        return False
