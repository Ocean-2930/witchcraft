from importlib import import_module

from .renderer import Renderer

# dungeon_scene
from .dungeon_scene import (
    FloorTileRenderer,
    MonsterMarkerRenderer,
    MonsterTooltipRenderer,
    PlayerMarkerRenderer,
    PlayerStatusRenderer,
    SkillDirectionCompassRenderer,
    StairTileRenderer,
    WallTileRenderer,
    MiniMap,
    DungeonFogRenderer,
)

# game_entry_scene
from .game_entry_scene import GameEntryStartButton, SeedInput, SeedStatusMarker

# inventory_scene
from .inventory_scene import (
    ActiveSkillGrid,
    EquipmentSlot,
    InventoryContentRenderer,
    InventoryPanelRenderer,
    InventoryPopupRenderer,
    InventoryTabButton,
    ItemSlot,
    InventoryPopupButton,
    LearnableSkillListView,
    PassiveSkillGrid,
)

# global
ChoiceBox = import_module(f"{__name__}.global").ChoiceBox
DialogueBox = import_module(f"{__name__}.global").DialogueBox
PauseButton = import_module(f"{__name__}.global").PauseButton
SkillCard = import_module(f"{__name__}.global").SkillCard
SkillInfoWindow = import_module(f"{__name__}.global").SkillInfoWindow
ShortcutBar = import_module(f"{__name__}.global").ShortcutBar
ShortcutSlot = import_module(f"{__name__}.global").ShortcutSlot
ItemWindow = import_module(f"{__name__}.global").ItemWindow

# pause_scene
from .pause_scene import PausePanelRenderer

# map_scene
from .map_scene import MapPanelRenderer

# title_scene
from .title_scene import TitleButton, TitleContentRenderer

# settings_scene
from .settings_scene import SettingsButton, SettingsContentRenderer, SettingsSlider

__all__ = [
    "Renderer",
    # dungeon_scene
    "FloorTileRenderer",
    "MonsterMarkerRenderer",
    "MonsterTooltipRenderer",
    "PlayerMarkerRenderer",
    "PlayerStatusRenderer",
    "SkillDirectionCompassRenderer",
    "StairTileRenderer",
    "WallTileRenderer",
    "MiniMap",
    "DungeonFogRenderer",
    # game_entry_scene
    "GameEntryStartButton",
    "SeedInput",
    "SeedStatusMarker",
    # inventory_scene
    "EquipmentSlot",
    "ActiveSkillGrid",
    "InventoryContentRenderer",
    "InventoryPanelRenderer",
    "InventoryPopupRenderer",
    "InventoryTabButton",
    "ItemSlot",
    "InventoryPopupButton",
    "LearnableSkillListView",
    "PassiveSkillGrid",
    # global
    "ChoiceBox",
    "DialogueBox",
    "PauseButton",
    "SkillCard",
    "SkillInfoWindow",
    "ShortcutBar",
    "ShortcutSlot",
    "ItemWindow",
    # pause_scene
    "PausePanelRenderer",
    # map_scene
    "MapPanelRenderer",
    # title_scene
    "TitleButton",
    "TitleContentRenderer",
    # settings_scene
    "SettingsButton",
    "SettingsContentRenderer",
    "SettingsSlider",
]
