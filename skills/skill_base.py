from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import pygame

from utilities import load_code_sprite

if TYPE_CHECKING:
    from random import Random

    from units import Unit
    from .skill_effect import SkillEffect


RangeVector = tuple[int, int]


class SkillDirectionStatus(Enum):
    READY = auto()
    MISSING = auto()
    UNEXPECTED = auto()
    INVALID = auto()


@dataclass(frozen=True)
class SkillTargetingInput:
    origin: RangeVector
    direction: RangeVector | None


@dataclass
class SkillBase:
    ICON_DIRECTORY: ClassVar[Path] = (
        Path(__file__).resolve().parents[1] / "assets" / "images" / "skills"
    )
    _icon_cache: ClassVar[dict[str, pygame.Surface]] = {}

    name: str
    skill_code: str = ""
    description: str = ""
    max_level: int | None = 1
    allow_negative_level: bool = False
    mp_cost: int = 0
    range_vectors: list[RangeVector] = field(default_factory=list)
    requires_direction: bool = True
    allow_diagonal: bool = False
    effects: list[SkillEffect] = field(default_factory=list)

    def __post_init__(self):
        if self.max_level is not None and self.max_level < 0:
            raise ValueError("max_level은 0 이상이거나 None이어야 합니다.")
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

    def get_icon(self) -> pygame.Surface | None:
        return load_code_sprite(
            self.ICON_DIRECTORY,
            self.skill_code,
            self._icon_cache,
        )

    def get_description(self, level: int) -> str:
        return self.description

    def has_icon(self) -> bool:
        return bool(
            self.skill_code
            and (self.ICON_DIRECTORY / f"{self.skill_code}.png").is_file()
        )

    def can_use_direction(self, direction: RangeVector) -> bool:
        direction_x, direction_y = direction
        if direction == (0, 0):
            return False
        if direction_x not in (-1, 0, 1) or direction_y not in (-1, 0, 1):
            return False

        return self.allow_diagonal or direction_x == 0 or direction_y == 0

    def check_direction(self, direction: RangeVector | None) -> SkillDirectionStatus:
        if direction is None:
            return (
                SkillDirectionStatus.MISSING
                if self.requires_direction
                else SkillDirectionStatus.READY
            )
        if not self.requires_direction:
            return SkillDirectionStatus.UNEXPECTED
        if not self.can_use_direction(direction):
            return SkillDirectionStatus.INVALID

        return SkillDirectionStatus.READY

    def accepts_direction(self, direction: RangeVector | None) -> bool:
        return self.check_direction(direction) is SkillDirectionStatus.READY

    def get_range_vectors(self, direction: RangeVector | None = None) -> list[RangeVector]:
        if not self.accepts_direction(direction):
            return []
        if direction is None or direction == (0, -1):
            return self.range_vectors[:]

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

    def get_target_tiles(self, targeting: SkillTargetingInput) -> list[RangeVector]:
        origin_x, origin_y = targeting.origin
        return [
            (origin_x + offset_x, origin_y + offset_y)
            for offset_x, offset_y in self.get_range_vectors(targeting.direction)
        ]

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
