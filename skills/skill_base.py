from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from random import Random

    from units import Unit
    from .skill_effect import SkillEffect


RangeVector = tuple[int, int]


@dataclass
class SkillBase:
    name: str
    skill_code: str = ""
    max_level: int = 1
    mp_cost: int = 0
    range_vectors: list[RangeVector] = field(default_factory=list)
    allow_diagonal: bool = False
    effects: list[SkillEffect] = field(default_factory=list)

    def __post_init__(self):
        if not self.skill_code:
            self.skill_code = self.name

    def can_use(self, caster: Unit, target: Unit | None = None):
        return (
            caster.is_alive
            and caster.mp >= self.mp_cost
            and any(effect.is_active_effect for effect in self.effects)
            and all(
                effect.can_apply(caster, target)
                for effect in self.effects
                if effect.is_active_effect
            )
        )

    def spend_cost(self, caster: Unit):
        return caster.spend_mp(self.mp_cost)

    def can_use_direction(self, direction: RangeVector) -> bool:
        direction_x, direction_y = direction
        return self.allow_diagonal or direction_x == 0 or direction_y == 0

    def get_range_vectors(self, direction: RangeVector | None = None) -> list[RangeVector]:
        if direction is None or direction == (0, -1):
            return self.range_vectors[:]
        if not self.can_use_direction(direction):
            return []

        direction_x, direction_y = direction
        right_x, right_y = -direction_y, direction_x
        oriented_vectors = []

        for offset_x, offset_y in self.range_vectors:
            forward_distance = -offset_y
            oriented_vectors.append(
                (
                    right_x * offset_x + direction_x * forward_distance,
                    right_y * offset_x + direction_y * forward_distance,
                )
            )

        return oriented_vectors

    def peek(self, caster: Unit, target: Unit | None = None):
        previews = []

        for effect in self.effects:
            if not effect.is_active_effect:
                continue

            preview = effect.peek(caster, target)

            if preview is not None:
                previews.append(preview)

        return previews

    def use(self, caster: Unit, target: Unit | None = None, rng: Random | None = None):
        if not self.can_use(caster, target):
            raise ValueError(f"{caster.name} cannot use {self.name}.")

        self.spend_cost(caster)
        return [
            effect.apply(caster, target, rng)
            for effect in self.effects
            if effect.is_active_effect
        ]
