import pygame

from .scene import Scene
from settings import ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import (
    ChoiceBox,
    DialogueBox,
    GameEntryStartButton,
    SeedInput,
    SeedStatusMarker,
)
from utilities import RandomGenerator, create_random_seed
from utilities.dungeon import DungeonMapGenerator


class GameEntryScene(Scene):
    DIALOGUE_MODE = "dialogue"
    SEED_MODE = "seed"

    def scene_initialize(self):
        self.mode = None
        self.dialogue_box = None
        self.choice_box = None
        self.seed_status_marker = None
        self.seed_input = None
        self.seed_buttons = []
        self.button_font = pygame.font.SysFont("malgungothic", 26, bold=True)
        self.seed_font = pygame.font.SysFont("consolas", 26)
        self.seed_label_font = pygame.font.SysFont("malgungothic", 19, bold=True)
        self.seed_error_font = pygame.font.SysFont("malgungothic", 16)
        self.show_dialogue()

    def show_dialogue(self):
        self.destroy_seed_ui()
        self.mode = self.DIALOGUE_MODE
        self.dialogue_box = DialogueBox(
            self,
            "???",
            "안녕. 오늘도 왔네.",
        )
        choice_width = 390
        option_height = 56
        option_gap = 12
        choice_height = option_height * 2 + option_gap
        self.choice_box = ChoiceBox(
            self,
            ["시드 고정", "게임 시작"],
            self.select_choice,
            pos_x=self.dialogue_box.rect.right - choice_width // 2,
            pos_y=self.dialogue_box.rect.top - 12 - choice_height // 2,
            width=choice_width,
            choice_height=option_height,
            gap=option_gap,
        )
        first_choice_rect = self.choice_box.get_choice_rect(0)
        self.seed_status_marker = SeedStatusMarker(
            self,
            lambda: self.game.fixed_seed,
            self.clear_fixed_seed,
            first_choice_rect.left - 22,
            first_choice_rect.centery,
        )

    def select_choice(self, index, choice):
        if choice == "시드 고정":
            self.show_seed_settings()
        elif choice == "게임 시작":
            self.start_game()

    def show_seed_settings(self):
        self.destroy_dialogue_ui()
        self.mode = self.SEED_MODE
        initial_seed = self.game.fixed_seed or create_random_seed()
        self.seed_input = SeedInput(
            self,
            initial_seed,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2 - 66,
            410,
            54,
            self.save_seed,
        )
        self.seed_buttons = [
            GameEntryStartButton(
                self,
                "붙여넣기",
                VIRTUAL_WIDTH // 2 - 176,
                VIRTUAL_HEIGHT // 2 + 20,
                160,
                54,
                self.paste_seed,
            ),
            GameEntryStartButton(
                self,
                "저장",
                VIRTUAL_WIDTH // 2,
                VIRTUAL_HEIGHT // 2 + 20,
                160,
                54,
                self.save_seed,
            ),
            GameEntryStartButton(
                self,
                "취소",
                VIRTUAL_WIDTH // 2 + 176,
                VIRTUAL_HEIGHT // 2 + 20,
                160,
                54,
                self.cancel_seed_settings,
            ),
        ]

    def start_game(self):
        from .dungeon_scene import DungeonScene

        seed = self.game.fixed_seed or create_random_seed()
        try:
            dungeon_map = DungeonMapGenerator(RandomGenerator(seed), seed).generate()
        except ValueError as error:
            self.dialogue_box.set_dialogue("???", f"던전을 만들지 못했어. {error}")
            return
        self.switch_scene(DungeonScene(self.game, dungeon_map))

    def save_seed(self):
        try:
            self.game.fixed_seed = self.seed_input.get_seed()
        except ValueError as error:
            self.seed_input.set_error(str(error))
            return
        self.show_dialogue()

    def cancel_seed_settings(self):
        self.clear_fixed_seed()
        self.show_dialogue()

    def clear_fixed_seed(self):
        self.game.fixed_seed = None

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

    @staticmethod
    def initialize_clipboard():
        if not pygame.scrap.get_init():
            pygame.scrap.init()

    def destroy_dialogue_ui(self):
        if self.seed_status_marker is not None:
            self.seed_status_marker.destroy()
            self.seed_status_marker = None
        if self.choice_box is not None:
            self.choice_box.destroy()
            self.choice_box = None
        if self.dialogue_box is not None:
            self.dialogue_box.destroy()
            self.dialogue_box = None

    def destroy_seed_ui(self):
        for button in self.seed_buttons:
            button.destroy()
        self.seed_buttons = []
        if self.seed_input is not None:
            self.seed_input.destroy()
            self.seed_input = None

    def return_to_title(self):
        from .title_scene import TitleScene

        self.destroy_dialogue_ui()
        self.destroy_seed_ui()
        self.switch_scene(TitleScene(self.game))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            if self.mode == self.SEED_MODE:
                self.cancel_seed_settings()
            else:
                self.return_to_title()
            return
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        self.game.virtual_screen.fill((18, 22, 29))
        super().scene_draw()
