import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class DungeonFogRenderer(Renderer):
    """겹치는 타일에서도 농도가 누적되지 않는 단일 탐험 안개 레이어."""

    draw_layer = -10
    FOG_ALPHA = 180

    def __init__(self, scene, floor_tiles_getter, wall_tiles_getter, visible_tiles_getter):
        self.floor_tiles_getter = floor_tiles_getter
        self.wall_tiles_getter = wall_tiles_getter
        self.visible_tiles_getter = visible_tiles_getter
        super().__init__(scene, VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    def draw(self, screen):
        visible_tiles = self.visible_tiles_getter()
        fog_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        fog_color = (0, 0, 0, self.FOG_ALPHA)

        # 같은 Surface에 색을 기록하면 겹친 영역도 알파가 한 번만 적용된다.
        for tile_position, renderer in self.floor_tiles_getter().items():
            if tile_position not in visible_tiles:
                pygame.draw.rect(fog_surface, fog_color, renderer.rect)

        for tile_position, renderer in self.wall_tiles_getter().items():
            if tile_position not in visible_tiles:
                pygame.draw.rect(fog_surface, fog_color, renderer.rect)

        # 높이가 큰 시야 밖 벽의 사각형이 방의 현재 시야 벽 위로 겹칠 수 있다.
        # 현재 보이는 바닥과 벽 영역을 마지막에 투명하게 되돌려 방 경계 전체를 밝게 유지한다.
        clear_color = (0, 0, 0, 0)
        for tile_position, renderer in self.floor_tiles_getter().items():
            if tile_position in visible_tiles:
                pygame.draw.rect(fog_surface, clear_color, renderer.rect)

        for tile_position, renderer in self.wall_tiles_getter().items():
            if tile_position in visible_tiles:
                pygame.draw.rect(fog_surface, clear_color, renderer.rect)

        screen.blit(fog_surface, (0, 0))
