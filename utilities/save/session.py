from dataclasses import dataclass, field

from utilities.dungeon import DungeonMap
from utilities.inventory import DungeonInventory


@dataclass
class GameSession:
    """한 번의 던전 진행에 속하는 모델만 소유한다."""

    inventory: DungeonInventory
    floors: dict[int, DungeonMap] = field(default_factory=dict)
    current_floor: int = 1
