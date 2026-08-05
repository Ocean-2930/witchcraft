import pygame
from importlib import import_module

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer

draw_explored_map = import_module("ui.global.map_graph").draw_explored_map


class MapPanelRenderer(Renderer):
    draw_layer = -10
    MIN_ZOOM = 1.0
    MAX_ZOOM = 4.0
    ZOOM_STEP = 1.18
    MAP_PADDING = 18
    PAN_MARGIN = 44

    def __init__(
        self,
        scene,
        map_tiles_getter,
        explored_tiles_getter,
        player_position_getter,
        rooms_getter,
        connections_getter,
        width=980,
        height=590,
    ):
        self.map_tiles_getter = map_tiles_getter
        self.explored_tiles_getter = explored_tiles_getter
        self.player_position_getter = player_position_getter
        self.rooms_getter = rooms_getter
        self.connections_getter = connections_getter
        self.zoom = self.MIN_ZOOM
        self.pan_x = 0.0
        self.pan_y = 0.0
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, width, height)

    def get_map_rect(self):
        map_rect = self.rect.inflate(-48, -112)
        map_rect.top += 28
        return map_rect

    def zoom_by(self, wheel_move):
        if not wheel_move:
            return
        self.zoom = max(
            self.MIN_ZOOM,
            min(self.MAX_ZOOM, self.zoom * (self.ZOOM_STEP ** wheel_move)),
        )
        self.clamp_pan()

    def pan_by(self, move_x, move_y):
        self.pan_x += move_x
        self.pan_y += move_y
        self.clamp_pan()

    def clamp_pan(self):
        map_tiles = self.map_tiles_getter()
        if not map_tiles or not map_tiles[0]:
            self.pan_x = 0.0
            self.pan_y = 0.0
            return
        map_rect = self.get_map_rect()
        map_width = max(len(row) for row in map_tiles)
        map_height = len(map_tiles)
        usable_width = max(1, map_rect.width - self.MAP_PADDING * 2)
        usable_height = max(1, map_rect.height - self.MAP_PADDING * 2)
        base_scale = min(usable_width / map_width, usable_height / map_height)
        content_width = map_width * base_scale * self.zoom
        content_height = map_height * base_scale * self.zoom
        limit_x = max(0.0, (content_width - usable_width) / 2) + self.PAN_MARGIN
        limit_y = max(0.0, (content_height - usable_height) / 2) + self.PAN_MARGIN
        self.pan_x = max(-limit_x, min(limit_x, self.pan_x))
        self.pan_y = max(-limit_y, min(limit_y, self.pan_y))

    def draw_legend(self, screen, map_rect):
        legend_rect = pygame.Rect(map_rect.left + 12, map_rect.top + 12, 188, 94)
        pygame.draw.rect(screen, (0, 0, 0), legend_rect, border_radius=5)
        pygame.draw.rect(screen, (82, 93, 97), legend_rect, width=1, border_radius=5)
        rows = (
            ((73, 220, 154), "현재 위치", "circle"),
            ((225, 235, 244), "올라가는 계단", "ring"),
            ((238, 177, 75), "내려가는 계단", "plus"),
        )
        for index, (color, label, marker_type) in enumerate(rows):
            point = (legend_rect.left + 18, legend_rect.top + 18 + index * 27)
            if marker_type == "circle":
                pygame.draw.circle(screen, color, point, 5)
            elif marker_type == "ring":
                pygame.draw.circle(screen, color, point, 6, width=2)
            else:
                pygame.draw.line(screen, color, (point[0] - 5, point[1]), (point[0] + 5, point[1]), 2)
                pygame.draw.line(screen, color, (point[0], point[1] - 5), (point[0], point[1] + 5), 2)
            text = self.scene.legend_font.render(label, True, (216, 221, 219))
            screen.blit(text, text.get_rect(midleft=(legend_rect.left + 34, point[1])))

    def draw(self, screen):
        overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 7, 10, 190))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (0, 0, 0), self.rect, border_radius=10)
        pygame.draw.rect(screen, (130, 145, 149), self.rect, width=2, border_radius=10)

        title = self.scene.title_font.render("탐험 지도", True, (240, 241, 232))
        screen.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 47)))
        map_rect = self.get_map_rect()
        pygame.draw.rect(screen, (0, 0, 0), map_rect, border_radius=6)
        previous_clip = screen.get_clip()
        screen.set_clip(map_rect)
        draw_explored_map(
            screen,
            map_rect,
            self.map_tiles_getter(),
            self.explored_tiles_getter(),
            self.player_position_getter(),
            self.rooms_getter(),
            self.connections_getter(),
            padding=self.MAP_PADDING,
            zoom=self.zoom,
            pan_offset=(self.pan_x, self.pan_y),
        )
        screen.set_clip(previous_clip)
        self.draw_legend(screen, map_rect)
