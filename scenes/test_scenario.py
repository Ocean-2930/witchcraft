from typing import TYPE_CHECKING

from items import BluePotion, Equip, ItemInstance, SkilledEquip
from inventory import LearnableSkill
from skills import AttackSkill, SkillInstance, STAT_PASSIVE_SKILLS

if TYPE_CHECKING:
    from .dungeon_scene import DungeonScene


def senario(scene: "DungeonScene"):
    """개발 중 던전의 초기 상태를 변경하는 테스트 시나리오."""
    scene.dungeon_inventory.add_item(ItemInstance(BluePotion(), stack=3))
    scene.dungeon_inventory.add_item(
        ItemInstance(
            SkilledEquip(
                Equip.TYPE_WEAPON,
                item_code="simple_sword",
            )
        )
    )
    for tier in (1, 2):
        scene.dungeon_inventory.add_learnable_skill(
            LearnableSkill(
                tier=tier,
                skill=SkillInstance(
                    AttackSkill(),
                    level=0,
                ),
                max_level=3,
            )
        )
        for passive_skill in STAT_PASSIVE_SKILLS[:4]:
            scene.dungeon_inventory.add_learnable_skill(
                LearnableSkill(
                    tier=tier,
                    skill=SkillInstance(
                        passive_skill,
                        level=0,
                    ),
                    max_level=3,
                )
            )
        scene.dungeon_inventory.set_tier_skill_points(tier, 50)
    scene.dungeon_inventory.add_learnable_skill(
        LearnableSkill(
            tier=8,
            skill=SkillInstance(
                STAT_PASSIVE_SKILLS[4],
                level=0,
            ),
            max_level=1,
        )
    )
    scene.dungeon_inventory.set_tier_skill_points(8, 1)

    # 예시:
    # scene.player.hp = 50
    # scene.player.mp = scene.player.max_mp
    # scene.create_monster(7, 3)
    pass
