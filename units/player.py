from __future__ import annotations

from items import Equip, SkilledEquip, SubWeapon
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

        self.weapon: SkilledEquip | None = None
        self.sub_weapon: SubWeapon | None = None
        self.armor: SkilledEquip | None = None
        self.accessory_1: SkilledEquip | None = None
        self.accessory_2: SkilledEquip | None = None
