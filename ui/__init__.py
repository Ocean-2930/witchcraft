from importlib import import_module

from .renderer import Renderer

# message_scene
from .message_scene.message_backdrop import MessageBackdropRenderer

# dungeon_scene
from .dungeon_scene import (
    CombatLogRenderer,
    CombatTimelineRenderer,
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
    InventoryPopupButton,
    LearnableSkillListView,
    PassiveSkillGrid,
)

# synthesis_scene
from .synthesis_scene import MaterialNotice, SynthesisPanel

# global
CurrencyBar = import_module(f"{__name__}.global").CurrencyBar
ItemSlot = import_module(f"{__name__}.global").ItemSlot
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
    "MessageBackdropRenderer",
    "Renderer",
    # dungeon_scene
    "CombatLogRenderer",
    "FloorTileRenderer",
    "CombatTimelineRenderer",
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
    "SynthesisPanel",
    "MaterialNotice",
    # global
    "ChoiceBox",
    "DialogueBox",
    "PauseButton",
    "SkillCard",
    "SkillInfoWindow",
    "ShortcutBar",
    "ShortcutSlot",
    "ItemWindow",
    "CurrencyBar",
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
