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
    KEY_Q,
    KEY_R,
    KEY_T,
    KEY_W,
    VIRTUAL_HEIGHT,
    VIRTUAL_WIDTH,
)
from ui import (
    FloorTileRenderer,
    HotbarRenderer,
    MonsterMarkerRenderer,
    MonsterTooltipRenderer,
    PauseButton,
    PlayerMarkerRenderer,
    PlayerStatusRenderer,
    SkillDirectionCompassRenderer,
    WallTileRenderer,
)
from skills import Skill, SkillDirectionStatus, SkillTargetingInput
from units import Enemy, Player
from utilities import DungeonInventory


class DungeonScene(Scene):
    FLOOR_TILE_WIDTH = 90
    FLOOR_TILE_HEIGHT = 60
    WALL_TILE_HEIGHT = 80
    TILE_RENDER_BUFFER = 2
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
        "position": [3, 3], "map": [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    }

    def __init__(self, game, dungeon_map=None):
        self.dungeon_map = dungeon_map or self.DEFAULT_MAP
        super().__init__(game)

    def scene_initialize(self):
        self.map_tiles = self.dungeon_map["map"]
        self.player = Player("플레이어")
        self.dungeon_inventory = DungeonInventory(unit_base=self.player)
        self.player.tile_x, self.player.tile_y = self.dungeon_map["position"]
        self.player_status = PlayerStatusRenderer(
            self,
            self.player,
            28 + (92 + 10 + 82 + 10 + 220) // 2,
            28 + 92 // 2,
        )
        self.hotbar_skills = self.create_hotbar_skills()
        self.monsters = []
        self.hovered_monster = None
        self.peek_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.monster_tooltip = MonsterTooltipRenderer(self)
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
        self.last_skill_call = None
        self.maze_offset_x = 0.0
        self.maze_offset_y = 0.0
        self.maze_renderers = []
        self.floor_tiles = {}
        self.wall_tiles = {}
        self.refresh_visible_tiles()
        self.player_marker = PlayerMarkerRenderer(
            self,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            72,
            72,
        )
        self.set_dungeon_draw_order(self.player_marker, self.player.tile_x, self.player.tile_y, self.DEPTH_UNIT)
        self.create_monster(6, 3)
        self.hotbar = HotbarRenderer(
            self,
            28 + (72 * 4 + 8 * 3) // 2,
            VIRTUAL_HEIGHT - 28 - (72 * 2 + 8) // 2,
            72,
            8,
        )
        self.skill_direction_compass = SkillDirectionCompassRenderer(
            self,
            self.hotbar.rect.right + 28,
            self.hotbar.rect.centery,
            46,
            46,
        )
        self.pause_button = PauseButton(
            self,
            VIRTUAL_WIDTH - 42,
            42,
            48,
            48,
            self.open_pause,
        )

        if settings.ENABLE_TEST_SCENARIO:
            from .test_scenario import senario

            senario(self)

    def create_hotbar_skills(self):
        return {
            "1": Skill("1", range_vectors=[(0, -1)]),
            "2": Skill("2", range_vectors=[(0, -1)]),
            "3": Skill("3", range_vectors=[(0, -1)]),
            "4": Skill("4", range_vectors=[(0, -1)]),
            "Q": Skill("Q", range_vectors=[(0, -1)]),
            "W": Skill("W", range_vectors=[(0, -1)]),
            "E": Skill("E", range_vectors=[(0, -1)]),
            "R": Skill("R", range_vectors=[(0, -1), (0, -2)]),
        }

    def refresh_visible_tiles(self):
        visible_tiles = self.get_visible_tile_positions()
        visible_walls = visible_tiles & self.wall_positions

        self.remove_hidden_tiles(self.floor_tiles, visible_tiles)
        self.remove_hidden_tiles(self.wall_tiles, visible_walls)

        for tile_x, tile_y in visible_tiles:
            if (tile_x, tile_y) not in self.floor_tiles:
                self.create_floor_tile(tile_x, tile_y)

        for tile_x, tile_y in visible_walls:
            if (tile_x, tile_y) not in self.wall_tiles:
                self.create_wall_tile(tile_x, tile_y)

    def get_visible_tile_positions(self):
        horizontal_radius = ceil((VIRTUAL_WIDTH / 2) / self.FLOOR_TILE_WIDTH) + self.TILE_RENDER_BUFFER
        vertical_radius = ceil((VIRTUAL_HEIGHT / 2) / self.FLOOR_TILE_HEIGHT) + self.TILE_RENDER_BUFFER
        visible_tiles = set()

        start_y = max(0, self.player.tile_y - vertical_radius)
        end_y = min(len(self.map_tiles), self.player.tile_y + vertical_radius + 1)

        for tile_y in range(start_y, end_y):
            row = self.map_tiles[tile_y]
            start_x = max(0, self.player.tile_x - horizontal_radius)
            end_x = min(len(row), self.player.tile_x + horizontal_radius + 1)

            for tile_x in range(start_x, end_x):
                visible_tiles.add((tile_x, tile_y))

        return visible_tiles

    def remove_hidden_tiles(self, tile_renderers, visible_tiles):
        for tile_position, renderer in list(tile_renderers.items()):
            if tile_position in visible_tiles:
                continue

            renderer.destroy()
            self.maze_renderers.remove(renderer)
            del tile_renderers[tile_position]

    def create_floor_tile(self, tile_x, tile_y):
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

    def create_monster(self, tile_x, tile_y):
        unit = Enemy("적 몬스터", max_hp=100, attack_power=0, tile_x=tile_x, tile_y=tile_y)
        monster = {
            "unit": unit,
            "renderer": MonsterMarkerRenderer(
                self,
                self.get_tile_screen_x(unit.tile_x),
                self.get_tile_screen_y(unit.tile_y),
                self.MONSTER_MARKER_SIZE,
                self.MONSTER_MARKER_SIZE,
            ),
        }
        self.set_dungeon_draw_order(monster["renderer"], unit.tile_x, unit.tile_y, self.DEPTH_UNIT)
        self.set_maze_base_position(monster["renderer"])
        self.maze_renderers.append(monster["renderer"])
        self.monsters.append(monster)
        return monster

    def create_wall_tile(self, tile_x, tile_y):
        wall_y_offset = (self.WALL_TILE_HEIGHT - self.FLOOR_TILE_HEIGHT) // 2

        wall = WallTileRenderer(
            self,
            self.get_tile_screen_x(tile_x),
            self.get_tile_screen_y(tile_y) - wall_y_offset,
            self.FLOOR_TILE_WIDTH,
            self.WALL_TILE_HEIGHT,
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
                if tile_value == 1:
                    wall_positions.add((tile_x, tile_y))

        return wall_positions

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
        return VIRTUAL_WIDTH // 2 + (tile_x - self.player.tile_x) * self.FLOOR_TILE_WIDTH

    def get_tile_screen_y(self, tile_y):
        return VIRTUAL_HEIGHT // 2 + (tile_y - self.player.tile_y) * self.FLOOR_TILE_HEIGHT

    @staticmethod
    def set_dungeon_draw_order(renderer, tile_x, tile_y, depth_order):
        renderer.dungeon_tile_x = tile_x
        renderer.dungeon_tile_y = tile_y
        renderer.dungeon_depth_order = depth_order

    def set_player_draw_order(self, move=None):
        tile_x = self.player.tile_x
        tile_y = self.player.tile_y

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

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.open_pause()
            return

        if game_events[TAB]["keydown"]:
            self.open_inventory()
            return

        self.update_hovered_monster(mouse_position)
        self.update_hotbar_input(game_events)
        self.update_maze_move(delta_time)

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
            if self.is_mouse_over_monster(monster, mouse_position):
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
        for key, label in self.HOTBAR_KEYS:
            if game_events[key]["keydown"] or game_events[key]["status"]:
                self.active_hotbar_key = key
                self.active_hotbar_label = label
                skill = self.get_hotbar_action_skill(label)
                self.active_hotbar_direction = (
                    self.saved_skill_direction
                    if skill is not None and skill.requires_direction
                    else self.get_combined_direction(game_events)
                )
                self.active_hotbar_direction_touched = False
                return

    def use_hotbar_item(self, label):
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        item_code = getattr(getattr(item_instance, "item", None), "item_code", None)
        use = getattr(getattr(item_instance, "item", None), "use", None)
        used_amount = use(self.player) if callable(use) else 0

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
                origin=(self.player.tile_x, self.player.tile_y),
                direction=direction,
            )
        )
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        self.last_skill_call = {
            "label": label,
            "skill": skill,
            "item": item_instance,
            "direction": direction,
            "target_vectors": target_vectors,
            "target_tiles": target_tiles,
        }

    def get_hotbar_action_skill(self, label):
        item_instance = self.dungeon_inventory.get_hotbar_item(label)
        if item_instance is not None:
            return getattr(item_instance.item, "skillbase", None)

        return self.hotbar_skills.get(label)

    def cancel_hotbar_skill(self, label):
        self.last_skill_call = {
            "label": label,
            "direction": None,
            "cancelled": True,
        }

    def skip_hotbar_skill(self, label, direction):
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

        target_tile = (self.player.tile_x + move_x, self.player.tile_y + move_y)

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

        self.player.tile_x += move["move_x"]
        self.player.tile_y += move["move_y"]
        self.set_player_draw_order()
        self.active_move = None
        self.refresh_visible_tiles()

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
        screen.fill((42, 48, 50))

        super().scene_draw()
