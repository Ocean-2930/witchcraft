from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dungeon_inventory.skill_tree import SkillTree


def _new_skill_tree():
    from .dungeon_inventory.skill_tree import SkillTree

    return SkillTree()


@dataclass
class UnitBase:
    """유닛을 구성하는 기본 스탯과 보유 스킬 트리."""

    name: str
    max_hp: int
    attack_power: int
    max_mp: int = 0
    defense: int = 0
    penetration: int = 0
    accuracy: int = 0
    evasion: int = 0
    attack_speed: int = 0
    move_speed: int = 0
    luck: int = 0
    overloaded: int = 0
    critical_chance: float = 0.0
    critical_evasion: float = 0.0
    critical_damage: float = 0.0
    critical_damage_reduction: float = 0.0
    damage_increase: float = 0.0
    incoming_damage_reduction: float = 0.0
    equipment_drop_rate: float = 0.0
    gold_drop_amount: float = 0.0
    skill_tree: SkillTree = field(default_factory=_new_skill_tree)
