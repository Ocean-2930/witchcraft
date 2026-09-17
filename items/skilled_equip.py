from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar

from .equip import Equip

if TYPE_CHECKING:
    from skills import SkillInstance


@dataclass
class SkilledEquip(Equip):
    MAX_SKILLS: ClassVar[int] = 7

    base_skills: list[SkillInstance] = field(default_factory=list)

    def __post_init__(self):
        if len(self.base_skills) > self.MAX_SKILLS:
            raise ValueError(f"스킬은 최대 {self.MAX_SKILLS}개까지 장착할 수 있습니다.")

    def add_skill(self, skill: SkillInstance):
        if len(self.base_skills) >= self.MAX_SKILLS:
            return False

        self.base_skills.append(skill)
        return True

    def remove_skill(self, skill: SkillInstance):
        if skill not in self.base_skills:
            return False

        self.base_skills.remove(skill)
        return True

    def getstar(self) -> int:
        return len(self.base_skills)

    def get_drop_stat_rows(self) -> list[SkillInstance | None]:
        rows: list[SkillInstance | None] = list(self.base_skills)
        rows.extend(None for _ in range(self.MAX_SKILLS - len(rows)))
        return rows

    def mergecheck(self, equip: Equip) -> bool:
        try:
            self.synthesize_rows(equip, self.base_skills, equip.base_skills)
        except (AttributeError, ValueError):
            return False
        return True

    def synthesize_rows(self, material, main_rows, material_rows):
        """원본을 변경하지 않고 정렬된 스킬 행과 행별 합성 분류를 반환한다."""
        if (
            not isinstance(material, SkilledEquip)
            or self.type not in (self.TYPE_WEAPON, self.TYPE_ARMOR, self.TYPE_ACCESSORY)
            or self.type != material.type
        ):
            raise ValueError("같은 종류의 무기·방어구·장신구만 재료로 선택할 수 있습니다.")

        def by_code(rows):
            result = {}
            for row in rows:
                if row is None:
                    continue
                code = row.skill.skill_code
                if code in result:
                    raise ValueError("같은 장비 안에 중복된 스킬이 있습니다.")
                result[code] = row
            return result

        main = by_code(main_rows)
        other = by_code(material_rows)
        if len(main.keys() | other.keys()) >= self.MAX_SKILLS:
            raise ValueError("결과 스킬이 7개 이상인 장비는 재료로 선택할 수 없습니다.")

        upgraded, shared, original, added = [], [], [], []
        for code, row in main.items():
            result = deepcopy(row)
            if code not in other:
                original.append((result, "original"))
            elif row.level == other[code].level:
                if row.max_level is not None and row.level >= row.max_level:
                    raise ValueError("최대 레벨 스킬은 레벨을 올릴 수 없습니다.")
                result.level += 1
                upgraded.append((result, "upgraded"))
            else:
                shared.append((result, "lower" if row.level < other[code].level else "original"))
        for code, row in other.items():
            if code not in main:
                added.append((deepcopy(row), "added"))
        ordered = upgraded + shared + original + added
        rows = [row for row, _ in ordered]
        kinds = [kind for _, kind in ordered]
        rows.extend([None] * (self.MAX_SKILLS - len(rows)))
        kinds.extend(["original"] * (self.MAX_SKILLS - len(kinds)))
        return rows, kinds
