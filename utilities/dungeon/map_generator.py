from __future__ import annotations

from collections import deque
from dataclasses import dataclass, replace
from itertools import combinations

from ..random_generator import RandomGenerator, RandomSeed


FLOOR = 0
WALL = 1
UP_STAIRS = 2
DOWN_STAIRS = 3

Position = tuple[int, int]
CorridorEdge = tuple[str, int, int]
Side = str
SIDES: tuple[Side, ...] = ("top", "right", "bottom", "left")


@dataclass(frozen=True)
class Room:
    room_id: int
    x: int
    y: int
    width: int
    height: int

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.width - 1

    @property
    def top(self) -> int:
        return self.y

    @property
    def bottom(self) -> int:
        return self.y + self.height - 1

    @property
    def center(self) -> Position:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def is_large(self) -> bool:
        return self.width >= 5 and self.height >= 5

    def contains(self, position: Position) -> bool:
        x, y = position
        return self.left <= x <= self.right and self.top <= y <= self.bottom


@dataclass(frozen=True)
class MapConnection:
    room_a: int
    room_b: int
    side_a: Side
    side_b: Side
    path: tuple[Position, ...]


@dataclass(frozen=True)
class DungeonMapConfig:
    min_rooms: int = 8
    max_rooms: int = 12
    min_room_gap: int = 3
    max_room_gap: int = 10
    min_large_rooms: int = 5
    placement_attempts: int = 240
    generation_attempts: int = 12
    extra_connection_chance: float = 0.28
    outer_wall_padding: int = 2

    def validate(self) -> None:
        if self.min_rooms < 7 or self.max_rooms < self.min_rooms:
            raise ValueError("방 개수는 최소 7개이며 최댓값은 최솟값 이상이어야 합니다.")
        if self.min_large_rooms < 5 or self.min_large_rooms > self.min_rooms:
            raise ValueError("큰 방은 최소 5개이고 전체 최소 방 수 이하여야 합니다.")
        if self.min_room_gap < 3 or self.max_room_gap < self.min_room_gap:
            raise ValueError("방 간격은 최소 3이며 최댓값은 최솟값 이상이어야 합니다.")
        if self.placement_attempts < 1 or self.generation_attempts < 1:
            raise ValueError("생성 시도 횟수는 1 이상이어야 합니다.")
        if not 0.0 <= self.extra_connection_chance <= 1.0:
            raise ValueError("추가 연결 확률은 0과 1 사이여야 합니다.")
        if self.outer_wall_padding < 2:
            raise ValueError("외곽 벽 두께는 2 이상이어야 합니다.")


@dataclass(frozen=True)
class DungeonMap:
    tiles: tuple[tuple[int, ...], ...]
    rooms: tuple[Room, ...]
    connections: tuple[MapConnection, ...]
    hub_room_id: int
    up_stairs: Position
    down_stairs: Position
    seed: RandomSeed

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    @property
    def height(self) -> int:
        return len(self.tiles)

    @property
    def map(self) -> list[list[int]]:
        """기존 scene 입력과 호환되는 복사본을 반환한다."""
        return [list(row) for row in self.tiles]


class DungeonMapGenerator:
    def __init__(
        self,
        random_generator: RandomGenerator,
        seed: RandomSeed,
        config: DungeonMapConfig | None = None,
    ) -> None:
        self.random = random_generator
        self.seed = seed
        self.config = config or DungeonMapConfig()
        self.config.validate()

    def generate(self) -> DungeonMap:
        for _ in range(self.config.generation_attempts):
            rooms = self._place_rooms()
            if rooms is None:
                continue

            connection_pairs, hub_sides = self._build_connection_graph(rooms)
            paths = self._route_connections(rooms, connection_pairs, hub_sides)
            if paths is None:
                continue
            if self._has_wide_room_opening(rooms, paths):
                continue

            floor_tiles = self._carve_floor(rooms, paths)
            stair_pair = self._find_stair_rooms(rooms, floor_tiles, hub_room_id=0)
            if stair_pair is None:
                continue

            return self._normalize(rooms, paths, floor_tiles, stair_pair)

        raise ValueError(f"seed {self.seed}로 조건을 만족하는 던전을 생성하지 못했습니다.")

    def _place_rooms(self) -> list[Room] | None:
        room_count = self.random.randint(self.config.min_rooms, self.config.max_rooms)
        sizes = [self._large_room_size() for _ in range(self.config.min_large_rooms)]
        sizes.extend(self._room_size() for _ in range(room_count - len(sizes)))
        remaining_sizes = sizes[1:]
        self.random.shuffle(remaining_sizes)
        sizes = [sizes[0], *remaining_sizes]

        hub_width, hub_height = sizes[0]
        rooms = [Room(0, 0, 0, hub_width, hub_height)]

        hub_sides = list(SIDES)
        self.random.shuffle(hub_sides)
        branch_count = self.random.randint(3, 4)
        for side in hub_sides[:branch_count]:
            if not sizes[1:]:
                return None
            size = sizes[len(rooms)]
            room = self._place_next_to_anchor(rooms, rooms[0], size, side)
            if room is None:
                return None
            rooms.append(room)

        while len(rooms) < room_count:
            size = sizes[len(rooms)]
            room = None
            for _ in range(self.config.placement_attempts):
                anchor = self.random.choice(rooms)
                side = self.random.choice(SIDES)
                room = self._candidate_room(len(rooms), anchor, size, side)
                if self._valid_room(room, rooms):
                    break
                room = None
            if room is None:
                return None
            rooms.append(room)

        return rooms

    def _place_next_to_anchor(
        self,
        rooms: list[Room],
        anchor: Room,
        size: tuple[int, int],
        side: Side,
    ) -> Room | None:
        for _ in range(self.config.placement_attempts):
            candidate = self._candidate_room(len(rooms), anchor, size, side)
            if self._valid_room(candidate, rooms):
                return candidate
        return None

    def _candidate_room(
        self,
        room_id: int,
        anchor: Room,
        size: tuple[int, int],
        side: Side,
    ) -> Room:
        width, height = size
        gap = self.random.randint(self.config.min_room_gap, self.config.max_room_gap)
        if side == "top":
            x = self.random.randint(anchor.left - width + 1, anchor.right)
            y = anchor.top - gap - height
        elif side == "right":
            x = anchor.right + gap + 1
            y = self.random.randint(anchor.top - height + 1, anchor.bottom)
        elif side == "bottom":
            x = self.random.randint(anchor.left - width + 1, anchor.right)
            y = anchor.bottom + gap + 1
        else:
            x = anchor.left - gap - width
            y = self.random.randint(anchor.top - height + 1, anchor.bottom)
        return Room(room_id, x, y, width, height)

    def _valid_room(self, candidate: Room, rooms: list[Room]) -> bool:
        distances = [self.room_distance(candidate, room) for room in rooms]
        return min(distances) >= self.config.min_room_gap and min(distances) <= self.config.max_room_gap

    @staticmethod
    def room_distance(room_a: Room, room_b: Room) -> int:
        gap_x = max(room_b.left - room_a.right - 1, room_a.left - room_b.right - 1, 0)
        gap_y = max(room_b.top - room_a.bottom - 1, room_a.top - room_b.bottom - 1, 0)
        return gap_x + gap_y

    def _large_room_size(self) -> tuple[int, int]:
        return (self.random.randint(5, 8), self.random.randint(5, 8))

    def _room_size(self) -> tuple[int, int]:
        if self.random.random() < 0.35:
            return self._large_room_size()
        if self.random.random() < 0.5:
            return (self.random.randint(2, 3), self.random.randint(4, 8))
        return (self.random.randint(4, 8), self.random.randint(2, 8))

    def _build_connection_graph(
        self, rooms: list[Room]
    ) -> tuple[list[tuple[int, int]], dict[tuple[int, int], Side]]:
        hub_sides: dict[tuple[int, int], Side] = {}
        pairs: list[tuple[int, int]] = []

        side_candidates: dict[Side, list[int]] = {side: [] for side in SIDES}
        hub = rooms[0]
        for room in rooms[1:]:
            side_candidates[self._relative_side(hub, room)].append(room.room_id)

        available_sides = [side for side, ids in side_candidates.items() if ids]
        self.random.shuffle(available_sides)
        required_sides = available_sides[: min(4, len(available_sides))]
        if len(required_sides) < 3:
            return ([], {})

        for side in required_sides:
            room_id = min(
                side_candidates[side],
                key=lambda value: self.room_distance(hub, rooms[value]),
            )
            pair = (0, room_id)
            pairs.append(pair)
            hub_sides[pair] = side

        parent = list(range(len(rooms)))

        def find(value: int) -> int:
            while parent[value] != value:
                parent[value] = parent[parent[value]]
                value = parent[value]
            return value

        def union(a: int, b: int) -> bool:
            root_a, root_b = find(a), find(b)
            if root_a == root_b:
                return False
            parent[root_b] = root_a
            return True

        for a, b in pairs:
            union(a, b)

        edges = sorted(
            combinations(range(len(rooms)), 2),
            key=lambda pair: (
                self.room_distance(rooms[pair[0]], rooms[pair[1]]),
                pair[0],
                pair[1],
            ),
        )
        for a, b in edges:
            pair = (a, b)
            if pair in pairs:
                continue
            if union(a, b):
                pairs.append(pair)

        extra_candidates = [edge for edge in edges if edge not in pairs]
        self.random.shuffle(extra_candidates)
        added_extra = False
        for pair in extra_candidates:
            if not added_extra or self.random.random() < self.config.extra_connection_chance:
                pairs.append(pair)
                added_extra = True
            if added_extra and len(pairs) >= len(rooms) + 1:
                break

        return (pairs, hub_sides)

    def _route_connections(
        self,
        rooms: list[Room],
        pairs: list[tuple[int, int]],
        hub_sides: dict[tuple[int, int], Side],
    ) -> list[MapConnection] | None:
        if not pairs:
            return None
        connections: list[MapConnection] = []
        corridor_edges: set[CorridorEdge] = set()
        for room_a_id, room_b_id in pairs:
            room_a, room_b = rooms[room_a_id], rooms[room_b_id]
            side_a = hub_sides.get((room_a_id, room_b_id)) or self._relative_side(room_a, room_b)
            side_b = self._opposite_side(side_a)
            start_door = self._door_position(room_a, side_a)
            end_door = self._door_position(room_b, side_b)
            start = self._move_to_outside(start_door, side_a)
            end = self._move_to_outside(end_door, side_b)
            allowed_contacts = {room_a_id: start, room_b_id: end}
            outside_path = self._find_corridor_path(
                start,
                end,
                rooms,
                allowed_contacts,
                corridor_edges,
            )
            if outside_path is None:
                return None
            path = (start_door, *outside_path, end_door)
            connections.append(MapConnection(room_a_id, room_b_id, side_a, side_b, path))
            corridor_edges.update(self._path_edges(path))
        return connections

    def _find_corridor_path(
        self,
        start: Position,
        end: Position,
        rooms: list[Room],
        allowed_contacts: dict[int, Position],
        corridor_edges: set[CorridorEdge],
    ) -> list[Position] | None:
        variants = self._corridor_variants(start, end)
        self.random.shuffle(variants)
        for waypoints in variants:
            path = self._expand_waypoints(waypoints)
            if (
                not self._touches_room_buffer(path, rooms, allowed_contacts)
                and not self._has_adjacent_parallel_edge(path, corridor_edges)
            ):
                return path
        return self._route_around_rooms(
            start,
            end,
            rooms,
            allowed_contacts,
            corridor_edges,
        )

    def _corridor_variants(self, start: Position, end: Position) -> list[list[Position]]:
        start_x, start_y = start
        end_x, end_y = end
        mid_x = (start_x + end_x) // 2
        mid_y = (start_y + end_y) // 2
        return [
            [start, (end_x, start_y), end],
            [start, (start_x, end_y), end],
            [start, (mid_x, start_y), (mid_x, end_y), end],
            [start, (start_x, mid_y), (end_x, mid_y), end],
        ]

    @staticmethod
    def _expand_waypoints(waypoints: list[Position]) -> list[Position]:
        path = [waypoints[0]]
        for target_x, target_y in waypoints[1:]:
            x, y = path[-1]
            while x != target_x:
                x += 1 if target_x > x else -1
                path.append((x, y))
            while y != target_y:
                y += 1 if target_y > y else -1
                path.append((x, y))
        return path

    @staticmethod
    def _touches_room_buffer(
        path: list[Position], rooms: list[Room], allowed_contacts: dict[int, Position]
    ) -> bool:
        return any(
            position != allowed_contacts.get(room.room_id)
            and DungeonMapGenerator._is_in_room_buffer(position, room)
            for room in rooms
            for position in path
        )

    @staticmethod
    def _is_in_room_buffer(position: Position, room: Room) -> bool:
        x, y = position
        return (
            room.left - 1 <= x <= room.right + 1
            and room.top - 1 <= y <= room.bottom + 1
        )

    @staticmethod
    def _has_adjacent_parallel_edge(
        path: list[Position], corridor_edges: set[CorridorEdge]
    ) -> bool:
        for orientation, x, y in DungeonMapGenerator._path_edges(path):
            if orientation == "horizontal":
                adjacent_edges = (
                    (orientation, x, y - 1),
                    (orientation, x, y + 1),
                )
            else:
                adjacent_edges = (
                    (orientation, x - 1, y),
                    (orientation, x + 1, y),
                )
            if any(edge in corridor_edges for edge in adjacent_edges):
                return True
        return False

    @staticmethod
    def _path_edges(path: list[Position] | tuple[Position, ...]) -> set[CorridorEdge]:
        edges = set()
        for start, end in zip(path, path[1:]):
            if start[1] == end[1]:
                edges.add(("horizontal", min(start[0], end[0]), start[1]))
            else:
                edges.add(("vertical", start[0], min(start[1], end[1])))
        return edges

    @staticmethod
    def _has_wide_room_opening(
        rooms: list[Room], connections: list[MapConnection]
    ) -> bool:
        corridor_tiles = {
            position
            for connection in connections
            for position in connection.path
        }
        for room in rooms:
            wall_contacts = (
                [
                    (x, room.top - 1)
                    for x in range(room.left, room.right + 1)
                ],
                [
                    (room.right + 1, y)
                    for y in range(room.top, room.bottom + 1)
                ],
                [
                    (x, room.bottom + 1)
                    for x in range(room.left, room.right + 1)
                ],
                [
                    (room.left - 1, y)
                    for y in range(room.top, room.bottom + 1)
                ],
            )
            for contacts in wall_contacts:
                previous_is_open = False
                for position in contacts:
                    is_open = position in corridor_tiles
                    if previous_is_open and is_open:
                        return True
                    previous_is_open = is_open
        return False

    def _route_around_rooms(
        self,
        start: Position,
        end: Position,
        rooms: list[Room],
        allowed_contacts: dict[int, Position],
        corridor_edges: set[CorridorEdge],
    ) -> list[Position] | None:
        margin = self.config.max_room_gap + 4
        min_x = min(room.left for room in rooms) - margin
        max_x = max(room.right for room in rooms) + margin
        min_y = min(room.top for room in rooms) - margin
        max_y = max(room.bottom for room in rooms) + margin
        blocked = {
            (x, y)
            for room in rooms
            for y in range(room.top - 1, room.bottom + 2)
            for x in range(room.left - 1, room.right + 2)
            if self._is_in_room_buffer((x, y), room)
            and (x, y) != allowed_contacts.get(room.room_id)
        }
        queue = deque([start])
        previous: dict[Position, Position | None] = {start: None}
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.random.shuffle(directions)
        while queue:
            current = queue.popleft()
            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = previous[current]
                return list(reversed(path))
            for dx, dy in directions:
                next_position = (current[0] + dx, current[1] + dy)
                if not (min_x <= next_position[0] <= max_x and min_y <= next_position[1] <= max_y):
                    continue
                if next_position in blocked or next_position in previous:
                    continue
                if self._has_adjacent_parallel_edge(
                    [current, next_position], corridor_edges
                ):
                    continue
                previous[next_position] = current
                queue.append(next_position)
        return None

    @staticmethod
    def _relative_side(room_a: Room, room_b: Room) -> Side:
        dx = room_b.center[0] - room_a.center[0]
        dy = room_b.center[1] - room_a.center[1]
        if abs(dx) >= abs(dy):
            return "right" if dx >= 0 else "left"
        return "bottom" if dy >= 0 else "top"

    @staticmethod
    def _opposite_side(side: Side) -> Side:
        return {"top": "bottom", "right": "left", "bottom": "top", "left": "right"}[side]

    def _door_position(self, room: Room, side: Side) -> Position:
        if side in ("top", "bottom"):
            x = self.random.randint(room.left, room.right)
            return (x, room.top if side == "top" else room.bottom)
        y = self.random.randint(room.top, room.bottom)
        return (room.left if side == "left" else room.right, y)

    @staticmethod
    def _move_to_outside(position: Position, side: Side) -> Position:
        offset_x, offset_y = {
            "top": (0, -1),
            "right": (1, 0),
            "bottom": (0, 1),
            "left": (-1, 0),
        }[side]
        return (position[0] + offset_x, position[1] + offset_y)

    @staticmethod
    def _carve_floor(rooms: list[Room], connections: list[MapConnection]) -> set[Position]:
        floor_tiles = {
            (x, y)
            for room in rooms
            for y in range(room.top, room.bottom + 1)
            for x in range(room.left, room.right + 1)
        }
        for connection in connections:
            floor_tiles.update(connection.path)
        return floor_tiles

    def _find_stair_rooms(
        self, rooms: list[Room], floor_tiles: set[Position], hub_room_id: int
    ) -> tuple[int, int] | None:
        candidates = [room for room in rooms if room.room_id != hub_room_id]
        best_pair = None
        best_distance = -1
        for room_a, room_b in combinations(candidates, 2):
            distance = self._floor_distance(room_a.center, room_b.center, floor_tiles)
            if distance is not None and distance > best_distance:
                best_distance = distance
                best_pair = (room_a.room_id, room_b.room_id)
        return best_pair

    @staticmethod
    def _floor_distance(start: Position, end: Position, floor_tiles: set[Position]) -> int | None:
        queue = deque([(start, 0)])
        visited = {start}
        while queue:
            position, distance = queue.popleft()
            if position == end:
                return distance
            x, y = position
            for next_position in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if next_position in floor_tiles and next_position not in visited:
                    visited.add(next_position)
                    queue.append((next_position, distance + 1))
        return None

    def _normalize(
        self,
        rooms: list[Room],
        connections: list[MapConnection],
        floor_tiles: set[Position],
        stair_pair: tuple[int, int],
    ) -> DungeonMap:
        padding = self.config.outer_wall_padding
        min_x = min(x for x, _ in floor_tiles) - padding
        max_x = max(x for x, _ in floor_tiles) + padding
        min_y = min(y for _, y in floor_tiles) - padding
        max_y = max(y for _, y in floor_tiles) + padding
        offset_x, offset_y = -min_x, -min_y
        width, height = max_x - min_x + 1, max_y - min_y + 1
        tiles = [[WALL for _ in range(width)] for _ in range(height)]
        for x, y in floor_tiles:
            tiles[y + offset_y][x + offset_x] = FLOOR

        normalized_rooms = tuple(
            replace(room, x=room.x + offset_x, y=room.y + offset_y) for room in rooms
        )
        normalized_connections = tuple(
            replace(
                connection,
                path=tuple((x + offset_x, y + offset_y) for x, y in connection.path),
            )
            for connection in connections
        )
        up_stairs = normalized_rooms[stair_pair[0]].center
        down_stairs = normalized_rooms[stair_pair[1]].center
        tiles[up_stairs[1]][up_stairs[0]] = UP_STAIRS
        tiles[down_stairs[1]][down_stairs[0]] = DOWN_STAIRS

        return DungeonMap(
            tiles=tuple(tuple(row) for row in tiles),
            rooms=normalized_rooms,
            connections=normalized_connections,
            hub_room_id=0,
            up_stairs=up_stairs,
            down_stairs=down_stairs,
            seed=self.seed,
        )
