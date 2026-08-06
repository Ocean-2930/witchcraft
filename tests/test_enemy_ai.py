import unittest

from scenes.dungeon_scene import DungeonScene
from units import Enemy, EnemyMode
from utilities.dungeon import CombatTimer


class EnemyAiStateTest(unittest.TestCase):
    def test_enemy_starts_in_guard_mode(self):
        enemy = Enemy("적", max_hp=10, attack_power=1)

        self.assertEqual(enemy.ai_mode, EnemyMode.GUARD)
        self.assertFalse(enemy.is_in_combat)

    def test_entering_combat_clears_patrol_target(self):
        enemy = Enemy("적", max_hp=10, attack_power=1, patrol_target=(3, 4))

        enemy.set_ai_mode(EnemyMode.COMBAT)

        self.assertTrue(enemy.is_in_combat)
        self.assertIsNone(enemy.patrol_target)

    def test_elapsed_player_action_runs_each_ready_enemy_repeatedly(self):
        scene = DungeonScene.__new__(DungeonScene)
        scene.combat_timer = CombatTimer()
        enemies = [
            Enemy("적 1", max_hp=10, attack_power=1),
            Enemy("적 2", max_hp=10, attack_power=1),
        ]
        for enemy in enemies:
            scene.combat_timer.register(enemy, 100)
        acted = []
        scene.run_monster_turn = acted.append

        completed_turns = scene.advance_monster_turns(250)

        self.assertEqual(acted, [enemies[0], enemies[1], enemies[0], enemies[1]])
        self.assertEqual(completed_turns, 2)
        self.assertEqual(
            [scene.combat_timer.get_entry(enemy).remaining for enemy in enemies],
            [50, 50],
        )


if __name__ == "__main__":
    unittest.main()
