from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .unit import Unit


@dataclass
class DamageBlock:
    attacker: Unit
    defender: Unit
    base_damage: float | None = None
    skill_coefficient: float = 1.0
    flat_damage_bonus: float = 0.0
    accuracy_bonus: int = 0
    penetration_bonus: int = 0
    critical_chance_bonus: float = 0.0
    critical_damage_bonus: float = 0.0
    damage_increase_bonus: float = 0.0
    incoming_damage_reduction_bonus: float = 0.0
    outgoing_damage_modifier: float = 1.0
    incoming_damage_modifier: float = 1.0
    random_modifier: float | None = None
    use_random_modifier: bool = True

    def peek(self):
        return self.attacker.peek_damage_block(self)

    def apply(self, rng=None):
        result = self.attacker.apply_damage_block(self, rng)
        self.defender.take_damage(result.damage)
        return result
