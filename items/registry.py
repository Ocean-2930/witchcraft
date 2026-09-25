"""드롭과 저장 복원이 공유하는 콘텐츠 생성 레지스트리."""

from .items.blue_potion import BluePotion
from .equips.weapons.simple_sword import SimpleSword


ITEM_FACTORIES = {cls.ITEM_CODE: cls for cls in (BluePotion, SimpleSword)}
