from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from items import Equip, ItemInstance, SkilledEquip
from skills import SkillInstance

from .item_inventory import ItemInventory
from units.unit_base import UnitBase

if TYPE_CHECKING:
    from units import Player


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

    EQUIPMENT_SLOTS_BY_TYPE: ClassVar[dict[str, tuple[str, ...]]] = {
        Equip.TYPE_WEAPON: ("weapon",),
        Equip.TYPE_SUB_WEAPON: ("sub_weapon",),
        Equip.TYPE_ARMOR: ("armor",),
        Equip.TYPE_ACCESSORY: ("accessory_1", "accessory_2"),
    }
    EQUIPMENT_SLOTS: ClassVar[tuple[str, ...]] = (
        "weapon",
        "sub_weapon",
        "armor",
        "accessory_1",
        "accessory_2",
    )

    def add_item(self, item_instance: ItemInstance):
        return self.item_inventory.add_item(item_instance)

    def remove_item(self, item_instance: ItemInstance):
        return self.item_inventory.remove_item(item_instance)

    def equip_item(self, item_instance: ItemInstance, player: Player) -> bool:
        item_index = self.item_inventory.find_item_index(item_instance)
        if item_index is None:
            return False

        equipment = item_instance.item
        if not isinstance(equipment, Equip):
            return False

        slot_names = self.EQUIPMENT_SLOTS_BY_TYPE.get(equipment.type)
        if slot_names is None:
            return False

        slot_name = next(
            (
                candidate
                for candidate in slot_names
                if getattr(self, candidate) is None
            ),
            slot_names[0],
        )

        equipped_instance = getattr(self, slot_name)
        equipped_item = (
            equipped_instance.item
            if equipped_instance is not None
            else None
        )
        if not equipment.equipcheck(player, equipped_item):
            return False

        if equipped_instance is None:
            self.item_inventory.items.pop(item_index)
        else:
            self.item_inventory.items[item_index] = equipped_instance
        setattr(self, slot_name, item_instance)
        return True

    def unequip_item(self, slot_name: str, player: Player) -> bool:
        if slot_name not in self.EQUIPMENT_SLOTS:
            return False

        equipped_instance = getattr(self, slot_name)
        equipment = (
            equipped_instance.item
            if equipped_instance is not None
            else None
        )
        if equipment is None or not equipment.unequipcheck(player):
            return False
        if not self.item_inventory.add_item(equipped_instance):
            return False

        setattr(self, slot_name, None)
        return True

    def assign_hotbar_item(self, label: str, item_instance: ItemInstance) -> bool:
        if not self.item_inventory.contains(item_instance):
            return False

        self.hotbar_items[label] = item_instance
        return True

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
