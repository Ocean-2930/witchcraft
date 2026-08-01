"""실제 게임에서 사용하는 개별 스킬 구현 모음."""

from .active_skills import AttackSkill
from .passive_skills import STAT_PASSIVE_SKILLS, create_stat_passive_skills

__all__ = ["AttackSkill", "STAT_PASSIVE_SKILLS", "create_stat_passive_skills"]
