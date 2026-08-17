from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parents[2] / "assets" / "images" / "dungeon_scene"

TEXTURE_SOURCES = {
    "character": "character.png",
    "character_idle": "player/idle_sheet.png",
    "player_profile": "player_profile.png",
    "floor": "floor_tile.png",
    "up_stairs": "up_stairs.png",
    "down_stairs": "down_stairs.png",
    "wall": "wall_tile.png",
    "wall_edge": "wall_edge.png",
}


class DungeonTextureStore:
    def __init__(self, sources):
        self.sources = sources
        self.cache = {}
        self.scaled_cache = {}

    def get(self, key):
        if key in self.cache:
            return self.cache[key]

        source = self.sources.get(key)

        if source is None:
            self.cache[key] = None
            return None

        image_path = ASSET_ROOT / source

        if not image_path.exists():
            self.cache[key] = None
            return None

        image = pygame.image.load(str(image_path)).convert_alpha()
        self.cache[key] = image
        return image

    def get_scaled(self, key, width, height):
        cache_key = ("cover", key, int(width), int(height))

        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        image = self.get(key)

        if image is None:
            self.scaled_cache[cache_key] = None
            return None

        scaled_image = self.scale_cover(image, cache_key[2], cache_key[3])
        self.scaled_cache[cache_key] = scaled_image
        return scaled_image

    def get_contained(self, key, width, height, trim_alpha=False):
        cache_key = ("contain", key, int(width), int(height), trim_alpha)

        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        image = self.get(key)

        if image is None:
            self.scaled_cache[cache_key] = None
            return None

        if trim_alpha:
            image = self.trim_alpha(image)

        scaled_image = self.scale_contain(image, cache_key[2], cache_key[3])
        self.scaled_cache[cache_key] = scaled_image
        return scaled_image

    def get_sheet_frames(self, key, columns, rows=1):
        cache_key = ("sheet", key, int(columns), int(rows))

        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        image = self.get(key)
        if image is None:
            self.scaled_cache[cache_key] = ()
            return ()

        frame_width = image.get_width() // columns
        frame_height = image.get_height() // rows
        frames = tuple(
            image.subsurface(
                pygame.Rect(
                    column * frame_width,
                    row * frame_height,
                    frame_width,
                    frame_height,
                )
            ).copy()
            for row in range(rows)
            for column in range(columns)
        )
        self.scaled_cache[cache_key] = frames
        return frames

    @staticmethod
    def scale_cover(image, width, height):
        source_width, source_height = image.get_size()
        scale = max(width / source_width, height / source_height)
        scaled_width = round(source_width * scale)
        scaled_height = round(source_height * scale)
        scaled_image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))

        crop_rect = pygame.Rect(0, 0, width, height)
        crop_rect.center = scaled_image.get_rect().center

        return scaled_image.subsurface(crop_rect).copy()

    @staticmethod
    def scale_contain(image, width, height):
        source_width, source_height = image.get_size()
        scale = min(width / source_width, height / source_height)
        scaled_width = round(source_width * scale)
        scaled_height = round(source_height * scale)

        return pygame.transform.smoothscale(image, (scaled_width, scaled_height))

    @staticmethod
    def trim_alpha(image):
        content_rect = image.get_bounding_rect(min_alpha=1)

        if content_rect.width == 0 or content_rect.height == 0:
            return image

        return image.subsurface(content_rect).copy()


DUNGEON_TEXTURES = DungeonTextureStore(TEXTURE_SOURCES)
