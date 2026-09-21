from items.equip import Equip
from items.skilled_equip import SkilledEquip
from items.definitions import get_item_definition


class SimpleSword(SkilledEquip):
    ITEM_CODE = "simple_sword"
    definition = get_item_definition(ITEM_CODE)
    max_stack = definition.max_stack
    if definition.equip_type != Equip.TYPE_WEAPON:
        raise ValueError("simple_sword의 equip_type은 weapon이어야 합니다.")

    def __init__(self):
        super().__init__(
            type=self.definition.equip_type,
            item_code=self.ITEM_CODE,
        )
