from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .equip import Equip
from .item import Item
from .skilled_equip import SkilledEquip


@dataclass
class ItemInstance:
    """실제로 보유 중인 아이템과 현재 스택 수."""

    item: Item
    stack: int = 1

    def __post_init__(self):
        if not 1 <= self.stack <= self.item.max_stack:
            raise ValueError(
                f"stack은 1 이상 {self.item.max_stack} 이하여야 합니다."
            )

    @property
    def max_stack(self):
        return self.item.max_stack

    def get_detail_rows(self) -> list[tuple[str, str]]:
        return self.item.get_detail_rows()


@dataclass
class EquipmentInstance(ItemInstance):
    """드롭 이후의 장비별 스탯 행을 소유하는 인스턴스."""

    item: Equip
    stat_rows: list | None = None

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.item, Equip):
            raise TypeError("EquipmentInstance에는 Equip만 넣을 수 있습니다.")

        if self.stat_rows is None:
            rows = self.item.get_drop_stat_rows()
        else:
            rows = self.stat_rows
        self.stat_rows = deepcopy(rows)

        if (
            isinstance(self.item, SkilledEquip)
            and len(self.stat_rows) != self.item.MAX_SKILLS
        ):
            raise ValueError(
                f"스킬 장비의 stat_rows는 {self.item.MAX_SKILLS}행이어야 합니다."
            )

    def skill_instances(self):
        return [row for row in self.stat_rows if row is not None]

    def synthesis_preview(self, material):
        if material is self:
            raise ValueError("메인 장비는 재료로 선택할 수 없습니다.")
        if not isinstance(material, EquipmentInstance) or not isinstance(self.item, SkilledEquip):
            raise ValueError("스킬 장비만 합성할 수 있습니다.")
        rows, kinds = self.item.synthesize_rows(
            material.item, self.stat_rows, material.stat_rows
        )
        return EquipmentInstance(deepcopy(self.item), stat_rows=rows), kinds

    def synthesis_cost(self, kinds) -> int:
        """합성 결과의 행 분류로 필요한 조화석 수를 계산한다."""
        total = 0
        for row, kind in zip(self.stat_rows, kinds):
            if row is None:
                continue
            if kind == "upgraded":
                total += row.level ** 2
            elif kind == "lower":
                total += 1
            elif kind == "added":
                total += max(0, row.level)
        return total

    def get_detail_rows(self) -> list[tuple[str, str]]:
        return [
            (row.skill.name, f"Lv.{row.level}")
            if row is not None
            else ("-", "Lv.-")
            for row in self.stat_rows
        ]
