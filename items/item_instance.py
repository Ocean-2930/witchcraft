from __future__ import annotations

from dataclasses import dataclass

from .item import Item


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
