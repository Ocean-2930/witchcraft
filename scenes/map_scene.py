import pygame

from settings import ESCAPE, KEY_M, MOUSE_LEFT, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import MapPanelRenderer, SettingsButton

from .scene import Scene


class MapScene(Scene):
    def __init__(self, game, map_tiles_getter, explored_tiles_getter, player_position_getter, rooms_getter, connections_getter):
        self.map_tiles_getter = map_tiles_getter
        self.explored_tiles_getter = explored_tiles_getter
        self.player_position_getter = player_position_getter
        self.rooms_getter = rooms_getter
        self.connections_getter = connections_getter
        super().__init__(game)

    def scene_initialize(self):
        self.title_font = pygame.font.SysFont("malgungothic", 36, bold=True)
        self.button_font = pygame.font.SysFont("malgungothic", 20, bold=True)
        self.legend_font = pygame.font.SysFont("malgungothic", 16)
        self.drag_position = None
        self.panel_renderer = MapPanelRenderer(
            self,
            self.map_tiles_getter,
            self.explored_tiles_getter,
            self.player_position_getter,
            self.rooms_getter,
            self.connections_getter,
        )
        self.close_button = SettingsButton(
            self,
            "닫기",
            VIRTUAL_WIDTH // 2 + 420,
            VIRTUAL_HEIGHT // 2 - 247,
            82,
            40,
            self.close,
            font=self.button_font,
        )

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"] or game_events[KEY_M]["keydown"]:
            self.close()
            return

        map_rect = self.panel_renderer.get_map_rect()
        if mouse_position is not None and map_rect.collidepoint(mouse_position):
            self.panel_renderer.zoom_by(wheel_move)
            if game_events[MOUSE_LEFT]["keydown"]:
                self.drag_position = mouse_position

        if game_events[MOUSE_LEFT]["keyup"] or not game_events[MOUSE_LEFT]["status"]:
            self.drag_position = None
        elif self.drag_position is not None and mouse_position is not None:
            move_x = mouse_position[0] - self.drag_position[0]
            move_y = mouse_position[1] - self.drag_position[1]
            self.panel_renderer.pan_by(move_x, move_y)
            self.drag_position = mouse_position
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def close(self):
        self.exit_scene()

    def scene_draw(self):
        super().scene_draw()
