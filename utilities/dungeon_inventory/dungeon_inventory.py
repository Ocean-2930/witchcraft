from __future__ import annotations

from dataclasses import dataclass, field

from items import Equip, ItemInstance, SkilledEquip, SubWeapon

from .item_inventory import ItemInventory
from .unit_base import UnitBase


@dataclass
class DungeonInventory:
    """던전행 한 번에 사용되는 플레이어 인벤토리."""

    unit_base: UnitBase | None = None
    item_inventory: ItemInventory = field(default_factory=ItemInventory)
    weapon: ItemInstance = field(
        default_factory=lambda: ItemInstance(SkilledEquip(Equip.TYPE_WEAPON))
    )
    sub_weapon: ItemInstance = field(
        default_factory=lambda: ItemInstance(SubWeapon(Equip.TYPE_SUB_WEAPON))
    )
    armor: ItemInstance = field(
        default_factory=lambda: ItemInstance(SkilledEquip(Equip.TYPE_ARMOR))
    )
    accessory_1: ItemInstance = field(
        default_factory=lambda: ItemInstance(SkilledEquip(Equip.TYPE_ACCESSORY))
    )
    accessory_2: ItemInstance = field(
        default_factory=lambda: ItemInstance(SkilledEquip(Equip.TYPE_ACCESSORY))
    )

    def add_item(self, item_instance: ItemInstance):
        return self.item_inventory.add_item(item_instance)

    def remove_item(self, item_instance: ItemInstance):
        return self.item_inventory.remove_item(item_instance)
