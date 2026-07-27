from typing import TYPE_CHECKING

from items import BluePotion, Equip, ItemInstance, SkilledEquip

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

    # 예시:
    # scene.player.hp = 50
    # scene.player.mp = scene.player.max_mp
    # scene.create_monster(7, 3)
    pass
