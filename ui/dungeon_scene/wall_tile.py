import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


class WallTileRenderer(Renderer):
    draw_layer = -50
    texture_images = {}

    def __init__(self, scene, pos_x, pos_y, width, height, connections=None):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.connections = connections or {}
        self.configure_draw_variant()

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(screen.get_rect())

        cap_height = self.rect.height - self.scene.FLOOR_TILE_HEIGHT
        cap_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, cap_height)
        body_rect = pygame.Rect(
            self.rect.left,
            self.rect.top + cap_height,
            self.rect.width,
            self.scene.FLOOR_TILE_HEIGHT,
        )

        self.draw_variant(screen, cap_rect, body_rect)

        screen.set_clip(previous_clip)

    @classmethod
    def get_texture_image(cls, key, width, height):
        texture_size = (key, int(width), int(height))

        if texture_size not in cls.texture_images:
            cls.texture_images[texture_size] = DUNGEON_TEXTURES.get_scaled(key, width, height)

        return cls.texture_images[texture_size]

    def configure_draw_variant(self):
        self.cap_borders = self.build_cap_borders()
        self.body_borders = self.build_body_borders()
        self.erase_left_body_foot = self.is_connected("down_left") and not self.is_connected("left")
        self.erase_right_body_foot = self.is_connected("down_right") and not self.is_connected("right")

        if self.is_connected("up") and self.is_connected("down"):
            self.draw_variant = self.draw_body_ceiling_without_cap
        elif self.is_connected("up"):
            self.draw_variant = self.draw_brown_body_without_cap
        elif self.is_connected("down"):
            self.draw_variant = self.draw_body_ceiling_with_cap
        else:
            self.draw_variant = self.draw_brown_body_with_cap

    def draw_brown_body_with_cap(self, screen, cap_rect, body_rect):
        self.draw_brown_body(screen, body_rect, draw_top_border=False)
        self.draw_cap(screen, cap_rect)

    def draw_brown_body_without_cap(self, screen, cap_rect, body_rect):
        self.draw_brown_body(screen, body_rect, draw_top_border=True)

    def draw_body_ceiling_with_cap(self, screen, cap_rect, body_rect):
        self.draw_connected_body(screen, body_rect)
        self.draw_cap(screen, cap_rect)

    def draw_body_ceiling_without_cap(self, screen, cap_rect, body_rect):
        self.draw_connected_body(screen, body_rect)

    def draw_brown_body(self, screen, body_rect, draw_top_border):
        body_texture = self.get_texture_image("wall", body_rect.width, body_rect.height)

        if body_texture is not None:
            screen.blit(body_texture, body_rect)
        else:
            pygame.draw.rect(screen, (82, 52, 32), body_rect)
            pygame.draw.rect(screen, (58, 37, 24), body_rect, width=2)

        if draw_top_border:
            self.draw_border_line(screen, body_rect.left, body_rect.top, body_rect.right, body_rect.top)

    def draw_cap(self, screen, cap_rect):
        self.draw_ceiling_box(screen, cap_rect, self.cap_borders)

    def is_connected(self, direction):
        return self.connections.get(direction, False)

    def build_cap_borders(self):
        return {
            "top": True,
            "bottom": not self.is_connected("down"),
            "left": not self.is_connected("left"),
            "right": not self.is_connected("right"),
        }

    def build_body_borders(self):
        return {
            "top": False,
            "bottom": False,
            "left": not (self.is_connected("left") and self.is_connected("down_left")),
            "right": not (self.is_connected("right") and self.is_connected("down_right")),
        }

    def draw_connected_body(self, screen, body_rect):
        self.draw_ceiling_box(screen, body_rect, self.body_borders)

        cap_height = self.rect.height - self.scene.FLOOR_TILE_HEIGHT
        black_color = (12, 10, 9)

        if self.erase_left_body_foot:
            erase_rect = pygame.Rect(body_rect.left, body_rect.bottom - cap_height, 4, cap_height)
            pygame.draw.rect(screen, black_color, erase_rect)

        if self.erase_right_body_foot:
            erase_rect = pygame.Rect(body_rect.right - 4, body_rect.bottom - cap_height, 4, cap_height)
            pygame.draw.rect(screen, black_color, erase_rect)

    def draw_ceiling_box(self, screen, rect, borders):
        border_color = (172, 44, 38)
        border_width = 4
        black_color = (12, 10, 9)

        pygame.draw.rect(screen, black_color, rect)

        if borders["top"]:
            self.draw_edge_rect(
                screen,
                pygame.Rect(rect.left, rect.top, rect.width, border_width),
                border_color,
            )
        if borders["bottom"]:
            self.draw_edge_rect(
                screen,
                pygame.Rect(rect.left, rect.bottom - border_width, rect.width, border_width),
                border_color,
            )
        if borders["left"]:
            self.draw_edge_rect(
                screen,
                pygame.Rect(rect.left, rect.top, border_width, rect.height),
                border_color,
            )
        if borders["right"]:
            self.draw_edge_rect(
                screen,
                pygame.Rect(rect.right - border_width, rect.top, border_width, rect.height),
                border_color,
            )

    def draw_edge_rect(self, screen, rect, fallback_color):
        edge_texture = self.get_texture_image("wall_edge", rect.width, rect.height)

        if edge_texture is not None:
            screen.blit(edge_texture, rect)
        else:
            pygame.draw.rect(screen, fallback_color, rect)

    def draw_border_line(self, screen, start_x, start_y, end_x, end_y):
        self.draw_edge_rect(
            screen,
            pygame.Rect(start_x, start_y, end_x - start_x, 4),
            (172, 44, 38),
        )
