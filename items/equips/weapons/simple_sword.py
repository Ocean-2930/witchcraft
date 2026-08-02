from items.equip import Equip
from items.skilled_equip import SkilledEquip


class SimpleSword(SkilledEquip):
    ITEM_CODE = "simple_sword"

    def __init__(self):
        super().__init__(
            type=Equip.TYPE_WEAPON,
            item_code=self.ITEM_CODE,
        )

    def get_name(self) -> str:
        return "평범한 철검"

    def get_flavor_text(self) -> str:
        return "간단하게 만들어진 철검이다"
