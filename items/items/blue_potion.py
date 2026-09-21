from typing import ClassVar

from ..usable_item import UsableItem
from ..definitions import get_item_definition


class BluePotion(UsableItem):
    ITEM_CODE: ClassVar[str] = "blue_potion"
    definition = get_item_definition(ITEM_CODE)
    if definition.mp_recovery is None:
        raise ValueError("blue_potion 정의에 mp_recovery가 필요합니다.")
    MP_RECOVERY: ClassVar[int] = definition.mp_recovery
    max_stack: ClassVar[int] = definition.max_stack

    def __init__(self):
        super().__init__(item_code=self.ITEM_CODE)

    def use(self, user, target=None, rng=None):
        return user.recover_mp(self.MP_RECOVERY)

    def get_use_log(self, result) -> str | None:
        return f"마력을 {result} 회복했다."
