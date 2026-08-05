from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ..random_generator import RandomGenerator
from .map_generator import FLOOR


Position = tuple[int, int]


@dataclass(frozen=True)
class MonsterSpawnConfig:
    initial_minimum: int = 3
    initial_maximum: int = 5
    periodic_chance: float = 0.15
    maximum_alive: int = 10

    def validate(self) -> None:
        if self.initial_minimum < 0:
            raise ValueError("초기 몬스터 최솟값은 0 이상이어야 합니다.")
        if self.initial_maximum < self.initial_minimum:
            raise ValueError("초기 몬스터 최댓값은 최솟값 이상이어야 합니다.")
        if not 0.0 <= self.periodic_chance <= 1.0:
            raise ValueError("주기 소환 확률은 0과 1 사이여야 합니다.")
        if self.maximum_alive < 1:
            raise ValueError("생존 몬스터 상한은 1 이상이어야 합니다.")


class MonsterSpawner:
    """적 전용 난수 흐름으로 몬스터 소환 위치를 결정한다."""

    def __init__(
        self,
        map_tiles: Sequence[Sequence[int]],
        random_generator: RandomGenerator,
        config: MonsterSpawnConfig | None = None,
    ) -> None:
        self.map_tiles = map_tiles
        self.random = random_generator
        self.config = config or MonsterSpawnConfig()
        self.config.validate()

    def initial_positions(self, excluded_positions: Iterable[Position]) -> list[Position]:
        requested_count = self.random.randint(
            self.config.initial_minimum,
            self.config.initial_maximum,
        )
        candidates = self._available_positions(excluded_positions)
        return self._take_random_positions(candidates, requested_count)

    def periodic_positions(
        self,
        completed_turns: int,
        excluded_positions: Iterable[Position],
        alive_count: int,
    ) -> list[Position]:
        if completed_turns < 0:
            raise ValueError("완료된 턴 수는 0 이상이어야 합니다.")
        if alive_count < 0:
            raise ValueError("생존 몬스터 수는 0 이상이어야 합니다.")

        candidates = self._available_positions(excluded_positions)
        selected: list[Position] = []

        for _ in range(completed_turns):
            if alive_count + len(selected) >= self.config.maximum_alive:
                break
            if self.random.random() >= self.config.periodic_chance:
                continue
            if not candidates:
                continue

            position = self.random.choice(candidates)
            candidates.remove(position)
            selected.append(position)

        return selected

    def _available_positions(self, excluded_positions: Iterable[Position]) -> list[Position]:
        excluded = set(excluded_positions)
        return [
            (tile_x, tile_y)
            for tile_y, row in enumerate(self.map_tiles)
            for tile_x, tile_value in enumerate(row)
            if tile_value == FLOOR and (tile_x, tile_y) not in excluded
        ]

    def _take_random_positions(
        self,
        candidates: list[Position],
        count: int,
    ) -> list[Position]:
        selected: list[Position] = []
        for _ in range(min(count, len(candidates))):
            position = self.random.choice(candidates)
            candidates.remove(position)
            selected.append(position)
        return selected
