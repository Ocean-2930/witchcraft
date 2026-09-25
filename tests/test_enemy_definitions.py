import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from units import Enemy
from units.enemy_definitions import DEFINITIONS_PATH, get_enemy_definition, load_enemy_definitions
from units.enemy_definitions import SPAWN_ENEMY_CODES
from utilities.random_generator import RandomGenerator


class EnemyDefinitionTests(unittest.TestCase):
    def test_weighted_drop_boundaries(self):
        from utilities.dungeon.item_drops import roll_item_drop
        table = (("blue_potion", 1), (0, 3), ("simple_sword", 0))
        self.assertEqual(roll_item_drop(table, Mock(random=lambda: 0)).item.item_code, "blue_potion")
        self.assertIsNone(roll_item_drop(table, Mock(random=lambda: 0.25)))
        self.assertIsNone(roll_item_drop(table, Mock(random=lambda: 0.999)))
        rng = Mock()
        self.assertIsNone(roll_item_drop(((0, 0),), rng))
        rng.random.assert_not_called()
        self.assertIsNone(roll_item_drop(((1, 10),), RandomGenerator(123)))

    def test_random_spawn_repeats_after_rng_restore(self):
        from scenes.dungeon_scene import DungeonScene

        def make_scene(rng):
            scene = Mock()
            scene.enemy_random = rng
            scene.attach_monster.side_effect = lambda unit: unit
            return scene

        original = make_scene(RandomGenerator(12345))
        for _ in range(7):
            DungeonScene.create_monster(original, 2, 3)
        restored = make_scene(RandomGenerator.from_state(original.enemy_random.current_random))
        first = [DungeonScene.create_monster(original, 2, 3) for _ in range(60)]
        second = [DungeonScene.create_monster(restored, 2, 3) for _ in range(60)]
        self.assertEqual([unit.name for unit in first], [unit.name for unit in second])
        self.assertEqual({unit.name for unit in first},
                         {get_enemy_definition(code)["name"] for code in SPAWN_ENEMY_CODES})
        self.assertTrue(all((unit.tile_x, unit.tile_y) == (2, 3) for unit in first))
        state = original.enemy_random.current_random
        unit = DungeonScene.create_monster(original, 4, 5, "goblin")
        self.assertEqual(unit.name, "고블린")
        self.assertEqual(original.enemy_random.current_random, state)

    def test_spawn_uses_file_and_independent_state(self):
        definition = get_enemy_definition("basic_monster")
        first = Enemy.from_code("basic_monster", tile_x=3, tile_y=4)
        second = Enemy.from_code("basic_monster")
        self.assertEqual(first.name, "슬라임")
        self.assertEqual(first.hp, definition["max_hp"])
        self.assertEqual((first.tile_x, first.tile_y), (3, 4))
        first.take_damage(7)
        first.buffs.append({"test": True})
        self.assertEqual(second.hp, definition["max_hp"])
        self.assertEqual(second.buffs, [])
        with self.assertRaises(TypeError):
            definition["max_hp"] = 1

    def test_invalid_definitions(self):
        for field, value in (("max_hp", 0), ("max_mp", -1), ("attack_power", True),
                             ("move_speed", 4), ("critical_chance", float("nan")),
                             ("name", ""), ("hp", 10), ("drop_gold", -1), ("drop_harmony_stones", True), ("drop_gold", 1.5)):
            with self.subTest(field=field):
                row = {"name": "적", "max_hp": 100, "attack_power": 0, field: value}
                with patch.object(Path, "read_text", return_value=json.dumps({"bad": row})):
                    with self.assertRaisesRegex(ValueError, "bad"):
                        load_enemy_definitions(DEFINITIONS_PATH)

    def test_duplicate_and_unknown_codes(self):
        with patch.object(Path, "read_text", return_value='{"same": {}, "same": {}}'):
            with self.assertRaisesRegex(ValueError, "중복"):
                load_enemy_definitions(DEFINITIONS_PATH)
        with self.assertRaisesRegex(ValueError, "missing"):
            Enemy.from_code("missing")
