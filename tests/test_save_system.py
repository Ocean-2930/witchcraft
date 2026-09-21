import json
import os
from pathlib import Path
from uuid import uuid4
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import settings
from core.game import Game
from items import BluePotion, ItemInstance
from scenes.dungeon_scene import DungeonScene
from scenes.title_scene import TitleScene
from scenes.game_entry_scene import GameEntryScene
from scenes.pause_scene import PauseScene
from utilities.inventory import DungeonInventory
from utilities.save import GameSession, SaveManager, SaveError
from utilities.save.serializers import to_data
from units import EnemyMode


class SaveSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.temp_path = Path(__file__).resolve().parent / ("save_test_" + uuid4().hex)
        self.temp_path.mkdir()
        self.addCleanup(self.clean_files)
        self.game = Game.__new__(Game)
        self.game.running = True
        self.game.fixed_seed = None
        self.game.session = None
        self.game.dungeon_scene = None
        self.game.save_error = None
        self.game._save_elapsed = 0.0
        self.game.virtual_screen = pygame.Surface(settings.VIRTUAL_SIZE)
        self.game.save_manager = SaveManager(self.temp_path / "continue.json")
        self.game.scene = TitleScene(self.game)

    def clean_files(self):
        for path in self.temp_path.iterdir():
            path.unlink()
        self.temp_path.rmdir()

    def start(self):
        with patch.object(settings, "ENABLE_TEST_SCENARIO", True):
            dungeon = DungeonScene(self.game, dungeon_inventory=DungeonInventory(game_seed=12345))
        self.game.activate_dungeon(dungeon)
        self.assertIsNone(self.game.save_error)
        return dungeon

    def test_roundtrip_preserves_models_references_and_rng(self):
        dungeon = self.start()
        inventory = dungeon.dungeon_inventory
        potion = inventory.item_inventory.items[0]
        inventory.assign_hotbar_item("1", potion)
        inventory.equip_item(inventory.item_inventory.items[1])
        inventory.player.hp = 47
        inventory.player.buffs = [{"code": "test", "remaining": 3}]
        dungeon.ground_items[(1, 1)] = [ItemInstance(BluePotion(), stack=2)]
        dungeon.dungeon_map.event_states["000:1:1"] = {"used": True}
        enemy = dungeon.dungeon_map.enemies[0]
        enemy.ai_mode = EnemyMode.COMBAT
        enemy.last_known_player_position = (2, 2)
        enemy.hp = 7
        dungeon.combat_timer.entries.reverse()
        dungeon.combat_timer.entries[0].remaining = 37
        dungeon.combat_timer.turn_counter.value = 61
        self.assertTrue(self.game.save_progress())
        before = json.loads(json.dumps(to_data(self.game.session)))
        loaded = self.game.save_manager.load()
        self.assertEqual(before, json.loads(json.dumps(to_data(loaded))))
        self.assertIs(loaded.inventory.player, loaded.floors[1].player)
        self.assertIs(loaded.inventory.hotbar_items["1"], loaded.inventory.item_inventory.items[0])
        restored_potion = loaded.floors[1].ground_items[(1, 1)][0]
        self.assertEqual(restored_potion.stack, 2)
        self.assertEqual(restored_potion.item.get_name(), BluePotion().get_name())
        self.assertEqual(restored_potion.item.MP_RECOVERY, BluePotion.MP_RECOVERY)
        self.assertEqual(restored_potion.max_stack, BluePotion.max_stack)
        for name in ("map", "enemy", "item", "battle"):
            original = getattr(inventory, f"{name}_random_generators")
            restored = getattr(loaded.inventory, f"{name}_random_generators")
            for a, b in zip(original, restored):
                self.assertEqual(a.random(8), b.random(8))

    def test_title_continue_does_not_reinitialize_dungeon(self):
        dungeon = self.start()
        dungeon.dungeon_inventory.gold = 123
        dungeon.dungeon_inventory.player.tile_x = 2
        dungeon.dungeon_inventory.player.tile_y = 2
        count = len(dungeon.dungeon_map.enemies)
        self.game.leave_dungeon()
        title = TitleScene(self.game)
        self.game.scene = title
        self.assertIsNotNone(title.continue_button)
        title.continue_game()
        self.assertIsInstance(self.game.scene, DungeonScene)
        self.assertEqual(self.game.session.inventory.gold, 123)
        self.assertEqual(self.game.session.inventory.get_player_position(), (2, 2))
        self.assertEqual(len(self.game.scene.monsters), count)
        self.game.scene.draw()

    def test_no_save_uses_original_entry(self):
        title = self.game.scene
        self.assertIsNone(title.continue_button)
        title.start_game()
        self.assertIsInstance(self.game.scene, GameEntryScene)

    def test_new_game_cancel_then_confirm(self):
        self.start()
        self.game.leave_dungeon()
        title = TitleScene(self.game)
        self.game.scene = title
        original = self.game.save_manager.path.read_bytes()
        title.start_game()
        title.draw()
        title.overlay_scene.select(0, "취소")
        self.assertEqual(original, self.game.save_manager.path.read_bytes())
        title.start_game()
        title.overlay_scene.select(1, "삭제하고 새로 시작")
        self.assertIsInstance(self.game.scene, GameEntryScene)
        self.assertFalse(self.game.save_manager.exists())
        self.assertFalse(self.game.save_manager.backup_path.exists())

    def test_corrupt_save_stays_untouched(self):
        path = self.game.save_manager.path
        path.write_text('{"잘못된 저장":', encoding="utf-8")
        title = TitleScene(self.game)
        self.game.scene = title
        title.continue_game()
        self.assertIs(self.game.scene, title)
        self.assertIsNotNone(title.overlay_scene)
        self.assertEqual(path.read_text(encoding="utf-8"), '{"잘못된 저장":')

    def test_failed_atomic_replace_preserves_previous_save(self):
        self.start()
        previous = self.game.save_manager.path.read_bytes()
        self.game.session.inventory.gold += 1
        with patch("utilities.save.save_manager.os.replace", side_effect=OSError("test failure")):
            with self.assertRaises(SaveError):
                self.game.save_manager.save(self.game.session)
        self.assertEqual(previous, self.game.save_manager.path.read_bytes())
        self.assertEqual(list(self.temp_path.glob("*.tmp")), [])

    def test_quit_finishes_pending_move_and_saves(self):
        dungeon = self.start()
        dungeon.start_maze_move((1, 0))
        self.assertIsNotNone(dungeon.active_move)
        original = dungeon.dungeon_inventory.get_player_position()
        self.game.quit()
        self.assertFalse(self.game.running)
        loaded = self.game.save_manager.load()
        self.assertEqual(loaded.inventory.get_player_position(), (original[0] + 1, original[1]))

    def test_pause_main_saves_inventory_changes(self):
        dungeon = self.start()
        dungeon.dungeon_inventory.harmony_stones = 321
        pause = PauseScene(self.game)
        dungeon.add_overlay(pause)
        pause.go_main()
        self.assertIsInstance(self.game.scene, TitleScene)
        self.assertIsNone(self.game.session)
        self.assertEqual(self.game.save_manager.load().inventory.harmony_stones, 321)

    def test_invalid_reference_and_version_rejected(self):
        self.start()
        data = json.loads(self.game.save_manager.path.read_text(encoding="utf-8"))
        data["inventory"]["hotbar_items"]["1"] = "missing"
        self.game.save_manager.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(SaveError):
            self.game.save_manager.load()

        data["save_version"] = 999
        self.game.save_manager.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(SaveError):
            self.game.save_manager.load()

    def test_generated_new_game_and_backup(self):
        self.game.fixed_seed = 12345
        entry = GameEntryScene(self.game)
        self.game.scene = entry
        entry.start_game()
        self.assertIsInstance(self.game.scene, DungeonScene)
        self.assertIsNone(self.game.save_error)
        original = self.game.save_manager.path.read_bytes()
        self.game.session.inventory.gold += 1
        self.game.save_progress()
        self.assertEqual(original, self.game.save_manager.backup_path.read_bytes())
        loaded = self.game.save_manager.load()
        self.assertEqual(self.game.scene.dungeon_map.tiles, loaded.floors[1].tiles)
        self.assertEqual(self.game.scene.dungeon_map.event_tiles, loaded.floors[1].event_tiles)

    def test_save_failure_blocks_quit_and_delete_failure_blocks_new_game(self):
        self.start()
        with patch.object(self.game.save_manager, "save", side_effect=SaveError("쓰기 실패")):
            self.game.quit()
        self.assertTrue(self.game.running)
        self.assertIsNotNone(self.game.scene.overlay_scene)
        self.game.leave_dungeon()
        title = TitleScene(self.game)
        self.game.scene = title
        with patch.object(self.game.save_manager, "delete", side_effect=SaveError("삭제 실패")):
            title.start_new_game()
        self.assertIs(self.game.scene, title)
        self.assertTrue(self.game.save_manager.exists())
if __name__ == "__main__":
    unittest.main()
