from __future__ import annotations

from dataclasses import dataclass, field

from units.skill.skill_base import SkillBase


@dataclass
class SkillTree:
    """영웅이 보유한 스킬 목록."""

    skills: list[SkillBase] = field(default_factory=list)

    def add_skill(self, skill: SkillBase):
        if any(owned_skill is skill for owned_skill in self.skills):
            return False

        self.skills.append(skill)
        return True

    def remove_skill(self, skill: SkillBase):
        for index, owned_skill in enumerate(self.skills):
            if owned_skill is skill:
                del self.skills[index]
                return True

        return False
