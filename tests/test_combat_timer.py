import unittest

from units import Enemy
from utilities.dungeon import CombatTimer


class CombatTimerCompletedTurnsTest(unittest.TestCase):
    def setUp(self):
        self.timer = CombatTimer()
        self.timer.register(
            Enemy("테스트 적", max_hp=100, attack_power=0),
            500,
        )

    def test_advance_exposes_no_completed_turn_below_boundary(self):
        self.timer.advance(99)

        self.assertEqual(self.timer.last_completed_turns, 0)

    def test_advance_exposes_each_crossed_boundary(self):
        self.timer.advance(99)
        self.timer.advance(201)

        self.assertEqual(self.timer.last_completed_turns, 3)
        self.assertEqual(self.timer.turn_counter.value, 0)


if __name__ == "__main__":
    unittest.main()
