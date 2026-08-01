from typing import TYPE_CHECKING

from items import BluePotion, Equip, ItemInstance, SkilledEquip
from inventory import SkillNode
from skills import AttackSkill, SkillBase, SkillInstance

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
    scene.dungeon_inventory.add_skill_node(
        SkillNode(
            tier=1,
            skill=SkillInstance(
                AttackSkill(),
                level=0,
            ),
        )
    )
    for index in range(1, 5):
        scene.dungeon_inventory.add_skill_node(
            SkillNode(
                tier=1,
                skill=SkillInstance(
                    AttackSkill(
                        name=f"공격 {index + 1}",
                        skill_code=f"attack_{index + 1}",
                        max_level=5,
                    ),
                    level=0,
                ),
            )
        )
    scene.dungeon_inventory.set_tier_skill_points(1, 3)
    scene.dungeon_inventory.add_skill_node(
        SkillNode(
            tier=8,
            skill=SkillInstance(
                SkillBase(
                    name="필살기",
                    skill_code="ultimate_test",
                    description="기능 테스트용 스킬이다.",
                    max_level=1,
                    requires_direction=False,
                ),
                level=0,
            ),
        )
    )
    scene.dungeon_inventory.set_tier_skill_points(8, 1)

    # 예시:
    # scene.player.hp = 50
    # scene.player.mp = scene.player.max_mp
    # scene.create_monster(7, 3)
    pass
