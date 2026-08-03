from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from items import ItemInstance


@dataclass
class ItemInventory:
    """정해진 개수만큼 아이템을 보관하는 인벤토리."""

    DEFAULT_CAPACITY: ClassVar[int] = 20

    capacity: int = DEFAULT_CAPACITY
    items: list[ItemInstance] = field(default_factory=list)

    def __post_init__(self):
        if self.capacity < 0:
            raise ValueError("capacity는 0 이상이어야 합니다.")
        if len(self.items) > self.capacity:
            raise ValueError("아이템 수가 capacity를 초과했습니다.")

    @property
    def is_full(self):
        return len(self.items) >= self.capacity

    def find_item_index(self, item: ItemInstance) -> int | None:
        for index, owned_item in enumerate(self.items):
            if owned_item is item:
                return index

        return None

    def contains(self, item: ItemInstance) -> bool:
        return self.find_item_index(item) is not None

    def add_item(self, item: ItemInstance):
        if self.is_full or self.contains(item):
            return False

        self.items.append(item)
        return True

    def remove_item(self, item: ItemInstance):
        item_index = self.find_item_index(item)
        if item_index is None:
            return False

        self.items.pop(item_index)
        return True

    def remove_amount(self, item: ItemInstance, amount: int):
        item_index = self.find_item_index(item)
        if item_index is None:
            return False
        if amount < 1 or amount > item.stack:
            return False

        item.stack -= amount
        if item.stack == 0:
            self.items.pop(item_index)

        return True
