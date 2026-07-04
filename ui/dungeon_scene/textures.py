from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parents[2] / "assets" / "images" / "dungeon_scene"

TEXTURE_SOURCES = {
    "floor": None,
    "wall": None,
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

        image = pygame.image.load(str(ASSET_ROOT / source)).convert_alpha()
        self.cache[key] = image
        return image

    def get_scaled(self, key, width, height):
        cache_key = (key, int(width), int(height))

        if cache_key in self.scaled_cache:
            return self.scaled_cache[cache_key]

        image = self.get(key)

        if image is None:
            self.scaled_cache[cache_key] = None
            return None

        scaled_image = pygame.transform.smoothscale(image, (cache_key[1], cache_key[2]))
        self.scaled_cache[cache_key] = scaled_image
        return scaled_image


DUNGEON_TEXTURES = DungeonTextureStore(TEXTURE_SOURCES)
