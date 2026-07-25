from .unit_base import UnitBase

__all__ = ["DungeonInventory", "ItemInventory", "SkillTree", "UnitBase"]


def __getattr__(name):
    if name in {"DungeonInventory", "ItemInventory", "SkillTree"}:
        from .dungeon_inventory import DungeonInventory, ItemInventory, SkillTree

        exports = {
            "DungeonInventory": DungeonInventory,
            "ItemInventory": ItemInventory,
            "SkillTree": SkillTree,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
