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

    def add_item(self, item: ItemInstance):
        if self.is_full:
            return False

        self.items.append(item)
        return True

    def remove_item(self, item: ItemInstance):
        if item not in self.items:
            return False

        self.items.remove(item)
        return True

    def remove_amount(self, item: ItemInstance, amount: int):
        if item not in self.items:
            return False
        if amount < 1 or amount > item.stack:
            return False

        item.stack -= amount
        if item.stack == 0:
            self.items.remove(item)

        return True
