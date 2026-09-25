"""층별 아이템 난수로 드롭 표에서 최대 한 개를 생성한다."""

from items.registry import ITEM_FACTORIES
from items.equip import Equip
from items.item_instance import ItemInstance, EquipmentInstance
from units.drop_table import validate_drop_table


def checked_drop_table(table):
    table = validate_drop_table(table)
    for code, _ in table:
        if isinstance(code, str) and code not in ITEM_FACTORIES:
            raise ValueError(f"등록되지 않은 드롭 아이템: {code}")
    return table


def roll_item_drop(table, rng):
    table = checked_drop_table(table)
    total = sum(weight for _, weight in table)
    if total == 0:
        return None
    ticket = rng.random() * total
    selected = next(code for code, weight in reversed(table) if weight > 0)
    for code, weight in table:
        if ticket < weight:
            selected = code
            break
        ticket -= weight
    if selected == 0:
        return None
    if selected == 1:
        return roll_random_equipment(rng)
    item = ITEM_FACTORIES[selected]()
    return EquipmentInstance(item) if isinstance(item, Equip) else ItemInstance(item)


def roll_random_equipment(rng):
    """코드 1의 예약 분기. 랜덤 드롭 규칙은 추후 구현한다."""
    return None
