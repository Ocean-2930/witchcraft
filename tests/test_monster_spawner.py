import unittest

from utilities.dungeon import (
    FLOOR,
    UP_STAIRS,
    WALL,
    MonsterSpawnConfig,
    MonsterSpawner,
)
from utilities.random_generator import RandomGenerator


class MonsterSpawnerTest(unittest.TestCase):
    MAP_TILES = (
        (WALL, WALL, WALL, WALL, WALL),
        (WALL, FLOOR, FLOOR, UP_STAIRS, WALL),
        (WALL, FLOOR, FLOOR, FLOOR, WALL),
        (WALL, FLOOR, FLOOR, FLOOR, WALL),
        (WALL, WALL, WALL, WALL, WALL),
    )

    def test_initial_positions_are_deterministic_and_respect_exclusions(self):
        excluded = {(1, 1), (2, 1), (1, 2)}
        first = MonsterSpawner(self.MAP_TILES, RandomGenerator("같은 시드"))
        second = MonsterSpawner(self.MAP_TILES, RandomGenerator("같은 시드"))

        first_positions = first.initial_positions(excluded)
        second_positions = second.initial_positions(excluded)

        self.assertEqual(first_positions, second_positions)
        self.assertGreaterEqual(len(first_positions), 3)
        self.assertLessEqual(len(first_positions), 5)
        self.assertTrue(set(first_positions).isdisjoint(excluded))
        self.assertTrue(
            all(self.MAP_TILES[y][x] == FLOOR for x, y in first_positions)
        )

    def test_initial_positions_use_all_candidates_when_requested_count_is_larger(self):
        config = MonsterSpawnConfig(initial_minimum=5, initial_maximum=5)
        spawner = MonsterSpawner(self.MAP_TILES, RandomGenerator(1), config)

        positions = spawner.initial_positions(
            {(1, 1), (2, 1), (1, 2), (2, 2), (3, 2)}
        )

        self.assertEqual(len(positions), 3)

    def test_periodic_positions_roll_once_per_completed_turn(self):
        config = MonsterSpawnConfig(periodic_chance=1.0, maximum_alive=10)
        spawner = MonsterSpawner(self.MAP_TILES, RandomGenerator(2), config)

        positions = spawner.periodic_positions(3, set(), alive_count=0)

        self.assertEqual(len(positions), 3)
        self.assertEqual(len(set(positions)), 3)

    def test_periodic_positions_respect_alive_cap(self):
        config = MonsterSpawnConfig(periodic_chance=1.0, maximum_alive=10)
        spawner = MonsterSpawner(self.MAP_TILES, RandomGenerator(3), config)

        positions = spawner.periodic_positions(5, set(), alive_count=9)

        self.assertEqual(len(positions), 1)

    def test_periodic_positions_can_fail_spawn_roll(self):
        config = MonsterSpawnConfig(periodic_chance=0.0)
        spawner = MonsterSpawner(self.MAP_TILES, RandomGenerator(4), config)

        self.assertEqual(spawner.periodic_positions(10, set(), alive_count=0), [])


if __name__ == "__main__":
    unittest.main()
