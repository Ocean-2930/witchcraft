from items.equip import Equip
from items.skilled_equip import SkilledEquip
from skills import SkillInstance, STAT_PASSIVE_SKILLS


class SimpleSword(SkilledEquip):
    ITEM_CODE = "simple_sword"

    def __init__(self):
        skill_levels = (3, 2, 5, 4, 2)
        super().__init__(
            type=Equip.TYPE_WEAPON,
            item_code=self.ITEM_CODE,
            skills=[
                SkillInstance(skill, level=level)
                for skill, level in zip(
                    STAT_PASSIVE_SKILLS[:5],
                    skill_levels,
                )
            ],
        )

    def get_name(self) -> str:
        return "평범한 철검"

    def get_flavor_text(self) -> str:
        return "간단하게 만들어진 철검이다"
