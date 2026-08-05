import pygame

from utilities.dungeon import DOWN_STAIRS, UP_STAIRS, WALL


def draw_explored_map(
    screen,
    rect,
    map_tiles,
    explored_tiles,
    player_position,
    rooms=(),
    connections=(),
    padding=10,
    zoom=1.0,
    pan_offset=(0.0, 0.0),
):
    """방은 사각형, 통로는 중심선으로 구분해 발견 지형을 그린다."""
    if not map_tiles or not map_tiles[0]:
        return

    map_width = max(len(row) for row in map_tiles)
    map_height = len(map_tiles)
    usable_width = max(1, rect.width - padding * 2)
    usable_height = max(1, rect.height - padding * 2)
    scale = min(usable_width / max(1, map_width), usable_height / max(1, map_height)) * zoom
    origin_x = rect.centerx - map_width * scale / 2 + pan_offset[0]
    origin_y = rect.centery - map_height * scale / 2 + pan_offset[1]
    line_width = max(1, round(scale * 0.32))

    def center(position):
        x, y = position
        return (round(origin_x + (x + 0.5) * scale), round(origin_y + (y + 0.5) * scale))

    walkable = {
        (x, y)
        for x, y in explored_tiles
        if 0 <= y < len(map_tiles)
        and 0 <= x < len(map_tiles[y])
        and map_tiles[y][x] != WALL
    }

    path_color = (143, 157, 163)
    if rooms and connections:
        # 생성기가 보관한 실제 통로 경로만 이어 그려 방 내부의 격자와 짧은 가지를 없앤다.
        for connection in connections:
            previous = None
            for position in connection.path:
                if position not in walkable:
                    previous = None
                    continue
                point = center(position)
                if previous is not None:
                    pygame.draw.line(screen, path_color, previous, point, line_width)
                else:
                    pygame.draw.circle(screen, path_color, point, max(1, line_width // 2))
                previous = point

        # 통로를 먼저 그리고 방의 면과 외곽선을 덮어 출입구 선이 방 안으로 돌출되지 않게 한다.
        for room in rooms:
            room_tiles = {
                (x, y)
                for y in range(room.top, room.bottom + 1)
                for x in range(room.left, room.right + 1)
            }
            if not room_tiles <= explored_tiles:
                continue
            room_rect = pygame.Rect(
                round(origin_x + room.left * scale),
                round(origin_y + room.top * scale),
                max(2, round(room.width * scale)),
                max(2, round(room.height * scale)),
            )
            pygame.draw.rect(screen, (24, 31, 34), room_rect)
            pygame.draw.rect(screen, path_color, room_rect, width=max(1, line_width))
    else:
        # 방 메타데이터가 없는 기존 dict 맵은 타일 연결 표현을 유지한다.
        for x, y in walkable:
            start = center((x, y))
            pygame.draw.circle(screen, path_color, start, max(1, line_width // 2))
            for neighbor in ((x + 1, y), (x, y + 1)):
                if neighbor in walkable:
                    pygame.draw.line(screen, path_color, start, center(neighbor), line_width)

    for x, y in walkable:
        tile_value = map_tiles[y][x]
        if tile_value == UP_STAIRS:
            pygame.draw.circle(screen, (225, 235, 244), center((x, y)), max(2, line_width + 1), width=1)
        elif tile_value == DOWN_STAIRS:
            point = center((x, y))
            size = max(3, line_width + 2)
            pygame.draw.line(screen, (238, 177, 75), (point[0] - size, point[1]), (point[0] + size, point[1]), 2)
            pygame.draw.line(screen, (238, 177, 75), (point[0], point[1] - size), (point[0], point[1] + size), 2)

    if player_position in explored_tiles:
        pygame.draw.circle(screen, (73, 220, 154), center(player_position), max(3, line_width + 2))
        pygame.draw.circle(screen, (222, 255, 239), center(player_position), max(3, line_width + 2), width=1)
