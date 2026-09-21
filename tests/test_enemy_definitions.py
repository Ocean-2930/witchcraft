import json
from pathlib import Path
import unittest
from unittest.mock import patch

from units import Enemy
from units.enemy_definitions import DEFINITIONS_PATH, get_enemy_definition, load_enemy_definitions


class EnemyDefinitionTests(unittest.TestCase):
    def test_spawn_uses_file_and_independent_state(self):
        definition = get_enemy_definition("basic_monster")
        first = Enemy.from_code("basic_monster", tile_x=3, tile_y=4)
        second = Enemy.from_code("basic_monster")
        self.assertEqual(first.name, "적 몬스터")
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
                             ("name", ""), ("hp", 10)):
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
