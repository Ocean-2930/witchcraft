from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .item import Item

if TYPE_CHECKING:
    from skills.skill_base import SkillBase
    from units import Player


@dataclass
class Equip(Item):
    TYPE_WEAPON: ClassVar[str] = "weapon"
    TYPE_SUB_WEAPON: ClassVar[str] = "sub_weapon"
    TYPE_ARMOR: ClassVar[str] = "armor"
    TYPE_ACCESSORY: ClassVar[str] = "accessory"

    type: str
    baseskill: SkillBase | None = None

    def get_drop_stat_rows(self) -> list:
        return []

    def equipcheck(self, player: Player, target: Equip | None) -> bool:
        return target is None or target.unequipcheck(player)

    def unequipcheck(self, player: Player) -> bool:
        return True

    def mergecheck(self, equip: Equip) -> bool:
        return False
