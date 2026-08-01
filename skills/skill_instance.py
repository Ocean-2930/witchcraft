from __future__ import annotations

from dataclasses import dataclass

from .skill_base import SkillBase


@dataclass
class SkillInstance:
    """실제로 보유 중인 스킬과 현재 레벨 및 중첩 수."""

    skill: SkillBase
    level: int = 1
    stack: int = 1

    def __post_init__(self):
        if not 0 <= self.level <= self.skill.max_level:
            raise ValueError(
                f"level은 0 이상 {self.skill.max_level} 이하여야 합니다."
            )
        if self.stack < 1:
            raise ValueError("stack은 1 이상이어야 합니다.")

    @property
    def max_level(self):
        return self.skill.max_level
