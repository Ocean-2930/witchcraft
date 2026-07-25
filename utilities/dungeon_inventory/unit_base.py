from __future__ import annotations

from dataclasses import dataclass, field

from units import Player

from .skill_tree import SkillTree


@dataclass
class UnitBase:
    """던전 인벤토리에서 플레이어블 캐릭터 한 명을 나타낸다."""

    unit: Player
    skill_tree: SkillTree = field(default_factory=SkillTree)
