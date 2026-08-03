from secrets import randbelow

import pygame

from .scene import Scene
from settings import ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import GameEntryStartButton, PauseButton, SeedInput
from utilities import RandomGenerator
from utilities.dungeon import DungeonMapGenerator


class GameEntryScene(Scene):
    MIN_SEED = 10**15
    SEED_RANGE = 9 * 10**15

    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 32, bold=True)
        self.seed_font = pygame.font.SysFont("consolas", 26)
        self.seed_label_font = pygame.font.SysFont("malgungothic", 19, bold=True)
        self.seed_error_font = pygame.font.SysFont("malgungothic", 16)

        self.seed_input = SeedInput(
            self,
            self.create_random_seed(),
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2 - 72,
            410,
            54,
        )
        self.copy_seed_button = GameEntryStartButton(
            self,
            "복사",
            VIRTUAL_WIDTH // 2 - 249,
            VIRTUAL_HEIGHT // 2 - 5,
            150,
            48,
            self.copy_seed,
        )
        self.paste_seed_button = GameEntryStartButton(
            self,
            "붙여넣기",
            VIRTUAL_WIDTH // 2 - 83,
            VIRTUAL_HEIGHT // 2 - 5,
            150,
            48,
            self.paste_seed,
        )
        self.clear_seed_button = GameEntryStartButton(
            self,
            "비우기",
            VIRTUAL_WIDTH // 2 + 83,
            VIRTUAL_HEIGHT // 2 - 5,
            150,
            48,
            self.clear_seed,
        )
        self.reset_seed_button = GameEntryStartButton(
            self,
            "재설정",
            VIRTUAL_WIDTH // 2 + 249,
            VIRTUAL_HEIGHT // 2 - 5,
            150,
            48,
            self.reset_seed,
        )

        self.start_button = GameEntryStartButton(
            self,
            "게임 시작",
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2 + 100,
            280,
            64,
            self.start_game,
        )
        self.pause_button = PauseButton(
            self,
            VIRTUAL_WIDTH - 42,
            42,
            48,
            48,
            self.open_pause,
        )

    def start_game(self):
        from .dungeon_scene import DungeonScene

        try:
            seed = self.seed_input.get_seed()
            dungeon_map = DungeonMapGenerator(RandomGenerator(seed), seed).generate()
        except ValueError as error:
            self.seed_input.set_error(str(error))
            return

        self.seed_input.deactivate()
        self.switch_scene(DungeonScene(self.game, dungeon_map))

    def copy_seed(self):
        try:
            self.initialize_clipboard()
            pygame.scrap.put(pygame.SCRAP_TEXT, self.seed_input.text.encode("utf-8"))
        except pygame.error:
            self.seed_input.set_error("클립보드에 시드를 복사하지 못했습니다.")

    def paste_seed(self):
        try:
            self.initialize_clipboard()
            clipboard_data = pygame.scrap.get(pygame.SCRAP_TEXT)
        except pygame.error:
            self.seed_input.set_error("클립보드에서 시드를 읽지 못했습니다.")
            return

        if not clipboard_data:
            self.seed_input.set_error("클립보드에 붙여넣을 텍스트가 없습니다.")
            return

        clipboard_text = clipboard_data.decode("utf-8", errors="ignore").replace("\x00", "")
        digits = "".join(character for character in clipboard_text if character.isdigit())
        if not digits or len(digits) > SeedInput.SEED_LENGTH:
            self.seed_input.set_error("붙여넣을 시드는 숫자 1~16자리여야 합니다.")
            return
        self.seed_input.replace_text(digits)

    def clear_seed(self):
        self.seed_input.clear()

    def reset_seed(self):
        self.seed_input.replace_text(str(self.create_random_seed()))

    @classmethod
    def create_random_seed(cls) -> int:
        return randbelow(cls.SEED_RANGE) + cls.MIN_SEED

    @staticmethod
    def initialize_clipboard():
        if not pygame.scrap.get_init():
            pygame.scrap.init()

    def open_pause(self):
        from .pause_scene import PauseScene

        self.add_overlay(PauseScene(self.game))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.open_pause()

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        screen = self.game.virtual_screen
        screen.fill((18, 22, 29))

        super().scene_draw()
