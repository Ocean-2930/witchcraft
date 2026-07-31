from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from items import ItemInstance, SkilledEquip
from skills import SkillInstance

from .item_inventory import ItemInventory
from ..unit_base import UnitBase


@dataclass
class DungeonInventory:
    """던전행 한 번에 사용되는 플레이어 인벤토리."""

    unit_base: UnitBase | None = None
    item_inventory: ItemInventory = field(default_factory=ItemInventory)
    hotbar_items: dict[str, ItemInstance] = field(default_factory=dict)
    weapon: ItemInstance | None = None
    sub_weapon: ItemInstance | None = None
    armor: ItemInstance | None = None
    accessory_1: ItemInstance | None = None
    accessory_2: ItemInstance | None = None

    def add_item(self, item_instance: ItemInstance):
        return self.item_inventory.add_item(item_instance)

    def remove_item(self, item_instance: ItemInstance):
        return self.item_inventory.remove_item(item_instance)

    def get_hotbar_item(self, label: str) -> ItemInstance | None:
        item_instance = self.hotbar_items.get(label)
        if (
            item_instance is not None
            and all(
                owned_item is not item_instance
                for owned_item in self.item_inventory.items
            )
        ):
            self.hotbar_items.pop(label, None)
            return None

        return item_instance

    def get_stat(self):
        if self.unit_base is None:
            raise ValueError("스탯을 계산할 UnitBase가 없습니다.")

        calculated_stat = deepcopy(self.unit_base)

        for skill_instance in self.passive_skills():
            for effect in skill_instance.skill.effects:
                if effect.is_active_effect:
                    continue

                apply_passive = getattr(effect, "apply_passive", None)
                if apply_passive is None:
                    continue

                result = apply_passive(
                    calculated_stat,
                    level=skill_instance.level,
                    stack=skill_instance.stack,
                )
                if isinstance(result, UnitBase):
                    calculated_stat = result

        return calculated_stat

    def active_skills(self):
        return self._stack_skills(
            skill_instance
            for skill_instance in self._all_skill_instances()
            if any(
                effect.is_active_effect
                for effect in skill_instance.skill.effects
            )
        )

    def passive_skills(self):
        return self._stack_skills(
            skill_instance
            for skill_instance in self._all_skill_instances()
            if not any(
                effect.is_active_effect
                for effect in skill_instance.skill.effects
            )
        )

    def _all_skill_instances(self):
        if self.unit_base is not None:
            yield from self.unit_base.skill_tree.skills

        for equipment in (
            self.weapon,
            self.sub_weapon,
            self.armor,
            self.accessory_1,
            self.accessory_2,
        ):
            if (
                equipment is not None
                and isinstance(equipment.item, SkilledEquip)
            ):
                yield from equipment.item.skills

    @staticmethod
    def _stack_skills(skill_instances):
        stacked_skills: dict[str, SkillInstance] = {}

        for skill_instance in skill_instances:
            skill_code = skill_instance.skill.skill_code
            stacked_skill = stacked_skills.get(skill_code)

            if stacked_skill is None:
                stacked_skills[skill_code] = SkillInstance(
                    skill=skill_instance.skill,
                    level=skill_instance.level,
                    stack=skill_instance.stack,
                )
                continue

            if skill_instance.level > stacked_skill.level:
                stacked_skill.skill = skill_instance.skill
                stacked_skill.level = skill_instance.level
            stacked_skill.stack += skill_instance.stack

        return list(stacked_skills.values())
