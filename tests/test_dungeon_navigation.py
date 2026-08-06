import unittest

from utilities.dungeon import find_shortest_path


class DungeonNavigationTest(unittest.TestCase):
    def test_returns_shortest_eight_direction_path_without_start(self):
        map_tiles = [[0] * 4 for _ in range(4)]

        path = find_shortest_path(map_tiles, (0, 0), (3, 3))

        self.assertEqual(path, [(1, 1), (2, 2), (3, 3)])

    def test_routes_around_walls_and_blocked_positions(self):
        map_tiles = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ]

        path = find_shortest_path(map_tiles, (0, 1), (3, 1), {(0, 0)})

        self.assertTrue(path)
        self.assertNotIn((0, 0), path)
        self.assertNotIn((1, 1), path)

    def test_does_not_cross_closed_diagonal_corner(self):
        map_tiles = [[0, 1], [1, 0]]

        self.assertEqual(find_shortest_path(map_tiles, (0, 0), (1, 1)), [])

    def test_returns_empty_path_when_goal_is_unreachable(self):
        map_tiles = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]

        self.assertEqual(find_shortest_path(map_tiles, (0, 1), (2, 1)), [])


if __name__ == "__main__":
    unittest.main()
