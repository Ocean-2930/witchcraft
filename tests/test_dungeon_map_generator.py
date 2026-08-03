from collections import deque
import unittest

from dungeon import DungeonMapGenerator, WALL
from utilities import RandomGenerator
from ui.game_entry_scene.seed_input import SeedInput


class DungeonMapGeneratorTest(unittest.TestCase):
    def generate(self, seed: int):
        return DungeonMapGenerator(RandomGenerator(seed), seed).generate()

    def test_same_seed_reproduces_every_result(self):
        self.assertEqual(self.generate(230519), self.generate(230519))

    def test_seed_input_formats_and_reads_hyphenated_values(self):
        seed_input = SeedInput.__new__(SeedInput)
        seed_input._digits = ""
        seed_input.error_text = ""
        seed_input.text = "1234-5678-9012-3456"
        self.assertEqual(seed_input.text, "1234-5678-9012-3456")
        self.assertEqual(seed_input.get_seed(), 1234567890123456)

        seed_input.text = "1234567890123456"
        self.assertEqual(seed_input.text, "1234-5678-9012-3456")
        self.assertEqual(seed_input.get_seed(), 1234567890123456)

    def test_seed_input_pads_short_values_on_the_left(self):
        seed_input = SeedInput.__new__(SeedInput)
        seed_input._digits = ""
        seed_input.error_text = ""
        seed_input.text = "1234-5678"
        self.assertEqual(seed_input.text, "0000-0000-1234-5678")
        self.assertEqual(seed_input.get_seed(), 12345678)

        seed_input.clear()
        self.assertEqual(seed_input.text, "0000-0000-0000-0000")
        with self.assertRaises(ValueError):
            seed_input.get_seed()

    def test_held_backspace_waits_then_repeats(self):
        seed_input = SeedInput.__new__(SeedInput)
        seed_input._digits = "1234567890123456"
        seed_input.error_text = ""
        seed_input.backspace_elapsed = 0.0
        seed_input.backspace_repeat_elapsed = 0.0
        seed_input.update_backspace_repeat(0.39)
        self.assertEqual(len(seed_input._digits), 16)
        seed_input.update_backspace_repeat(0.06)
        self.assertEqual(len(seed_input._digits), 15)
        seed_input.update_backspace_repeat(0.1)
        self.assertEqual(len(seed_input._digits), 13)

    def test_generated_maps_meet_room_and_route_contracts(self):
        for seed in range(1, 41):
            with self.subTest(seed=seed):
                dungeon_map = self.generate(seed)
                rooms = dungeon_map.rooms
                self.assertGreaterEqual(len(rooms), 8)
                self.assertLessEqual(len(rooms), 12)
                self.assertGreaterEqual(len(dungeon_map.connections), len(rooms))

                for room in rooms:
                    self.assertGreaterEqual(min(room.width, room.height), 2)
                    self.assertGreaterEqual(max(room.width, room.height), 4)
                    self.assertLessEqual(max(room.width, room.height), 8)

                for index, room in enumerate(rooms):
                    distances = [
                        DungeonMapGenerator.room_distance(room, other)
                        for other_index, other in enumerate(rooms)
                        if other_index != index
                    ]
                    self.assertGreaterEqual(min(distances), 3)
                    self.assertLessEqual(min(distances), 10)

                stair_room_ids = {
                    room.room_id
                    for room in rooms
                    if room.center in (dungeon_map.up_stairs, dungeon_map.down_stairs)
                }
                self.assertEqual(len(stair_room_ids), 2)
                large_normal_rooms = [
                    room
                    for room in rooms
                    if room.is_large and room.room_id not in stair_room_ids
                ]
                self.assertGreaterEqual(len(large_normal_rooms), 3)
                self.assertNotIn(dungeon_map.hub_room_id, stair_room_ids)

                hub_connections = [
                    connection
                    for connection in dungeon_map.connections
                    if connection.room_a == dungeon_map.hub_room_id
                    or connection.room_b == dungeon_map.hub_room_id
                ]
                hub_sides = {
                    connection.side_a
                    if connection.room_a == dungeon_map.hub_room_id
                    else connection.side_b
                    for connection in hub_connections
                }
                self.assertGreaterEqual(len(hub_connections), 3)
                self.assertGreaterEqual(len(hub_sides), 3)

                self.assertTrue(self.is_reachable(dungeon_map, dungeon_map.down_stairs))
                for room in rooms:
                    self.assertTrue(self.is_reachable(dungeon_map, room.center))

                self.assertTrue(all(tile == WALL for tile in dungeon_map.tiles[0]))
                self.assertTrue(all(tile == WALL for tile in dungeon_map.tiles[-1]))
                self.assertTrue(all(row[0] == WALL and row[-1] == WALL for row in dungeon_map.tiles))

    @staticmethod
    def is_reachable(dungeon_map, target):
        queue = deque([dungeon_map.up_stairs])
        visited = {dungeon_map.up_stairs}
        while queue:
            x, y = queue.popleft()
            if (x, y) == target:
                return True
            for next_x, next_y in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= next_y < dungeon_map.height and 0 <= next_x < dungeon_map.width):
                    continue
                if dungeon_map.tiles[next_y][next_x] == WALL:
                    continue
                if (next_x, next_y) in visited:
                    continue
                visited.add((next_x, next_y))
                queue.append((next_x, next_y))
        return False


if __name__ == "__main__":
    unittest.main()
