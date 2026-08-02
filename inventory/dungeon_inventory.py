from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from items import Equip, ItemInstance, SkilledEquip
from skills import SkillInstance

from .item_inventory import ItemInventory
if TYPE_CHECKING:
    from units import Player
    from units.unit_base import UnitBase


@dataclass
class LearnableSkill:
    """영웅이 던전에서 배울 수 있는 티어별 스킬."""

    tier: int
    skill: SkillInstance
    max_level: int | None = None

    def __post_init__(self):
        if self.tier < 1:
            raise ValueError("tier는 1 이상이어야 합니다.")
        if self.max_level is None:
            self.max_level = self.skill.max_level
        if self.max_level is None:
            return
        if self.max_level < self.skill.level:
            raise ValueError("max_level은 현재 레벨 이상이어야 합니다.")
        if (
            self.skill.max_level is not None
            and self.max_level > self.skill.max_level
        ):
            raise ValueError(
                "max_level은 현재 레벨 이상, 스킬 정의의 최대 레벨 이하여야 합니다."
            )


@dataclass
class DungeonInventory:
    """던전행 한 번에 사용되는 플레이어 인벤토리."""

    unit_base: UnitBase | None = None
    item_inventory: ItemInventory = field(default_factory=ItemInventory)
    hotbar_items: dict[str, ItemInstance] = field(default_factory=dict)
    hotbar_skill_codes: dict[str, str] = field(default_factory=dict)
    weapon: ItemInstance | None = None
    sub_weapon: ItemInstance | None = None
    armor: ItemInstance | None = None
    accessory_1: ItemInstance | None = None
    accessory_2: ItemInstance | None = None
    learnable_skills: list[LearnableSkill] = field(default_factory=list)
    tier_skill_points: dict[int, int] = field(default_factory=dict)

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
        self.hotbar_skill_codes.pop(label, None)
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

    def assign_hotbar_skill(self, label: str, skill_code: str) -> bool:
        if not any(
            skill.skill.skill_code == skill_code
            for skill in self.active_skills()
        ):
            return False

        for assigned_label, assigned_code in tuple(
            self.hotbar_skill_codes.items()
        ):
            if assigned_code == skill_code:
                self.hotbar_skill_codes.pop(assigned_label)
        self.hotbar_skill_codes[label] = skill_code
        self.hotbar_items.pop(label, None)
        return True

    def get_hotbar_skill(self, label: str) -> SkillInstance | None:
        skill_code = self.hotbar_skill_codes.get(label)
        if skill_code is None:
            return None

        skill = next(
            (
                skill
                for skill in self.active_skills()
                if skill.skill.skill_code == skill_code
            ),
            None,
        )
        if skill is None:
            self.hotbar_skill_codes.pop(label, None)
        return skill

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
                if result is not None:
                    calculated_stat = result

        return calculated_stat

    def add_learnable_skill(self, learnable_skill: LearnableSkill) -> bool:
        if any(
            owned_skill is learnable_skill
            for owned_skill in self.learnable_skills
        ):
            return False
        self.learnable_skills.append(learnable_skill)
        self.tier_skill_points.setdefault(learnable_skill.tier, 0)
        return True

    def set_tier_skill_points(self, tier: int, points: int):
        if tier < 1 or points < 0:
            raise ValueError("tier는 1 이상, points는 0 이상이어야 합니다.")
        self.tier_skill_points[tier] = points

    def invest_skill(self, learnable_skill: LearnableSkill) -> bool:
        if not any(
            owned_skill is learnable_skill
            for owned_skill in self.learnable_skills
        ):
            return False
        if (
            learnable_skill.max_level is not None
            and learnable_skill.skill.level >= learnable_skill.max_level
        ):
            return False
        points = self.tier_skill_points.get(learnable_skill.tier, 0)
        if points < 1:
            return False
        learnable_skill.skill.level += 1
        self.tier_skill_points[learnable_skill.tier] = points - 1
        return True

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
        yield from (
            learnable_skill.skill
            for learnable_skill in self.learnable_skills
            if learnable_skill.skill.level != 0
        )

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
        skill_definitions = {}
        combined_levels: dict[str, int] = {}

        for skill_instance in skill_instances:
            skill_code = skill_instance.skill.skill_code
            skill_definitions.setdefault(skill_code, skill_instance.skill)
            combined_levels[skill_code] = (
                combined_levels.get(skill_code, 0)
                + skill_instance.level * skill_instance.stack
            )

        stacked_skills = []
        for skill_code, combined_level in combined_levels.items():
            skill = skill_definitions[skill_code]
            if skill.max_level is not None:
                combined_level = min(combined_level, skill.max_level)
            stacked_skills.append(
                SkillInstance(skill=skill, level=combined_level, stack=1)
            )

        return stacked_skills
