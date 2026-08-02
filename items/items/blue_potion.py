from typing import ClassVar

from ..usable_item import UsableItem


class BluePotion(UsableItem):
    ITEM_CODE: ClassVar[str] = "blue_potion"
    MP_RECOVERY: ClassVar[int] = 5
    max_stack: ClassVar[int] = 5

    def __init__(self):
        super().__init__(item_code=self.ITEM_CODE)

    def use(self, user, target=None, rng=None):
        return user.recover_mp(self.MP_RECOVERY)

    def get_name(self) -> str:
        return "푸른 물약"

    def get_description(self) -> str:
        return f"마나를 {self.MP_RECOVERY} 회복한다."

    def get_flavor_text(self) -> str:
        return "푸른 마력이 담긴 작은 물약이다."
