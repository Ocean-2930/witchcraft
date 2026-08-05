import pygame
from importlib import import_module

from ui.renderer import Renderer
from ui.ui import UIElement

draw_explored_map = import_module("ui.global.map_graph").draw_explored_map


class MiniMapRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, mini_map):
        self.mini_map = mini_map
        super().__init__(scene, pos_x, pos_y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, border_radius=7)
        pygame.draw.rect(
            screen,
            (211, 220, 215) if self.mini_map.is_hovered else (112, 126, 130),
            self.rect,
            width=2,
            border_radius=7,
        )
        draw_explored_map(
            screen,
            self.rect,
            self.mini_map.map_tiles_getter(),
            self.mini_map.explored_tiles_getter(),
            self.mini_map.player_position_getter(),
            self.mini_map.rooms_getter(),
            self.mini_map.connections_getter(),
            padding=7,
        )


class MiniMap(UIElement):
    def __init__(
        self,
        scene,
        pos_x,
        pos_y,
        width,
        height,
        map_tiles_getter,
        explored_tiles_getter,
        player_position_getter,
        rooms_getter,
        connections_getter,
        on_click,
    ):
        self.map_tiles_getter = map_tiles_getter
        self.explored_tiles_getter = explored_tiles_getter
        self.player_position_getter = player_position_getter
        self.rooms_getter = rooms_getter
        self.connections_getter = connections_getter
        self.click_callback = on_click
        self.is_hovered = False
        renderer = MiniMapRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer)

    def on_left_click(self):
        self.click_callback()

    def on_enter(self):
        self.is_hovered = True

    def on_exit(self):
        self.is_hovered = False

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
