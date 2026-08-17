from math import ceil

import pygame
import settings

from .scene import Scene
from settings import (
    ARROW_DOWN,
    ARROW_LEFT,
    ARROW_RIGHT,
    ARROW_UP,
    ESCAPE,
    TAB,
    KEY_1,
    KEY_2,
    KEY_3,
    KEY_4,
    KEY_E,
    KEY_M,
    KEY_Q,
    KEY_R,
    KEY_T,
    KEY_W,
    VIRTUAL_HEIGHT,
    VIRTUAL_WIDTH,
)
from ui import (
    CombatLogRenderer,
    CombatTimelineRenderer,
    FloorTileRenderer,
    DungeonFogRenderer,
    MonsterMarkerRenderer,
    MiniMap,
    MonsterTooltipRenderer,
    PauseButton,
    PlayerMarkerRenderer,
    PlayerStatusRenderer,
    SkillDirectionCompassRenderer,
    StairTileRenderer,
    ShortcutBar,
    WallTileRenderer,
)
from skills import SkillDirectionStatus, SkillTargetingInput
from units import AttackResult, Enemy, EnemyMode
from utilities.dungeon import (
    CombatTimer,
    DOWN_STAIRS,
    FLOOR,
    UP_STAIRS,
    WALL,
    DungeonMap,
    MonsterSpawner,
    find_shortest_path,
    get_grid_line,
    get_visible_tiles,
    has_line_of_sight,
)
from utilities.inventory import DungeonInventory


class DungeonScene(Scene):
    COMBAT_LOG_MAX_COUNT = 6
    COMBAT_LOG_WIDTH = 420
    FLOOR_TILE_WIDTH = 90
    FLOOR_TILE_HEIGHT = 60
    WALL_TILE_HEIGHT = 80
    TILE_RENDER_BUFFER = 2
    SIGHT_RADIUS = 4
    CURRENT_FLOOR = 1
    MOVE_DURATION = 0.16
    MOVE_REPEAT_DELAY = 0.24
    MONSTER_MARKER_SIZE = 54
    DEPTH_FLOOR = 0
    DEPTH_UNIT = 1
    DEPTH_WALL = 2
    DIRECTION_LABELS = {
        (-1, 0): "왼쪽",
        (1, 0): "오른쪽",
        (0, -1): "위",
        (0, 1): "아래",
        (-1, -1): "왼쪽 위",
        (1, -1): "오른쪽 위",
        (-1, 1): "왼쪽 아래",
        (1, 1): "오른쪽 아래",
        (0, 0): "상쇄 입력",
    }
    HOTBAR_KEYS = (
        (KEY_1, "1"),
        (KEY_2, "2"),
        (KEY_3, "3"),
        (KEY_4, "4"),
        (KEY_Q, "Q"),
        (KEY_W, "W"),
        (KEY_E, "E"),
        (KEY_R, "R"),
    )
    DIRECTION_KEYS = (
        (ARROW_LEFT, (-1, 0)),
        (ARROW_RIGHT, (1, 0)),
        (ARROW_UP, (0, -1)),
        (ARROW_DOWN, (0, 1)),
    )
    DEFAULT_MAP = {
        "map": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    }

    def __init__(
        self,
        game,
        dungeon_map: DungeonMap | dict | None = None,
        dungeon_inventory: DungeonInventory | None = None,
    ):
        self.dungeon_map = dungeon_map or self.DEFAULT_MAP
        self.initial_dungeon_inventory = dungeon_inventory
        super().__init__(game)

    def scene_initialize(self):
        if isinstance(self.dungeon_map, DungeonMap):
            self.map_tiles = self.dungeon_map.map
            self.rooms = self.dungeon_map.rooms
            self.connections = self.dungeon_map.connections
            self.up_stairs = self.dungeon_map.up_stairs
            self.down_stairs = self.dungeon_map.down_stairs
        else:
            self.map_tiles = self.dungeon_map["map"]
            self.rooms = ()
            self.connections = ()
            self.up_stairs = None
            self.down_stairs = None
        self.dungeon_inventory = (
            self.initial_dungeon_inventory or DungeonInventory()
        )
        self.combat_timer = CombatTimer()
        self.combat_timer.register(self.dungeon_inventory.player)
        if self.up_stairs is not None:
            self.dungeon_inventory.set_player_position(*self.up_stairs)
        else:
            self.dungeon_inventory.set_player_position(*self.get_first_floor_position())
        self.player_status = PlayerStatusRenderer(
            self,
            self.dungeon_inventory.get_stat,
            28 + (92 + 10 + 82 + 10 + 220) // 2,
            28 + 92 // 2,
        )
        self.monsters = []
        self.enemy_random = self.dungeon_inventory.get_enemy_random_generator(self.CURRENT_FLOOR)
        self.monster_spawner = MonsterSpawner(self.map_tiles, self.enemy_random)
        self.hovered_monster = None
        self.peek_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.monster_tooltip = MonsterTooltipRenderer(
            self,
            lambda: self.hovered_monster,
            lambda unit: self.dungeon_inventory.get_stat()
            .make_damage_block(unit)
            .peek(),
            self.peek_font,
        )
        self.wall_positions = self.get_wall_positions()
        self.active_move = None
        self.held_direction = None
        self.hold_elapsed = 0.0
        self.repeat_move_enabled = False
        self.active_hotbar_label = None
        self.active_hotbar_key = None
        self.active_hotbar_direction = None
        self.active_hotbar_direction_touched = False
        self.saved_skill_direction = None
        self.movement_input_guard = False
        self.hotbar_input_guard = False
        self.last_skill_call = None
        self.combat_logs = []
        self.maze_offset_x = 0.0
        self.maze_offset_y = 0.0
        self.maze_renderers = []
        self.floor_tiles = {}
        self.stair_tiles = {}
        self.wall_tiles = {}
        self.filtered_tile_renderers = set()
        self.current_visible_tiles = set()

        if settings.ENABLE_TEST_SCENARIO:
            from .test_scenario import senario

            senario(self)

        self.refresh_visible_tiles()
        self.spawn_initial_monsters()
        self.fog_renderer = DungeonFogRenderer(
            self,
            lambda: self.floor_tiles,
            lambda: self.wall_tiles,
            lambda: self.current_visible_tiles,
        )
        self.player_marker = PlayerMarkerRenderer(
            self,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            72,
            72,
        )
        self.combat_timeline = CombatTimelineRenderer(
            self,
            self.dungeon_inventory.get_stat,
            lambda: self.combat_timer.turn_counter.value,
            self.player_status.rect.centerx,
            self.player_status.rect.bottom + 46,
            width=self.player_status.rect.width,
            enemy_turns_getter=self.get_visible_monster_turns,
        )
        player_x, player_y = self.dungeon_inventory.get_player_position()
        self.set_dungeon_draw_order(self.player_marker, player_x, player_y, self.DEPTH_UNIT)
        self.hotbar = ShortcutBar(
            self,
            labels=("1", "2", "3", "4", "Q", "W", "E", "R"),
            pos_x=28 + (72 * 4 + 8 * 3) // 2,
            pos_y=VIRTUAL_HEIGHT - 28 - (72 * 2 + 8) // 2,
            columns=4,
            slot_width=72,
            slot_height=72,
            horizontal_gap=8,
            vertical_gap=8,
            item_getter=self.dungeon_inventory.get_hotbar_item,
            skill_getter=self.get_hotbar_display_skill,
            skill_fallback_getter=self.has_equipped_hotbar_skill,
        )
        self.skill_direction_compass = SkillDirectionCompassRenderer(
            self,
            self.hotbar.rect.right + 28,
            self.hotbar.rect.centery,
            46,
            46,
            lambda: self.saved_skill_direction,
        )
        self.pause_button = PauseButton(
            self,
            VIRTUAL_WIDTH - 42,
            42,
            48,
            48,
            self.open_pause,
        )
        self.mini_map = MiniMap(
            self,
            VIRTUAL_WIDTH - 92,
            142,
            148,
            128,
            lambda: self.map_tiles,
            self.get_explored_tiles,
            self.dungeon_inventory.get_player_position,
            lambda: self.rooms,
            lambda: self.connections,
            self.open_map,
        )
        self.combat_log = CombatLogRenderer(
            self,
            lambda: self.combat_logs,
            VIRTUAL_WIDTH - 28 - self.COMBAT_LOG_WIDTH // 2,
            VIRTUAL_HEIGHT
            - 28
            - (
                CombatLogRenderer.PADDING_Y * 2
                + CombatLogRenderer.LINE_HEIGHT * self.COMBAT_LOG_MAX_COUNT
            )
            // 2,
            self.COMBAT_LOG_WIDTH,
            self.COMBAT_LOG_MAX_COUNT,
        )

    def refresh_visible_tiles(self):
        self.current_visible_tiles = self.get_sight_tile_positions()
        explored_tiles = self.dungeon_inventory.explore_tiles(
            self.CURRENT_FLOOR,
            self.current_visible_tiles,
        )
        camera_tiles = self.get_camera_tile_positions()
        render_tiles = camera_tiles & explored_tiles
        visible_walls = render_tiles & self.wall_positions

        self.remove_hidden_tiles(self.floor_tiles, render_tiles)
        self.remove_hidden_tiles(self.stair_tiles, render_tiles)
        self.remove_hidden_tiles(self.wall_tiles, visible_walls)

        for tile_x, tile_y in render_tiles:
            if (tile_x, tile_y) not in self.floor_tiles:
                self.create_floor_tile(tile_x, tile_y)

        for tile_x, tile_y in visible_walls:
            if (tile_x, tile_y) not in self.wall_tiles:
                self.create_wall_tile(tile_x, tile_y)

        self.refresh_monster_visibility()

    def get_camera_tile_positions(self):
        horizontal_radius = ceil((VIRTUAL_WIDTH / 2) / self.FLOOR_TILE_WIDTH) + self.TILE_RENDER_BUFFER
        vertical_radius = ceil((VIRTUAL_HEIGHT / 2) / self.FLOOR_TILE_HEIGHT) + self.TILE_RENDER_BUFFER
        visible_tiles = set()
        player_x, player_y = self.dungeon_inventory.get_player_position()

        start_y = max(0, player_y - vertical_radius)
        end_y = min(len(self.map_tiles), player_y + vertical_radius + 1)

        for tile_y in range(start_y, end_y):
            row = self.map_tiles[tile_y]
            start_x = max(0, player_x - horizontal_radius)
            end_x = min(len(row), player_x + horizontal_radius + 1)

            for tile_x in range(start_x, end_x):
                visible_tiles.add((tile_x, tile_y))

        return visible_tiles

    def get_sight_tile_positions(self):
        return get_visible_tiles(
            self.map_tiles,
            self.dungeon_inventory.get_player_position(),
            self.rooms,
            self.SIGHT_RADIUS,
        )

    def add_walls_next_to_visible_floor(self, visible_tiles):
        """보이는 바닥에 직접 닿은 벽만 더해 통로 윤곽을 끊김 없이 보여준다."""
        neighbor_offsets = (
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        )
        visible_floor_tiles = (
            tile_position
            for tile_position in tuple(visible_tiles)
            if tile_position not in self.wall_positions
        )

        for tile_x, tile_y in visible_floor_tiles:
            for offset_x, offset_y in neighbor_offsets:
                wall_position = (tile_x + offset_x, tile_y + offset_y)
                if wall_position in self.wall_positions:
                    visible_tiles.add(wall_position)

    def has_line_of_sight(self, origin, target):
        """목표 벽은 보이게 두되 중간 벽과 막힌 대각선 모서리는 통과하지 않는다."""
        return has_line_of_sight(origin, target, self.wall_positions)

    @staticmethod
    def get_grid_line(origin, target):
        """두 타일 중심을 잇는 정수 격자선을 반환한다."""
        return get_grid_line(origin, target)

    def get_explored_tiles(self):
        return self.dungeon_inventory.get_explored_tiles(self.CURRENT_FLOOR)

    def remove_hidden_tiles(self, tile_renderers, visible_tiles):
        for tile_position, renderer in list(tile_renderers.items()):
            if tile_position in visible_tiles:
                continue

            self.filtered_tile_renderers.discard(renderer)
            renderer.destroy()
            self.maze_renderers.remove(renderer)
            del tile_renderers[tile_position]

    def create_floor_tile(self, tile_x, tile_y):
        tile_value = self.map_tiles[tile_y][tile_x]
        tile = FloorTileRenderer(
            self,
            self.get_tile_screen_x(tile_x),
            self.get_tile_screen_y(tile_y),
            self.FLOOR_TILE_WIDTH,
            self.FLOOR_TILE_HEIGHT,
        )
        self.set_dungeon_draw_order(tile, tile_x, tile_y, self.DEPTH_FLOOR)
        self.set_maze_base_position(tile)
        self.floor_tiles[(tile_x, tile_y)] = tile
        self.maze_renderers.append(tile)

        stair_texture_key = None
        if tile_value == UP_STAIRS:
            stair_texture_key = "up_stairs"
        elif tile_value == DOWN_STAIRS:
            stair_texture_key = "down_stairs"

        if stair_texture_key is not None:
            self.create_stair_tile(tile_x, tile_y, stair_texture_key)

    def create_stair_tile(self, tile_x, tile_y, texture_key):
        stair = StairTileRenderer(
            self,
            self.get_tile_screen_x(tile_x),
            self.get_tile_screen_y(tile_y),
            self.FLOOR_TILE_WIDTH,
            self.FLOOR_TILE_HEIGHT,
            texture_key,
        )
        self.set_dungeon_draw_order(stair, tile_x, tile_y, self.DEPTH_FLOOR)
        self.set_maze_base_position(stair)
        self.stair_tiles[(tile_x, tile_y)] = stair
        self.maze_renderers.append(stair)

    def create_monster(self, tile_x, tile_y):
        unit = Enemy("적 몬스터", max_hp=100, attack_power=0, tile_x=tile_x, tile_y=tile_y)
        self.combat_timer.register(unit)
        monster = {
            "unit": unit,
            "renderer": MonsterMarkerRenderer(
                self,
                self.get_tile_screen_x(unit.tile_x),
                self.get_tile_screen_y(unit.tile_y),
                self.MONSTER_MARKER_SIZE,
                self.MONSTER_MARKER_SIZE,
                unit,
            ),
        }
        self.set_dungeon_draw_order(monster["renderer"], unit.tile_x, unit.tile_y, self.DEPTH_UNIT)
        self.set_maze_base_position(monster["renderer"])
        self.maze_renderers.append(monster["renderer"])
        self.monsters.append(monster)
        monster["renderer"].set_visible((tile_x, tile_y) in self.current_visible_tiles)
        return monster

    def spawn_initial_monsters(self):
        for tile_x, tile_y in self.monster_spawner.initial_positions(
            self.get_monster_spawn_excluded_positions()
        ):
            self.create_monster(tile_x, tile_y)

    def spawn_periodic_monsters(self, completed_turns):
        alive_count = sum(monster["unit"].is_alive for monster in self.monsters)
        for tile_x, tile_y in self.monster_spawner.periodic_positions(
            completed_turns,
            self.get_monster_spawn_excluded_positions(),
            alive_count,
        ):
            self.create_monster(tile_x, tile_y)

    def get_monster_spawn_excluded_positions(self):
        excluded_positions = set(self.current_visible_tiles)
        excluded_positions.add(self.dungeon_inventory.get_player_position())
        excluded_positions.update(
            (monster["unit"].tile_x, monster["unit"].tile_y)
            for monster in self.monsters
            if monster["unit"].is_alive
        )
        return excluded_positions

    def refresh_monster_visibility(self):
        for monster in self.monsters:
            position = (monster["unit"].tile_x, monster["unit"].tile_y)
            monster["renderer"].set_visible(position in self.current_visible_tiles)

    def get_visible_monster_turns(self):
        turns = []
        for entry in self.combat_timer.entries:
            if not isinstance(entry.unit, Enemy) or not entry.unit.is_alive:
                continue
            position = (entry.unit.tile_x, entry.unit.tile_y)
            if position in self.current_visible_tiles:
                turns.append(entry.remaining)
        return turns

    def advance_monster_turns(self, ticks):
        """플레이어 행동 시간 동안 준비되는 모든 몬스터 행동을 처리한다."""
        remaining_ticks = ticks
        completed_turns = 0

        while remaining_ticks > 0:
            pending = [
                entry.remaining
                for entry in self.combat_timer.entries
                if isinstance(entry.unit, Enemy) and entry.unit.is_alive and entry.remaining > 0
            ]
            step = min(remaining_ticks, min(pending)) if pending else remaining_ticks
            self.combat_timer.advance(step)
            completed_turns += self.combat_timer.last_completed_turns
            remaining_ticks -= step

            ready_enemies = [
                unit
                for unit in self.combat_timer.ready_units
                if isinstance(unit, Enemy) and unit.is_alive
            ]
            for enemy in ready_enemies:
                self.run_monster_turn(enemy)
                self.combat_timer.schedule(enemy, enemy.move_turn_cost)

        return completed_turns

    def run_monster_turn(self, enemy):
        monster = next(
            (monster for monster in self.monsters if monster["unit"] is enemy),
            None,
        )
        if monster is None:
            return

        enemy_position = (enemy.tile_x, enemy.tile_y)
        player_position = self.dungeon_inventory.get_player_position()
        can_see_player = player_position in get_visible_tiles(
            self.map_tiles,
            enemy_position,
            self.rooms,
            self.SIGHT_RADIUS,
        )
        if can_see_player:
            enemy.remember_player_position(player_position)
        elif (
            enemy.last_known_player_position is not None
            and enemy_position == enemy.last_known_player_position
        ):
            enemy.forget_player_position()
        monster["renderer"].set_combat(enemy.is_in_combat)

        occupied = {
            (other["unit"].tile_x, other["unit"].tile_y)
            for other in self.monsters
            if other["unit"] is not enemy and other["unit"].is_alive
        }
        if enemy.is_in_combat:
            target_position = enemy.last_known_player_position
            if target_position is None:
                enemy.forget_player_position()
                monster["renderer"].set_combat(False)
                return
            if can_see_player and max(
                abs(enemy.tile_x - target_position[0]),
                abs(enemy.tile_y - target_position[1]),
            ) <= 1:
                return
            path = find_shortest_path(
                self.map_tiles,
                enemy_position,
                target_position,
                occupied,
            )
            if not path:
                enemy.forget_player_position()
                monster["renderer"].set_combat(False)
                return
        else:
            path = self.get_guard_path(enemy, occupied | {player_position})

        if path:
            self.move_monster(monster, path[0])

    def get_guard_path(self, enemy, blocked_positions):
        position = (enemy.tile_x, enemy.tile_y)
        if enemy.patrol_target == position:
            enemy.patrol_target = None

        if enemy.patrol_target is not None:
            path = find_shortest_path(
                self.map_tiles,
                position,
                enemy.patrol_target,
                blocked_positions,
            )
            if path:
                return path
            enemy.patrol_target = None

        candidates = [
            (tile_x, tile_y)
            for tile_y, row in enumerate(self.map_tiles)
            for tile_x, tile_value in enumerate(row)
            if tile_value == FLOOR
            and (tile_x, tile_y) != position
            and (tile_x, tile_y) not in blocked_positions
        ]
        self.enemy_random.shuffle(candidates)
        for target in candidates:
            path = find_shortest_path(
                self.map_tiles,
                position,
                target,
                blocked_positions,
            )
            if path:
                enemy.patrol_target = target
                return path
        return []

    def move_monster(self, monster, target_position):
        unit = monster["unit"]
        unit.tile_x, unit.tile_y = target_position
        renderer = monster["renderer"]
        renderer.set_transform(
            self.get_tile_screen_x(unit.tile_x),
            self.get_tile_screen_y(unit.tile_y),
        )
        self.set_dungeon_draw_order(renderer, unit.tile_x, unit.tile_y, self.DEPTH_UNIT)
        self.set_maze_base_position(renderer)

    def create_wall_tile(self, tile_x, tile_y):
        wall_y_offset = (self.WALL_TILE_HEIGHT - self.FLOOR_TILE_HEIGHT) // 2

        wall = WallTileRenderer(
            self,
            self.get_tile_screen_x(tile_x),
            self.get_tile_screen_y(tile_y) - wall_y_offset,
            self.FLOOR_TILE_WIDTH,
            self.WALL_TILE_HEIGHT,
            self.FLOOR_TILE_HEIGHT,
            self.get_wall_connections(tile_x, tile_y),
        )
        self.set_dungeon_draw_order(wall, tile_x, tile_y, self.DEPTH_WALL)
        self.set_maze_base_position(wall)
        self.wall_tiles[(tile_x, tile_y)] = wall
        self.maze_renderers.append(wall)

    def get_wall_positions(self):
        wall_positions = set()

        for tile_y, row in enumerate(self.map_tiles):
            for tile_x, tile_value in enumerate(row):
                if tile_value == WALL:
                    wall_positions.add((tile_x, tile_y))

        return wall_positions

    def get_first_floor_position(self):
        for tile_y, row in enumerate(self.map_tiles):
            for tile_x, tile_value in enumerate(row):
                if tile_value != WALL:
                    return (tile_x, tile_y)
        raise ValueError("던전 맵에 이동 가능한 바닥이 없습니다.")

    def get_wall_connections(self, tile_x, tile_y):
        neighbor_offsets = {
            "up_left": (-1, -1),
            "up": (0, -1),
            "up_right": (1, -1),
            "left": (-1, 0),
            "right": (1, 0),
            "down_left": (-1, 1),
            "down": (0, 1),
            "down_right": (1, 1),
        }

        return {
            direction: (tile_x + offset_x, tile_y + offset_y) in self.wall_positions
            for direction, (offset_x, offset_y) in neighbor_offsets.items()
        }

    def get_tile_screen_x(self, tile_x):
        player_x, _ = self.dungeon_inventory.get_player_position()
        return VIRTUAL_WIDTH // 2 + (tile_x - player_x) * self.FLOOR_TILE_WIDTH

    def get_tile_screen_y(self, tile_y):
        _, player_y = self.dungeon_inventory.get_player_position()
        return VIRTUAL_HEIGHT // 2 + (tile_y - player_y) * self.FLOOR_TILE_HEIGHT

    @staticmethod
    def set_dungeon_draw_order(renderer, tile_x, tile_y, depth_order):
        renderer.dungeon_tile_x = tile_x
        renderer.dungeon_tile_y = tile_y
        renderer.dungeon_depth_order = depth_order

    def set_player_draw_order(self, move=None):
        tile_x, tile_y = self.dungeon_inventory.get_player_position()

        if move is not None:
            tile_x += move["move_x"]
            tile_y = max(tile_y, tile_y + move["move_y"])

        self.set_dungeon_draw_order(
            self.player_marker,
            tile_x,
            tile_y,
            self.DEPTH_UNIT,
        )

    def get_draw_order(self, listener):
        if hasattr(listener, "dungeon_tile_y"):
            return (
                -1000,
                listener.dungeon_tile_y,
                listener.dungeon_depth_order,
                listener.dungeon_tile_x,
                getattr(listener, "draw_layer", 0),
            )

        return super().get_draw_order(listener)

    def open_pause(self):
        from .pause_scene import PauseScene

        self.add_overlay(PauseScene(self.game))

    def open_inventory(self):
        from .inventory_scene import InventoryScene

        self.add_overlay(InventoryScene(self.game))

    def open_map(self):
        from .map_scene import MapScene

        self.add_overlay(
            MapScene(
                self.game,
                lambda: self.map_tiles,
                self.get_explored_tiles,
                self.dungeon_inventory.get_player_position,
                lambda: self.rooms,
                lambda: self.connections,
            )
        )

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.open_pause()
            return

        if game_events[TAB]["keydown"]:
            self.open_inventory()
            return

        if game_events[KEY_M]["keydown"]:
            self.open_map()
            return

        self.update_hovered_monster(mouse_position)

        if self.active_move is not None:
            self.block_hotbar_input_during_move(game_events)
            self.update_player_facing(game_events)
            self.update_held_direction(delta_time, game_events)
            self.update_maze_move(delta_time)

            if self.active_move is None:
                self.try_start_maze_move(game_events)

            super().scene_update(delta_time, game_events, mouse_position, wheel_move)
            return

        self.update_hotbar_input_guard(game_events)

        if self.active_hotbar_key is not None:
            self.update_hotbar_input(game_events)
            self.reset_movement_repeat()
            super().scene_update(delta_time, game_events, mouse_position, wheel_move)
            return

        if self.has_direction_keydown(game_events):
            self.update_player_facing(game_events)
            self.update_held_direction(delta_time, game_events)
            self.try_start_maze_move(game_events)

            if self.active_move is not None:
                self.block_hotbar_input_during_move(game_events)
                super().scene_update(delta_time, game_events, mouse_position, wheel_move)
                return

        self.update_hotbar_input(game_events)

        if self.can_use_movement_input(game_events):
            self.update_player_facing(game_events)
            self.update_held_direction(delta_time, game_events)
            self.try_start_maze_move(game_events)
        else:
            self.reset_movement_repeat()

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def update_hovered_monster(self, mouse_position):
        self.hovered_monster = None

        if mouse_position is None:
            return

        for monster in reversed(self.monsters):
            position = (monster["unit"].tile_x, monster["unit"].tile_y)
            if position in self.current_visible_tiles and self.is_mouse_over_monster(monster, mouse_position):
                self.hovered_monster = monster
                return

    @staticmethod
    def is_mouse_over_monster(monster, mouse_position):
        renderer = monster["renderer"]
        dx = mouse_position[0] - renderer.rect.centerx
        dy = mouse_position[1] - renderer.rect.centery
        radius = min(renderer.rect.width, renderer.rect.height) / 2
        return dx * dx + dy * dy <= radius * radius

    def update_hotbar_input(self, game_events):
        if self.active_hotbar_key is None:
            self.start_hotbar_input(game_events)

        if self.active_hotbar_key is None:
            self.hotbar.set_active_label(None)
            self.update_movement_input_guard(game_events)
            return

        self.hotbar.set_active_label(self.active_hotbar_label)

        self.update_active_hotbar_direction(game_events)

        if game_events[self.active_hotbar_key]["keyup"] or not game_events[self.active_hotbar_key]["status"]:
            self.finish_hotbar_input()
            self.active_hotbar_key = None
            self.active_hotbar_label = None
            self.active_hotbar_direction = None
            self.active_hotbar_direction_touched = False
            self.movement_input_guard = True
            self.hotbar.set_active_label(None)

        self.update_movement_input_guard(game_events)

    def start_hotbar_input(self, game_events):
        if self.hotbar_input_guard:
            return

        for key, label in self.HOTBAR_KEYS:
            if game_events[key]["keydown"] or game_events[key]["status"]:
                if not self.has_hotbar_action(label):
                    continue

                self.active_hotbar_key = key
                self.active_hotbar_label = label
                skill = self.get_hotbar_action_skill(label)
                self.active_hotbar_direction = (
                    self.saved_skill_direction
                    if skill is not None and skill.requires_direction
                    else self.get_combined_direction(game_events)
                )
                self.active_hotbar_direction_touched = False
                self.show_skill_target_preview(skill, self.active_hotbar_direction)
                return

    def show_skill_target_preview(self, skill, direction):
        self.clean_tile_filters()

        if skill is None:
            return

        if skill.requires_direction:
            directions = [
                direction
                for _, direction in self.DIRECTION_KEYS
            ]
            if skill.allow_diagonal:
                directions.extend(((-1, -1), (1, -1), (-1, 1), (1, 1)))
        else:
            directions = [None]

        candidate_tiles = set()
        for candidate_direction in directions:
            candidate_tiles.update(
                skill.get_target_tiles(
                    SkillTargetingInput(
                        origin=self.dungeon_inventory.get_player_position(),
                        direction=candidate_direction,
                    )
                )
            )

        self.filter_tiles(candidate_tiles, "yellow")

        if skill.check_direction(direction) is not SkillDirectionStatus.READY:
            return
        if not skill.requires_direction:
            return

        effect_tiles = skill.get_target_tiles(
            SkillTargetingInput(
                origin=self.dungeon_inventory.get_player_position(),
                direction=direction,
            )
        )
        self.filter_tiles(effect_tiles, "red")

    def filter_tiles(self, tile_positions, color):
        filter_method_name = f"filter_{color}"

        for tile_position in tile_positions:
            renderer = self.floor_tiles.get(tile_position)
            if renderer is None:
                continue

            getattr(renderer, filter_method_name)()
            self.filtered_tile_renderers.add(renderer)

    def clean_tile_filters(self):
        for renderer in self.filtered_tile_renderers:
            renderer.filter_clean()

        self.filtered_tile_renderers.clear()

    def use_hotbar_item(self, label):
        self.clean_tile_filters()
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        item_code = getattr(getattr(item_instance, "item", None), "item_code", None)
        use = getattr(getattr(item_instance, "item", None), "use", None)
        used_amount = self.dungeon_inventory.use_item(item_instance)

        if used_amount:
            self.dungeon_inventory.item_inventory.remove_amount(
                item_instance,
                1,
            )
            self.dungeon_inventory.get_hotbar_item(label)

        self.last_skill_call = {
            "label": label,
            "item": item_instance,
            "item_code": item_code,
            "used": bool(used_amount),
        }
        if used_amount:
            item = item_instance.item
            self.add_combat_log(f"{item.get_name()}을 사용했다.")
            get_use_log = getattr(item, "get_use_log", None)
            effect_log = get_use_log(used_amount) if callable(get_use_log) else None
            if effect_log:
                self.add_combat_log(effect_log)
        return bool(used_amount)

    def update_active_hotbar_direction(self, game_events):
        skill = self.get_hotbar_action_skill(self.active_hotbar_label)
        current_direction = self.get_combined_direction(game_events)
        has_direction_input = self.is_direction_pressed(game_events)

        if skill is None or not skill.requires_direction:
            self.active_hotbar_direction = (
                current_direction
                if current_direction is not None
                else (0, 0) if has_direction_input else None
            )
            return

        if has_direction_input:
            self.active_hotbar_direction = current_direction or (0, 0)
            self.active_hotbar_direction_touched = True
        elif self.active_hotbar_direction_touched and self.has_direction_keyup(game_events):
            self.active_hotbar_direction = None

        self.show_skill_target_preview(skill, self.active_hotbar_direction)

    def finish_hotbar_input(self):
        item_instance = self.dungeon_inventory.get_hotbar_item(self.active_hotbar_label)
        skill = self.get_hotbar_action_skill(self.active_hotbar_label)

        if item_instance is not None and skill is None:
            if self.active_hotbar_direction is None:
                self.use_hotbar_item(self.active_hotbar_label)
            else:
                self.cancel_hotbar_skill(self.active_hotbar_label)
            return

        if skill is None:
            self.cancel_hotbar_skill(self.active_hotbar_label)
            return

        direction_status = skill.check_direction(self.active_hotbar_direction)
        if direction_status is SkillDirectionStatus.INVALID:
            self.skip_hotbar_skill(self.active_hotbar_label, self.active_hotbar_direction)
            return

        if direction_status is not SkillDirectionStatus.READY:
            self.cancel_hotbar_skill(self.active_hotbar_label)
            return

        if skill.requires_direction:
            self.saved_skill_direction = self.active_hotbar_direction

        self.use_hotbar_skill(self.active_hotbar_label, self.active_hotbar_direction)

    def use_hotbar_skill(self, label, direction):
        self.set_player_facing_by_direction(direction)
        skill = self.get_hotbar_action_skill(label)
        target_vectors = skill.get_range_vectors(direction)
        target_tiles = skill.get_target_tiles(
            SkillTargetingInput(
                origin=self.dungeon_inventory.get_player_position(),
                direction=direction,
            )
        )
        self.clean_tile_filters()
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        skill_instance = None if item_instance is not None else self.dungeon_inventory.get_hotbar_skill(label)
        targets_by_tile = {
            (monster["unit"].tile_x, monster["unit"].tile_y): monster
            for monster in self.monsters
            if monster["unit"].is_alive
        }
        target_monsters = [
            targets_by_tile[tile]
            for tile in target_tiles
            if tile in targets_by_tile
        ]
        targets = [monster["unit"] for monster in target_monsters]
        battle_rng = self.dungeon_inventory.get_battle_random_generator(self.CURRENT_FLOOR)
        action_skill = skill if skill_instance is None else skill_instance
        results = self.dungeon_inventory.use_skill(action_skill, targets, battle_rng)
        used = results is not None

        if used and item_instance is not None:
            self.dungeon_inventory.item_inventory.remove_amount(item_instance, 1)
            self.dungeon_inventory.get_hotbar_item(label)

        defeated = [monster for monster in target_monsters if not monster["unit"].is_alive]
        for monster in defeated:
            self.remove_monster(monster)

        completed_turns = 0
        if used:
            attack_turn_cost = self.dungeon_inventory.get_stat().attack_turn_cost
            completed_turns = self.advance_monster_turns(attack_turn_cost)
            self.combat_timer.schedule(self.dungeon_inventory.player, attack_turn_cost)
            self.spawn_periodic_monsters(completed_turns)

        self.last_skill_call = {
            "label": label,
            "skill": skill,
            "item": item_instance,
            "direction": direction,
            "target_vectors": target_vectors,
            "target_tiles": target_tiles,
            "targets": targets,
            "results": results or [],
            "used": used,
            "empty_target": not targets,
        }
        if used:
            self.add_skill_combat_logs(skill, targets, results)
        return used

    def add_combat_log(self, message):
        if not hasattr(self, "combat_logs"):
            self.combat_logs = []
        self.combat_logs.append(str(message))
        overflow = len(self.combat_logs) - self.COMBAT_LOG_MAX_COUNT
        if overflow > 0:
            del self.combat_logs[:overflow]

    def add_skill_combat_logs(self, skill, targets, results):
        self.add_combat_log(f"{skill.name} 스킬을 사용했다.")
        attack_results = [result for result in results if isinstance(result, AttackResult)]
        if not targets:
            return
        for index, result in enumerate(attack_results):
            target = targets[index % len(targets)]
            if result.hit:
                self.add_combat_log(
                    f"플레이어 > {target.name} {result.damage} 데미지"
                )
            else:
                self.add_combat_log(
                    f"플레이어 > {target.name} 공격이 빗나갔다"
                )

    def remove_monster(self, monster):
        if monster not in self.monsters:
            return False
        unit = monster["unit"]
        renderer = monster["renderer"]
        self.combat_timer.unregister(unit)
        renderer.destroy()
        if renderer in self.maze_renderers:
            self.maze_renderers.remove(renderer)
        self.monsters.remove(monster)
        if self.hovered_monster is monster:
            self.hovered_monster = None
        return True

    def get_hotbar_action_skill(self, label):
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        if item_instance is not None:
            return getattr(item_instance.item, "skillbase", None)

        skill_instance = self.dungeon_inventory.get_hotbar_skill(label)
        if skill_instance is not None:
            return skill_instance.skill

        return None

    def has_hotbar_action(self, label):
        return (
            self.dungeon_inventory.get_hotbar_item(label) is not None
            or self.dungeon_inventory.get_hotbar_skill(label) is not None
        )

    def get_hotbar_display_skill(self, label):
        return self.dungeon_inventory.get_hotbar_skill(label)

    def has_equipped_hotbar_skill(self, label):
        return self.dungeon_inventory.get_hotbar_skill(label) is not None

    def cancel_hotbar_skill(self, label):
        self.clean_tile_filters()
        self.last_skill_call = {
            "label": label,
            "direction": None,
            "cancelled": True,
        }

    def skip_hotbar_skill(self, label, direction):
        self.clean_tile_filters()
        self.last_skill_call = {
            "label": label,
            "skill": self.get_hotbar_action_skill(label),
            "direction": direction,
            "used": False,
            "invalid_direction": True,
        }

    def format_direction(self, direction):
        return self.DIRECTION_LABELS.get(direction, "중립")

    @staticmethod
    def format_vectors(vectors):
        if not vectors:
            return "[]"

        return "[" + ", ".join(f"({x},{y})" for x, y in vectors) + "]"

    def has_direction_keydown(self, game_events):
        return any(game_events[key]["keydown"] for key, _ in self.DIRECTION_KEYS)

    def has_direction_keyup(self, game_events):
        return any(game_events[key]["keyup"] for key, _ in self.DIRECTION_KEYS)

    def get_combined_direction(self, game_events):
        direction_x = 0
        direction_y = 0

        if game_events[ARROW_LEFT]["status"]:
            direction_x -= 1
        if game_events[ARROW_RIGHT]["status"]:
            direction_x += 1
        if game_events[ARROW_UP]["status"]:
            direction_y -= 1
        if game_events[ARROW_DOWN]["status"]:
            direction_y += 1

        if direction_x == 0 and direction_y == 0:
            return None

        return (direction_x, direction_y)

    def set_player_facing_by_direction(self, direction):
        if direction is None:
            return

        direction_x, direction_y = direction

        if direction_x < 0:
            self.player_marker.set_facing_left(True)
        elif direction_x > 0:
            self.player_marker.set_facing_left(False)
        elif direction_y < 0:
            self.player_marker.set_facing_left(True)
        elif direction_y > 0:
            self.player_marker.set_facing_left(False)

    def update_player_facing(self, game_events):
        direction = self.get_combined_direction(game_events)
        self.set_player_facing_by_direction(direction)

    def can_use_movement_input(self, game_events):
        if self.active_hotbar_key is not None:
            return False
        if self.is_hotbar_pressed(game_events):
            return False
        if self.movement_input_guard:
            return False

        return True

    def update_movement_input_guard(self, game_events):
        if self.movement_input_guard and not self.is_direction_pressed(game_events):
            self.movement_input_guard = False

    def block_hotbar_input_during_move(self, game_events):
        if self.is_hotbar_pressed(game_events):
            self.hotbar_input_guard = True

    def update_hotbar_input_guard(self, game_events):
        if self.hotbar_input_guard and not self.is_hotbar_pressed(game_events):
            self.hotbar_input_guard = False

    def reset_movement_repeat(self):
        self.held_direction = None
        self.hold_elapsed = 0.0
        self.repeat_move_enabled = False

    def is_hotbar_pressed(self, game_events):
        return any(game_events[key]["status"] for key, _ in self.HOTBAR_KEYS)

    def is_direction_pressed(self, game_events):
        return any(game_events[key]["status"] for key, _ in self.DIRECTION_KEYS)

    def update_held_direction(self, delta_time, game_events):
        direction = self.get_pressed_direction(game_events)

        if direction is not None and not self.can_start_move_direction(direction, game_events):
            direction = None

        if direction is None:
            self.held_direction = None
            self.hold_elapsed = 0.0
            self.repeat_move_enabled = False
            return

        if direction != self.held_direction:
            self.held_direction = direction
            self.hold_elapsed = 0.0
            self.repeat_move_enabled = False
            return

        self.hold_elapsed += delta_time

        if self.hold_elapsed >= self.MOVE_REPEAT_DELAY:
            self.repeat_move_enabled = True

    def try_start_maze_move(self, game_events):
        if self.active_move is not None:
            return

        direction = self.get_keydown_direction(game_events)

        if direction is None and self.repeat_move_enabled:
            direction = self.held_direction

        if direction is None:
            return

        if not self.can_start_move_direction(direction, game_events):
            return

        self.start_maze_move(direction)

    def get_keydown_direction(self, game_events):
        if not self.has_direction_keydown(game_events):
            return None

        return self.get_combined_direction(game_events)

    def get_pressed_direction(self, game_events):
        return self.get_combined_direction(game_events)

    def can_start_move_direction(self, direction, game_events):
        direction_x, direction_y = direction

        if not game_events[KEY_T]["status"]:
            return True

        return direction_x != 0 and direction_y != 0

    def start_maze_move(self, direction):
        move_x, move_y = direction
        shift_x = -move_x * self.FLOOR_TILE_WIDTH
        shift_y = -move_y * self.FLOOR_TILE_HEIGHT

        player_x, player_y = self.dungeon_inventory.get_player_position()
        target_tile = (player_x + move_x, player_y + move_y)

        if not self.can_move_to(target_tile):
            return

        self.active_move = {
            "elapsed": 0.0,
            "start_offset_x": self.maze_offset_x,
            "start_offset_y": self.maze_offset_y,
            "move_x": move_x,
            "move_y": move_y,
            "shift_x": shift_x,
            "shift_y": shift_y,
        }
        self.set_player_draw_order(self.active_move)

    def can_move_to(self, target_tile):
        tile_x, tile_y = target_tile

        if tile_y < 0 or tile_y >= len(self.map_tiles):
            return False
        if tile_x < 0 or tile_x >= len(self.map_tiles[tile_y]):
            return False

        return target_tile not in self.wall_positions and not self.has_monster_at(target_tile)

    def has_monster_at(self, tile_position):
        return any(
            monster["unit"].is_alive and (monster["unit"].tile_x, monster["unit"].tile_y) == tile_position
            for monster in self.monsters
        )

    def update_maze_move(self, delta_time):
        if self.active_move is None:
            return

        move = self.active_move
        move["elapsed"] = min(self.MOVE_DURATION, move["elapsed"] + delta_time)
        progress = move["elapsed"] / self.MOVE_DURATION

        self.maze_offset_x = move["start_offset_x"] + move["shift_x"] * progress
        self.maze_offset_y = move["start_offset_y"] + move["shift_y"] * progress
        self.set_player_draw_order(move)
        self.refresh_maze_positions()

        if move["elapsed"] < self.MOVE_DURATION:
            return

        self.dungeon_inventory.move_player(move["move_x"], move["move_y"])
        move_turn_cost = self.dungeon_inventory.get_stat().move_turn_cost
        completed_turns = self.advance_monster_turns(move_turn_cost)
        self.combat_timer.schedule(self.dungeon_inventory.player, move_turn_cost)
        self.set_player_draw_order()
        self.active_move = None
        self.refresh_visible_tiles()
        self.spawn_periodic_monsters(completed_turns)

    def set_maze_base_position(self, renderer):
        renderer.maze_base_x = renderer.rect.centerx - self.maze_offset_x
        renderer.maze_base_y = renderer.rect.centery - self.maze_offset_y

    def refresh_maze_positions(self):
        for renderer in self.maze_renderers:
            renderer.set_transform(
                round(renderer.maze_base_x + self.maze_offset_x),
                round(renderer.maze_base_y + self.maze_offset_y),
            )

    def scene_draw(self):
        screen = self.game.virtual_screen
        screen.fill((0, 0, 0))

        super().scene_draw()
