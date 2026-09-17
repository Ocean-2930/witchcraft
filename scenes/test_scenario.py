from typing import TYPE_CHECKING

from items import BluePotion, EquipmentInstance, ItemInstance, SimpleSword
from utilities.inventory import LearnableSkill
from skills import AttackSkill, SkillInstance, STAT_PASSIVE_SKILLS

if TYPE_CHECKING:
    from .dungeon_scene import DungeonScene


def senario(scene: "DungeonScene"):
    """개발 중 던전의 초기 상태를 변경하는 테스트 시나리오."""
    scene.dungeon_inventory.player.move_speed = -2
    scene.dungeon_inventory.gold = 1000
    scene.dungeon_inventory.harmony_stones = 100
    scene.dungeon_inventory.add_item(ItemInstance(BluePotion(), stack=3))
    scene.dungeon_inventory.add_item(
        EquipmentInstance(
            SimpleSword(),
            stat_rows=[
                *(
                    SkillInstance(skill, level=level)
                    for skill, level in zip(
                        STAT_PASSIVE_SKILLS[:5],
                        (3, 2, 5, 4, 2),
                    )
                ),
                None,
                None,
            ],
        )
    )
    # 원본 4행 방어력은 +1로 맨 위, 3행 마나는 낮은 원본 레벨로 그다음에 온다.
    scene.dungeon_inventory.add_item(
        EquipmentInstance(
            SimpleSword(),
            stat_rows=[
                SkillInstance(STAT_PASSIVE_SKILLS[2], level=6),
                SkillInstance(STAT_PASSIVE_SKILLS[3], level=4),
                SkillInstance(STAT_PASSIVE_SKILLS[5], level=2),
                None,
                None,
                None,
                None,
            ],
        )
    )
    # 첫 번째 철검의 5개 스킬과 합치면 8개가 되어 재료 선택이 거부된다.
    scene.dungeon_inventory.add_item(
        EquipmentInstance(
            SimpleSword(),
            stat_rows=[
                SkillInstance(STAT_PASSIVE_SKILLS[5], level=2),
                SkillInstance(STAT_PASSIVE_SKILLS[6], level=2),
                SkillInstance(STAT_PASSIVE_SKILLS[7], level=2),
                None,
                None,
                None,
                None,
            ],
        )
    )
    for tier in (1, 2):
        if tier == 1:
            scene.dungeon_inventory.add_learnable_skill(
                LearnableSkill(
                    tier=tier,
                    skill=SkillInstance(
                        AttackSkill(),
                        level=1,
                    ),
                    max_level=1,
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
    scene.dungeon_inventory.assign_hotbar_skill("R", "attack")
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
    # scene.dungeon_inventory.player.hp = 50
    # scene.dungeon_inventory.player.mp = scene.dungeon_inventory.player.max_mp
    # scene.create_monster(7, 3)
    pass
