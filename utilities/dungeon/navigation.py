from __future__ import annotations

from collections import deque
from typing import Iterable, Sequence, TypeAlias

from .map_generator import WALL


Position: TypeAlias = tuple[int, int]

NEIGHBOR_OFFSETS: tuple[Position, ...] = (
    (0, -1),
    (-1, 0),
    (1, 0),
    (0, 1),
    (-1, -1),
    (1, -1),
    (-1, 1),
    (1, 1),
)


def find_shortest_path(
    map_tiles: Sequence[Sequence[int]],
    start: Position,
    goal: Position,
    blocked_positions: Iterable[Position] = (),
) -> list[Position]:
    """8방향 최단 경로를 시작점을 제외하고 목적지를 포함해 반환한다."""
    if start == goal:
        return []

    blocked = set(blocked_positions)
    blocked.discard(start)
    if not _is_walkable(map_tiles, goal, blocked):
        return []

    previous: dict[Position, Position | None] = {start: None}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in _neighbors(map_tiles, current, blocked):
            if neighbor in previous:
                continue
            previous[neighbor] = current
            if neighbor == goal:
                return _reconstruct_path(previous, goal)
            queue.append(neighbor)

    return []


def _neighbors(
    map_tiles: Sequence[Sequence[int]],
    position: Position,
    blocked: set[Position],
):
    x, y = position
    for offset_x, offset_y in NEIGHBOR_OFFSETS:
        neighbor = (x + offset_x, y + offset_y)
        if not _is_walkable(map_tiles, neighbor, blocked):
            continue

        if offset_x and offset_y:
            side_x = (x + offset_x, y)
            side_y = (x, y + offset_y)
            if not _is_walkable(map_tiles, side_x, blocked) and not _is_walkable(
                map_tiles, side_y, blocked
            ):
                continue

        yield neighbor


def _is_walkable(
    map_tiles: Sequence[Sequence[int]],
    position: Position,
    blocked: set[Position],
) -> bool:
    x, y = position
    return (
        0 <= y < len(map_tiles)
        and 0 <= x < len(map_tiles[y])
        and map_tiles[y][x] != WALL
        and position not in blocked
    )


def _reconstruct_path(
    previous: dict[Position, Position | None],
    goal: Position,
) -> list[Position]:
    path = []
    current: Position | None = goal
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path[1:]
