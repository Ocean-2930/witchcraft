from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from .unit import Unit


@dataclass
class DamageBlock:
    # Attack - defense
    DEFENSE_BASE_VALUE: ClassVar[int] = 50
    EXCESS_PENETRATION_HIGH_EFFICIENCY_LIMIT: ClassVar[int] = 20
    EXCESS_PENETRATION_HIGH_EFFICIENCY_DAMAGE_RATE: ClassVar[float] = 0.015
    EXCESS_PENETRATION_LOW_EFFICIENCY_DAMAGE_RATE: ClassVar[float] = 0.005

    # Accuracy - evasion
    BASE_HIT_RATE: ClassVar[float] = 60.0
    MIN_HIT_RATE: ClassVar[float] = 20.0
    MAX_HIT_RATE: ClassVar[float] = 100.0
    HIT_RATE_HIGH_EFFICIENCY_LIMIT: ClassVar[int] = 20
    HIT_RATE_HIGH_EFFICIENCY_STEP: ClassVar[float] = 4.0
    HIT_RATE_LOW_EFFICIENCY_STEP: ClassVar[float] = 2.0

    # Critical
    MIN_CRITICAL_RATE: ClassVar[float] = -100.0
    MAX_CRITICAL_RATE: ClassVar[float] = 100.0
    BASE_CRITICAL_DAMAGE: ClassVar[float] = 75.0
    MIN_CRITICAL_DAMAGE: ClassVar[float] = 0.0
    MAX_CRITICAL_DAMAGE_REDUCTION: ClassVar[float] = 80.0
    UNDER_CRITICAL_DAMAGE_MODIFIER: ClassVar[float] = 0.25

    MIN_DAMAGE_INCREASE: ClassVar[float] = -80.0
    MAX_INCOMING_DAMAGE_REDUCTION: ClassVar[float] = 80.0
    OVERLOADED_DAMAGE_RATE: ClassVar[float] = 0.05
    MIN_RANDOM_DAMAGE_MODIFIER: ClassVar[float] = 0.9
    MAX_RANDOM_DAMAGE_MODIFIER: ClassVar[float] = 1.1

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
