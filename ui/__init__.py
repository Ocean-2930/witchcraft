from importlib import import_module

from .renderer import Renderer

# dungeon_scene
from .dungeon_scene import (
    FloorTileRenderer,
    HotbarRenderer,
    MonsterMarkerRenderer,
    MonsterTooltipRenderer,
    PlayerMarkerRenderer,
    PlayerStatusRenderer,
    SkillDirectionCompassRenderer,
    WallTileRenderer,
)

# game_entry_scene
from .game_entry_scene import GameEntryStartButton

# inventory_scene
from .inventory_scene import (
    EquipmentSlot,
    InventoryContentRenderer,
    InventoryPanelRenderer,
    InventoryPopupRenderer,
    InventoryTabButton,
    ItemSlot,
    InventoryPopupButton,
    SkillEquipSlot,
    SkillNodeListView,
)

# global
PauseButton = import_module(f"{__name__}.global").PauseButton
SkillCard = import_module(f"{__name__}.global").SkillCard
SkillInfoWindow = import_module(f"{__name__}.global").SkillInfoWindow

# pause_scene
from .pause_scene import PausePanelRenderer

# title_scene
from .title_scene import TitleButton, TitleContentRenderer

# settings_scene
from .settings_scene import SettingsButton, SettingsContentRenderer, SettingsSlider

__all__ = [
    "Renderer",
    # dungeon_scene
    "FloorTileRenderer",
    "HotbarRenderer",
    "MonsterMarkerRenderer",
    "MonsterTooltipRenderer",
    "PlayerMarkerRenderer",
    "PlayerStatusRenderer",
    "SkillDirectionCompassRenderer",
    "WallTileRenderer",
    # game_entry_scene
    "GameEntryStartButton",
    # inventory_scene
    "EquipmentSlot",
    "InventoryContentRenderer",
    "InventoryPanelRenderer",
    "InventoryPopupRenderer",
    "InventoryTabButton",
    "ItemSlot",
    "InventoryPopupButton",
    "SkillEquipSlot",
    "SkillNodeListView",
    # global
    "PauseButton",
    "SkillCard",
    "SkillInfoWindow",
    # pause_scene
    "PausePanelRenderer",
    # title_scene
    "TitleButton",
    "TitleContentRenderer",
    # settings_scene
    "SettingsButton",
    "SettingsContentRenderer",
    "SettingsSlider",
]
