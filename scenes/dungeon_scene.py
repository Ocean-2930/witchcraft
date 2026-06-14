from .scene import Scene
from settings import (
    ARROW_DOWN,
    ARROW_LEFT,
    ARROW_RIGHT,
    ARROW_UP,
    ESCAPE,
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
    PauseButton,
    PlayerMarkerRenderer,
    SkillLogRenderer,
    WallTileRenderer,
)


class DungeonScene(Scene):
    FLOOR_TILE_WIDTH = 90
    FLOOR_TILE_HEIGHT = 60
    WALL_TILE_HEIGHT = 80
    MOVE_DURATION = 0.16
    MOVE_REPEAT_DELAY = 0.24
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
        self.player_tile_x, self.player_tile_y = self.dungeon_map["position"]
        self.wall_positions = self.get_wall_positions()
        self.active_move = None
        self.held_direction = None
        self.hold_elapsed = 0.0
        self.repeat_move_enabled = False
        self.active_hotbar_label = None
        self.active_hotbar_key = None
        self.active_hotbar_direction = None
        self.active_hotbar_cancelled = False
        self.active_hotbar_direction_touched = False
        self.saved_skill_direction = None
        self.movement_input_guard = False
        self.last_skill_call = None
        self.maze_offset_x = 0.0
        self.maze_offset_y = 0.0
        self.maze_renderers = []
        self.floor_tiles = []
        self.wall_tiles = []
        self.create_floor_tiles()
        self.create_wall_tiles()
        self.player_marker = PlayerMarkerRenderer(
            self,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            42,
            42,
        )
        self.hotbar = HotbarRenderer(
            self,
            28 + (72 * 4 + 8 * 3) // 2,
            VIRTUAL_HEIGHT - 28 - (72 * 2 + 8) // 2,
            72,
            8,
        )
        self.skill_log = SkillLogRenderer(
            self,
            28 + 280 // 2,
            VIRTUAL_HEIGHT - 28 - (72 * 2 + 8) - 14 - 34 // 2,
            280,
            34,
        )

        self.pause_button = PauseButton(
            self,
            VIRTUAL_WIDTH - 42,
            42,
            48,
            48,
            self.open_pause,
        )

    def create_floor_tiles(self):
        for tile_y, row in enumerate(self.map_tiles):
            for tile_x, tile_value in enumerate(row):
                tile = FloorTileRenderer(
                    self,
                    self.get_tile_screen_x(tile_x),
                    self.get_tile_screen_y(tile_y),
                    self.FLOOR_TILE_WIDTH,
                    self.FLOOR_TILE_HEIGHT,
                )
                self.set_maze_base_position(tile)
                self.floor_tiles.append(tile)
                self.maze_renderers.append(tile)

    def create_wall_tiles(self):
        wall_y_offset = (self.WALL_TILE_HEIGHT - self.FLOOR_TILE_HEIGHT) // 2

        for tile_x, tile_y in self.wall_positions:
            wall = WallTileRenderer(
                self,
                self.get_tile_screen_x(tile_x),
                self.get_tile_screen_y(tile_y) - wall_y_offset,
                self.FLOOR_TILE_WIDTH,
                self.WALL_TILE_HEIGHT,
                self.get_wall_connections(tile_x, tile_y),
            )
            self.set_maze_base_position(wall)
            self.wall_tiles.append(wall)
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
        return VIRTUAL_WIDTH // 2 + (tile_x - self.player_tile_x) * self.FLOOR_TILE_WIDTH

    def get_tile_screen_y(self, tile_y):
        return VIRTUAL_HEIGHT // 2 + (tile_y - self.player_tile_y) * self.FLOOR_TILE_HEIGHT

    def open_pause(self):
        from .pause_scene import PauseScene

        self.add_overlay(PauseScene(self.game))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.open_pause()

        self.update_hotbar_input(game_events)
        self.update_maze_move(delta_time)

        if self.can_use_movement_input(game_events):
            self.update_held_direction(delta_time, game_events)
            self.try_start_maze_move(game_events)
        else:
            self.reset_movement_repeat()

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

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
            self.active_hotbar_cancelled = False
            self.active_hotbar_direction_touched = False
            self.movement_input_guard = True
            self.hotbar.set_active_label(None)

        self.update_movement_input_guard(game_events)

    def start_hotbar_input(self, game_events):
        for key, label in self.HOTBAR_KEYS:
            if game_events[key]["keydown"] or game_events[key]["status"]:
                self.active_hotbar_key = key
                self.active_hotbar_label = label
                self.active_hotbar_direction = self.saved_skill_direction
                self.active_hotbar_cancelled = False
                self.active_hotbar_direction_touched = False
                return

    def update_active_hotbar_direction(self, game_events):
        if self.has_direction_pressed(game_events):
            self.active_hotbar_direction = self.get_combined_direction(game_events)
            self.active_hotbar_cancelled = False
            self.active_hotbar_direction_touched = True

        if (
            self.active_hotbar_direction_touched
            and self.has_direction_keyup(game_events)
            and self.get_combined_direction(game_events) is None
        ):
            self.active_hotbar_direction = None
            self.active_hotbar_cancelled = True

    def finish_hotbar_input(self):
        if self.active_hotbar_cancelled:
            self.cancel_hotbar_skill(self.active_hotbar_label)
            return

        if self.active_hotbar_direction is None:
            self.cancel_hotbar_skill(self.active_hotbar_label)
            return

        self.saved_skill_direction = self.active_hotbar_direction
        self.use_hotbar_skill(self.active_hotbar_label, self.active_hotbar_direction)

    def use_hotbar_skill(self, label, direction):
        self.last_skill_call = {
            "label": label,
            "direction": direction,
        }
        self.skill_log.set_text(f"스킬 {label}: {self.format_direction(direction)}")

    def cancel_hotbar_skill(self, label):
        self.last_skill_call = {
            "label": label,
            "direction": None,
            "cancelled": True,
        }
        self.skill_log.set_text(f"스킬 {label}: 취소")

    @staticmethod
    def format_direction(direction):
        direction_labels = {
            (-1, 0): "왼쪽",
            (1, 0): "오른쪽",
            (0, -1): "위",
            (0, 1): "아래",
            (-1, -1): "왼쪽 위",
            (1, -1): "오른쪽 위",
            (-1, 1): "왼쪽 아래",
            (1, 1): "오른쪽 아래",
        }

        return direction_labels.get(direction, "중립")

    def has_direction_pressed(self, game_events):
        return any(game_events[key]["status"] for key, _ in self.DIRECTION_KEYS)

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

        target_tile = (self.player_tile_x + move_x, self.player_tile_y + move_y)

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

    def can_move_to(self, target_tile):
        tile_x, tile_y = target_tile

        if tile_y < 0 or tile_y >= len(self.map_tiles):
            return False
        if tile_x < 0 or tile_x >= len(self.map_tiles[tile_y]):
            return False

        return target_tile not in self.wall_positions

    def update_maze_move(self, delta_time):
        if self.active_move is None:
            return

        move = self.active_move
        move["elapsed"] = min(self.MOVE_DURATION, move["elapsed"] + delta_time)
        progress = move["elapsed"] / self.MOVE_DURATION

        self.maze_offset_x = move["start_offset_x"] + move["shift_x"] * progress
        self.maze_offset_y = move["start_offset_y"] + move["shift_y"] * progress
        self.refresh_maze_positions()

        if move["elapsed"] < self.MOVE_DURATION:
            return

        self.player_tile_x += move["move_x"]
        self.player_tile_y += move["move_y"]
        self.active_move = None

    def set_maze_base_position(self, renderer):
        renderer.maze_base_x = renderer.rect.centerx
        renderer.maze_base_y = renderer.rect.centery

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
