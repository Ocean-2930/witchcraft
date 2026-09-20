import pygame

from .scene import Scene
from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import TitleButton, TitleContentRenderer


class TitleScene(Scene):
    def scene_initialize(self):
        center_x = VIRTUAL_WIDTH // 2
        button_width = 280
        button_height = 64
        button_gap = 18
        button_group_center_y = VIRTUAL_HEIGHT // 2 + 52

        self.button_font = pygame.font.SysFont("malgungothic", 30, bold=True)
        self.content_renderer = TitleContentRenderer(self)
        has_save = self.game.save_manager.exists()
        button_count = 4 if has_save else 3
        group_height = button_count * button_height + (button_count - 1) * button_gap
        first_button_y = button_group_center_y - group_height // 2 + button_height // 2
        self.continue_button = None
        if has_save:
            self.continue_button = TitleButton(
                self, "이어하기", center_x, first_button_y,
                button_width, button_height, self.continue_game,
            )
            first_button_y += button_height + button_gap
        self.start_button = TitleButton(
            self,
            "게임 시작",
            center_x,
            first_button_y,
            button_width,
            button_height,
            self.start_game,
        )
        self.settings_button = TitleButton(
            self,
            "설정",
            center_x,
            first_button_y + button_height + button_gap,
            button_width,
            button_height,
            self.open_settings,
        )
        self.quit_button = TitleButton(
            self,
            "게임 종료",
            center_x,
            first_button_y + (button_height + button_gap) * 2,
            button_width,
            button_height,
            self.game.quit,
        )

    def start_game(self):
        from .message_scene import MessageScene

        if self.game.save_manager.exists():
            self.add_overlay(MessageScene(
                self.game, "새 게임을 시작하면 기존 저장 데이터가 삭제됩니다. 계속할까요?",
                self.start_new_game,
            ))
        else:
            self.start_new_game()

    def start_new_game(self):
        from .game_entry_scene import GameEntryScene
        from .message_scene import MessageScene
        from utilities.save import SaveError

        try:
            self.game.save_manager.delete()
        except SaveError as error:
            self.add_overlay(MessageScene(self.game, str(error)))
            return
        self.game.session = None
        self.game.dungeon_scene = None
        self.switch_scene(GameEntryScene(self.game))

    def continue_game(self):
        from .dungeon_scene import DungeonScene
        from .message_scene import MessageScene
        from utilities.save import SaveError

        try:
            session = self.game.save_manager.load()
            dungeon = DungeonScene(self.game, session.floors[session.current_floor],
                                   session.inventory, current_floor=session.current_floor)
        except (SaveError, ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
            self.add_overlay(MessageScene(self.game, f"이어하기에 실패했습니다. {error}"))
            return
        self.game.activate_dungeon(dungeon, session)

    def open_settings(self):
        from .settings_scene import SettingsScene

        self.switch_scene(SettingsScene(self.game, self))

    def scene_draw(self):
        self.game.virtual_screen.fill((20, 18, 28))
        super().scene_draw()
