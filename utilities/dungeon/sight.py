from __future__ import annotations

from typing import Iterable, Sequence

from .map_generator import Room, WALL
from .navigation import Position


def get_visible_tiles(
    map_tiles: Sequence[Sequence[int]],
    origin: Position,
    rooms: Iterable[Room] = (),
    radius: int = 4,
) -> set[Position]:
    """반경 시야와 현재 방 전체를 합쳐 보이는 던전 타일을 반환한다."""
    wall_positions = _wall_positions(map_tiles)
    origin_x, origin_y = origin
    visible = set()

    for tile_y in range(max(0, origin_y - radius), min(len(map_tiles), origin_y + radius + 1)):
        row = map_tiles[tile_y]
        for tile_x in range(max(0, origin_x - radius), min(len(row), origin_x + radius + 1)):
            target = (tile_x, tile_y)
            if has_line_of_sight(origin, target, wall_positions):
                visible.add(target)

    room = next((room for room in rooms if room.contains(origin)), None)
    if room is not None:
        for tile_y in range(max(0, room.top - 1), min(len(map_tiles), room.bottom + 2)):
            row = map_tiles[tile_y]
            for tile_x in range(max(0, room.left - 1), min(len(row), room.right + 2)):
                position = (tile_x, tile_y)
                if room.contains(position) or row[tile_x] == WALL:
                    visible.add(position)

    _add_adjacent_walls(visible, wall_positions)
    return visible


def has_line_of_sight(
    origin: Position,
    target: Position,
    wall_positions: set[Position],
) -> bool:
    line = get_grid_line(origin, target)
    previous = line[0]

    for position in line[1:]:
        move_x = position[0] - previous[0]
        move_y = position[1] - previous[1]
        if position == target and position in wall_positions:
            return True
        if move_x and move_y:
            side_x = (previous[0] + move_x, previous[1])
            side_y = (previous[0], previous[1] + move_y)
            if side_x in wall_positions and side_y in wall_positions:
                return False
        if position == target:
            return True
        if position in wall_positions:
            return False
        previous = position

    return True


def get_grid_line(origin: Position, target: Position) -> list[Position]:
    x, y = origin
    target_x, target_y = target
    width = abs(target_x - x)
    height = abs(target_y - y)
    step_x = 1 if target_x > x else -1
    step_y = 1 if target_y > y else -1
    moved_x = moved_y = 0
    positions = [(x, y)]

    while moved_x < width or moved_y < height:
        decision = (1 + 2 * moved_x) * height - (1 + 2 * moved_y) * width
        if decision == 0:
            x += step_x
            y += step_y
            moved_x += 1
            moved_y += 1
        elif decision < 0:
            x += step_x
            moved_x += 1
        else:
            y += step_y
            moved_y += 1
        positions.append((x, y))

    return positions


def _wall_positions(map_tiles: Sequence[Sequence[int]]) -> set[Position]:
    return {
        (tile_x, tile_y)
        for tile_y, row in enumerate(map_tiles)
        for tile_x, value in enumerate(row)
        if value == WALL
    }


def _add_adjacent_walls(
    visible: set[Position],
    wall_positions: set[Position],
) -> None:
    offsets = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
    floor_positions = (position for position in tuple(visible) if position not in wall_positions)
    for tile_x, tile_y in floor_positions:
        for offset_x, offset_y in offsets:
            wall = (tile_x + offset_x, tile_y + offset_y)
            if wall in wall_positions:
                visible.add(wall)
