from __future__ import annotations

from ..equip import Equip, SubWeapon
from ..equip.skilled_equip import SkilledEquip
from .unit import Unit


class Player(Unit):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            max_hp=100,
            attack_power=0,
            max_mp=30,
            accuracy=5,
            hp=100,
            mp=0,
        )

        self.weapon: SkilledEquip = SkilledEquip(Equip.TYPE_WEAPON)
        self.sub_weapon: SubWeapon = SubWeapon(Equip.TYPE_SUB_WEAPON)
        self.armor: SkilledEquip = SkilledEquip(Equip.TYPE_ARMOR)
        self.accessory_1: SkilledEquip = SkilledEquip(Equip.TYPE_ACCESSORY)
        self.accessory_2: SkilledEquip = SkilledEquip(Equip.TYPE_ACCESSORY)
