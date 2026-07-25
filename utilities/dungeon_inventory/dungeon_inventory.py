from __future__ import annotations

from dataclasses import dataclass, field

from items import ItemInstance

from .item_inventory import ItemInventory
from .unit_base import UnitBase


@dataclass
class DungeonInventory:
    """던전행 한 번에 사용되는 플레이어 인벤토리."""

    unit_base: UnitBase | None = None
    item_inventory: ItemInventory = field(default_factory=ItemInventory)

    def add_item(self, item_instance: ItemInstance):
        return self.item_inventory.add_item(item_instance)

    def remove_item(self, item_instance: ItemInstance):
        return self.item_inventory.remove_item(item_instance)
