import unittest

from utilities.dungeon import Room, get_visible_tiles


class DungeonSightTest(unittest.TestCase):
    def test_radius_is_four_tiles(self):
        map_tiles = [[0] * 11 for _ in range(11)]

        visible = get_visible_tiles(map_tiles, (5, 5), radius=4)

        self.assertIn((1, 5), visible)
        self.assertNotIn((0, 5), visible)

    def test_wall_blocks_tiles_behind_it(self):
        map_tiles = [[0, 0, 1, 0, 0]]

        visible = get_visible_tiles(map_tiles, (0, 0), radius=4)

        self.assertIn((2, 0), visible)
        self.assertNotIn((3, 0), visible)

    def test_room_reveals_all_room_floor_beyond_radius(self):
        map_tiles = [[1] * 9 for _ in range(5)]
        for y in range(1, 4):
            for x in range(1, 8):
                map_tiles[y][x] = 0
        room = Room(0, 1, 1, 7, 3)

        visible = get_visible_tiles(map_tiles, (1, 2), [room], radius=4)

        self.assertIn((7, 2), visible)


if __name__ == "__main__":
    unittest.main()
