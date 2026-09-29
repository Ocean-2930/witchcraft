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
from utilities.save.serializers import to_data, from_data
from units import EnemyMode


class SaveSystemTests(unittest.TestCase):
    def test_motion_anchor_offsets_and_mirroring(self):
        dungeon = self.start()
        marker = dungeon.player_marker
        marker.motion_settings = {"idle": {
            "scale": 1.25, "anchor": [220, 418], "offset": [4, -2],
            "frame_offsets": [[2, 3]] * 8,
        }}
        marker.set_animation("idle")
        image = marker.get_current_texture_image()
        self.assertEqual(image.get_width(), round(marker.image.get_width() * 1.25))
        rect = marker.get_texture_rect(image)
        foot_y = marker.rect.centery + dungeon.FLOOR_TILE_HEIGHT / 2 - marker.TILE_BOTTOM_MARGIN
        self.assertAlmostEqual(rect.left + (220 - 6) * rect.width / 512, marker.rect.centerx, delta=0.5)
        self.assertAlmostEqual(rect.top + (418 - 1) * rect.height / 512, foot_y, delta=0.5)
        marker.set_facing_left(True)
        flipped = marker.get_current_texture_image()
        left_rect = marker.get_texture_rect(flipped)
        self.assertEqual(flipped.get_size(), image.get_size())
        self.assertAlmostEqual(left_rect.left + (512 - 220 + 6) * left_rect.width / 512,
                               marker.rect.centerx, delta=0.5)

    def test_character_motion_config_validation_and_defaults(self):
        from units.character_definitions import load_character_motion_settings
        path = self.temp_path / "characters.json"
        row = {"code": "test", "name": "테스트"}
        with patch("units.character_definitions.DEFINITIONS_PATH", path):
            path.write_text(json.dumps({"test": row}), encoding="utf-8")
            self.assertEqual(load_character_motion_settings("test"), {})
            for config in ({"scale": 0}, {"scale": True}, {"scale": float("nan")},
                           {"anchor": [1]}, {"offset": [0, float("inf")]},
                           {"frame_offsets": [[0, 0]]}, {"scales": 1}):
                row["motions"] = {"attack": config}
                path.write_text(json.dumps({"test": row}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_character_motion_settings("test")

    def test_skill_motion_definition_roundtrip(self):
        from skills import AttackSkill, SkillInstance, STAT_PASSIVE_SKILLS
        from skills.active_skill import ActiveSkill
        from utilities.save.serializers import skill_data, read_skill

        self.assertIsNone(ActiveSkill("no motion").motion)
        for definition in (AttackSkill(), STAT_PASSIVE_SKILLS[0]):
            restored = read_skill(skill_data(SkillInstance(definition, 1)))
            self.assertEqual(restored.skill.motion, definition.motion)
        self.assertEqual(read_skill({"code": "attack", "level": 1, "stack": 1}).skill.motion, "attack")

    def test_skill_motion_plays_once_and_missing_sheet_does_not_block(self):
        dungeon = self.start()
        marker = dungeon.player_marker
        frames = tuple(pygame.Surface((32, 32), pygame.SRCALPHA) for _ in range(8))
        with patch("ui.dungeon_scene.player_marker.get_character_textures") as textures:
            textures.return_value.get_sheet_frames.return_value = frames
            self.assertFalse(marker.play_motion(None))
            self.assertTrue(marker.play_motion("attack"))
            self.assertFalse(marker.play_motion("attack"))
            marker.update(0.175, {}, None, 0)
            self.assertTrue(marker.is_playing_motion)
            self.assertEqual(marker.index, 3)
            marker.update(1.0, {}, None, 0)
            self.assertFalse(marker.is_playing_motion)
            self.assertEqual(marker.current, "idle")
            self.assertTrue(marker.play_motion("attack"))
            self.assertEqual(marker.index, 0)
            marker.update(1.0, {}, None, 0)
            textures.return_value.get_sheet_frames.return_value = ()
            self.assertFalse(marker.play_motion("missing"))
            self.assertFalse(marker.is_playing_motion)

    def test_successful_cast_starts_motion_but_failed_cast_does_not(self):
        from skills import AttackSkill
        dungeon = self.start()
        skill = AttackSkill()
        with patch.object(dungeon, "get_hotbar_action_skill", return_value=skill), \
             patch.object(dungeon.dungeon_inventory, "get_hotbar_item", return_value=None), \
             patch.object(dungeon.dungeon_inventory, "get_hotbar_skill", return_value=None), \
             patch.object(dungeon.dungeon_inventory, "use_skill", return_value=None) as cast, \
             patch.object(dungeon.player_marker, "play_motion", return_value=True) as motion:
            dungeon.use_hotbar_skill("1", (1, 0))
            motion.assert_not_called()
            cast.return_value = []
            dungeon.use_hotbar_skill("1", (1, 0))
            motion.assert_called_once_with("attack")
            motion.reset_mock()
            skill.motion = None
            dungeon.use_hotbar_skill("1", (1, 0))
            self.assertTrue(dungeon.last_skill_call["used"])
            motion.assert_called_once_with(None)

    def test_motion_blocks_followup_gameplay_input(self):
        from unittest.mock import PropertyMock
        from ui.dungeon_scene.player_marker import PlayerMarkerRenderer
        dungeon = self.start()
        events = {key: {"keydown": False, "keyup": False, "status": False}
                  for key in range(1024)}
        # Use the project's actual input constants, including non-integer keys.
        for value in vars(settings).values():
            if isinstance(value, (str, int)):
                events.setdefault(value, {"keydown": False, "keyup": False, "status": False})
        with patch.object(PlayerMarkerRenderer, "is_playing_motion", new_callable=PropertyMock, return_value=True), \
             patch.object(dungeon, "update_hotbar_input") as hotbar, \
             patch.object(dungeon, "try_start_maze_move") as movement, \
             patch.object(dungeon, "update_hovered_monster"), \
             patch.object(dungeon, "block_hotbar_input_during_move"):
            dungeon.scene_update(0.01, events, None, 0)
            self.assertFalse(dungeon.can_use_movement_input(events))
            hotbar.assert_not_called()
            movement.assert_not_called()

    def test_character_name_new_game_save_continue_and_resave(self):
        entry = GameEntryScene(self.game)
        entry.character_name = "valen"
        self.game.scene = entry
        entry.start_game()
        self.assertIsNone(self.game.save_error)
        self.assertEqual(self.game.session.inventory.character_name, entry.character_name)
        player = self.game.session.inventory.player
        player.name = "별빛"
        player.hp = 47
        self.game.save_progress()
        self.game.leave_dungeon()
        title = TitleScene(self.game)
        self.game.scene = title
        title.continue_game()
        inventory = self.game.session.inventory
        self.assertEqual(inventory.character_name, "valen")
        self.assertEqual((inventory.player.name, inventory.player.hp), ("별빛", 47))
        self.assertIs(self.game.session.floors[1].player, inventory.player)
        self.assertTrue(any(e.unit is inventory.player for e in self.game.session.floors[1].combat_timer.entries))
        inventory.character_name = "renea"
        self.game.save_progress()
        self.assertEqual(self.game.save_manager.load().inventory.character_name, "renea")

    def test_legacy_character_name_and_invalid_settings(self):
        self.start()
        for version in (1, 2, 3, 4):
            data = to_data(self.game.session)
            data["save_version"] = version
            del data["inventory"]["character_name"]
            loaded = from_data(data)
            self.assertEqual(loaded.inventory.character_name, "renea")
            self.assertEqual(to_data(loaded)["save_version"], 5)
        for info in (None, {}, "", "sample", "unknown", 1, True, " valen "):
            data = to_data(self.game.session)
            data["inventory"]["character_name"] = info
            with self.assertRaises(ValueError):
                from_data(data)
        data = to_data(self.game.session)
        data["save_version"] = 4
        del data["inventory"]["character_name"]
        data["inventory"]["character_info"] = {"character_type": "human", "job": "adventurer"}
        self.assertEqual(from_data(data).inventory.character_name, "renea")
        data = to_data(self.game.session)
        del data["inventory"]["character_name"]
        with self.assertRaises(KeyError):
            from_data(data)

    def test_equipped_actions_synthesis_and_save(self):
        from scenes.inventory_scene import InventoryScene
        from items import EquipmentInstance, SimpleSword

        dungeon = self.start()
        inventory = dungeon.dungeon_inventory
        main = EquipmentInstance(SimpleSword())
        material = EquipmentInstance(SimpleSword())
        inventory.add_item(main)
        inventory.add_item(material)
        self.assertTrue(inventory.equip_item(main))
        inventory.harmony_stones = 10000
        menu = InventoryScene(self.game)
        dungeon.add_overlay(menu)
        menu.equipment_slots[0].on_left_click()
        self.assertIs(menu.get_selected_item(), main)
        self.assertTrue(menu.popup_buttons["unequip"].visible)
        self.assertFalse(menu.popup_buttons["equip"].visible)
        self.assertFalse(menu.popup_buttons["discard"].visible)
        menu.open_synthesis()
        synthesis = menu.overlay_scene
        self.assertIs(synthesis.main_item, main)
        synthesis.select_material(inventory.item_inventory.find_item_index(material))
        synthesis.synthesize()
        self.assertIs(inventory.weapon, main)
        self.assertFalse(inventory.item_inventory.contains(material))
        loaded = from_data(to_data(self.game.session))
        self.assertEqual(loaded.inventory.weapon.stat_rows, main.stat_rows)
        self.assertEqual(loaded.inventory.harmony_stones, inventory.harmony_stones)
        synthesis.exit_scene()
        menu.equipment_slots[0].on_left_click()
        menu.unequip_selected_item()
        self.assertIsNone(inventory.weapon)
        self.assertTrue(inventory.item_inventory.contains(main))

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

    def test_enemy_drops_and_ground_equipment_roundtrip(self):
        from items import EquipmentInstance
        dungeon = self.start()
        for enemy_code, item_code in (("goblin", "simple_sword"), ("basic_monster", "blue_potion")):
            dungeon.create_monster(3, 4, enemy_code)
            monster = dungeon.monsters[-1]
            enemy = monster["unit"]
            loaded = from_data(to_data(self.game.session))
            self.assertEqual(loaded.floors[1].enemies[-1].drop_items, enemy.drop_items)
            before = len(dungeon.ground_items.get((3, 4), []))
            enemy.hp = 0
            self.assertTrue(dungeon.remove_monster(monster))
            self.assertFalse(dungeon.remove_monster(monster))
            self.assertEqual(len(dungeon.ground_items[(3, 4)]), before + 1)
            dropped = dungeon.ground_items[(3, 4)][-1]
            self.assertEqual(dropped.item.item_code, item_code)
            self.assertEqual(dropped.stack, 1)
            if isinstance(dropped, EquipmentInstance):
                dropped.stat_rows[0] = None
            loaded = from_data(to_data(self.game.session))
            restored = loaded.floors[1].ground_items[(3, 4)][-1]
            self.assertEqual(type(restored), type(dropped))
            self.assertEqual(restored.item.item_code, item_code)
            if isinstance(dropped, EquipmentInstance):
                self.assertEqual(restored.stat_rows, dropped.stat_rows)
            original_rng = dungeon.dungeon_inventory.get_item_random_generator(1)
            loaded_rng = loaded.inventory.get_item_random_generator(1)
            from utilities.dungeon.item_drops import roll_item_drop
            table = (("simple_sword", 2), ("blue_potion", 3), (0, 4), (1, 1))
            def codes(rng):
                return [None if item is None else item.item.item_code
                        for item in [roll_item_drop(table, rng) for _ in range(30)]]
            self.assertEqual(codes(original_rng), codes(loaded_rng))

    def test_legacy_drop_tables_and_invalid_drop_tables(self):
        self.start()
        data = to_data(self.game.session)
        data["save_version"] = 2
        for floor in data["floors"].values():
            for enemy in floor["enemies"]:
                enemy["unit"].pop("drop_items")
        self.assertTrue(all(not enemy.drop_items for enemy in from_data(data).floors[1].enemies))
        for table in ([["missing", 1]], [[0, -1]], [[True, 1]], [[0, float("nan")]]):
            invalid = to_data(self.game.session)
            next(iter(invalid["floors"].values()))["enemies"][0]["unit"]["drop_items"] = table
            with self.assertRaises(ValueError):
                from_data(invalid)

    def test_enemy_rewards_paid_once_and_saved(self):
        dungeon = self.start()
        monster = dungeon.monsters[0]
        enemy = monster["unit"]
        enemy.drop_gold = 37
        enemy.drop_harmony_stones = 4
        restored = from_data(to_data(self.game.session))
        self.assertEqual(restored.floors[1].enemies[0].drop_gold, 37)
        self.assertEqual(restored.floors[1].enemies[0].drop_harmony_stones, 4)
        gold = dungeon.dungeon_inventory.get_stat().get_gold_drop_amount(37)
        before = (dungeon.dungeon_inventory.gold, dungeon.dungeon_inventory.harmony_stones)
        enemy.hp = 0
        self.assertTrue(dungeon.remove_monster(monster))
        self.assertFalse(dungeon.remove_monster(monster))
        self.assertEqual(dungeon.combat_logs[-3:], [f"{enemy.name}를 쓰러뜨렸다", f"골드를 {gold} 얻었다", "조화석을 4 얻었다"])
        loaded = from_data(to_data(self.game.session))
        self.assertEqual((loaded.inventory.gold, loaded.inventory.harmony_stones), (before[0] + gold, before[1] + 4))
        self.assertEqual(len(loaded.floors[1].enemies), len(dungeon.monsters))

    def test_legacy_enemy_rewards_and_invalid_rewards(self):
        self.start()
        data = to_data(self.game.session)
        data["save_version"] = 1
        for floor in data["floors"].values():
            for enemy in floor["enemies"]:
                enemy["unit"].pop("drop_items")
                enemy["unit"].pop("drop_gold")
                enemy["unit"].pop("drop_harmony_stones")
        loaded = from_data(data)
        self.assertEqual(loaded.floors[1].enemies[0].drop_gold, 0)
        self.assertEqual(loaded.floors[1].enemies[0].drop_harmony_stones, 0)
        for value in (-1, True, 1.5):
            invalid = to_data(self.game.session)
            next(iter(invalid["floors"].values()))["enemies"][0]["unit"]["drop_gold"] = value
            with self.assertRaises(ValueError):
                from_data(invalid)

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

    def test_saved_enemy_does_not_reload_spawn_definition(self):
        dungeon = self.start()
        enemy = dungeon.dungeon_map.enemies[0]
        enemy.name = "저장된 적"
        enemy.max_hp = 222
        enemy.hp = 17
        enemy.attack_power = 31
        snapshot = to_data(self.game.session)
        with patch("units.enemy.get_enemy_definition", side_effect=AssertionError("생성 정의 재적용")):
            restored = from_data(snapshot).floors[1].enemies[0]
        self.assertEqual((restored.name, restored.max_hp, restored.hp, restored.attack_power),
                         ("저장된 적", 222, 17, 31))

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
