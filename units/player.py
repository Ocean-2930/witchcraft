from __future__ import annotations

from .unit import Unit


class Player(Unit):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            max_hp=100,
            attack_power=100,
            max_mp=30,
            accuracy=5,
            hp=100,
            mp=0,
        )
