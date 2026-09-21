import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from items import BluePotion, SimpleSword
from items.definitions import DEFINITIONS_PATH, load_definitions


class ItemDefinitionTests(unittest.TestCase):
    def test_content_and_effect(self):
        definitions = load_definitions(DEFINITIONS_PATH)
        potion = BluePotion()
        user = Mock()
        potion.use(user)
        user.recover_mp.assert_called_once_with(definitions["blue_potion"].mp_recovery)
        self.assertEqual(potion.get_name(), "푸른 물약")
        self.assertEqual(potion.get_description(), f"마나를 {potion.MP_RECOVERY} 회복한다.")
        self.assertEqual(SimpleSword().type, definitions["simple_sword"].equip_type)
        self.assertEqual(SimpleSword().get_name(), "평범한 철검")

    def test_invalid_definitions_are_rejected(self):
        original = json.loads(DEFINITIONS_PATH.read_text(encoding="utf-8"))
        for field, value in (("max_stack", 0), ("max_stack", True),
                             ("mp_recovery", -1), ("name", 5), ("unknown", 1)):
            with self.subTest(field=field, value=value):
                data = {code: dict(row) for code, row in original.items()}
                data["blue_potion"][field] = value
                with patch.object(Path, "read_text", return_value=json.dumps(data, ensure_ascii=False)):
                    with self.assertRaisesRegex(ValueError, "blue_potion"):
                        load_definitions(DEFINITIONS_PATH)

    def test_duplicate_keys_are_rejected(self):
        with patch.object(Path, "read_text", return_value='{"same": {}, "same": {}}'):
            with self.assertRaisesRegex(ValueError, "중복"):
                load_definitions(DEFINITIONS_PATH)
