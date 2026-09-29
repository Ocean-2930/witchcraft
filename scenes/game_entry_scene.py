import pygame

from .scene import Scene
from settings import ARROW_LEFT, ARROW_RIGHT, ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import (
    CharacterCard,
    ChoiceBox,
    DialogueBox,
    GameEntryStartButton,
    SeedInput,
    SeedStatusMarker,
)
from utilities import create_random_seed
from utilities.dungeon import DungeonMapGenerator
from utilities.inventory import DungeonInventory
from units.character_definitions import load_character_definitions


class GameEntryScene(Scene):
    DIALOGUE_MODE = "dialogue"
    SEED_MODE = "seed"
    CHARACTER_MODE = "character"

    def scene_initialize(self):
        self.mode = None
        self.character_name = "renea"
        self.dialogue_box = None
        self.choice_box = None
        self.seed_status_marker = None
        self.seed_input = None
        self.seed_buttons = []
        self.character_cards = []
        self.character_scroll_buttons = []
        self.character_viewport = pygame.Rect(96, 90, VIRTUAL_WIDTH - 192, VIRTUAL_HEIGHT - 180)
        self.character_scroll = 0
        self.character_scroll_max = 0
        self.button_font = pygame.font.SysFont("malgungothic", 26, bold=True)
        self.seed_font = pygame.font.SysFont("consolas", 26)
        self.seed_label_font = pygame.font.SysFont("malgungothic", 19, bold=True)
        self.seed_error_font = pygame.font.SysFont("malgungothic", 16)
        self.show_dialogue()

    def show_dialogue(self):
        self.destroy_seed_ui()
        self.destroy_character_ui()
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
            self.show_character_selection()

    def show_character_selection(self):
        try:
            definitions = load_character_definitions()
            if any(row["code"] not in DungeonInventory.CHARACTER_NAMES for row in definitions):
                raise ValueError("지원하지 않는 캐릭터 코드입니다.")
            self.destroy_character_ui()
            gap = 48
            width = 320
            height = VIRTUAL_HEIGHT - 180
            total_width = width * len(definitions) + gap * (len(definitions) - 1)
            self.character_scroll = 0
            self.character_scroll_max = max(0, total_width - self.character_viewport.width)
            self.character_content_left = self.character_viewport.left + max(0, (self.character_viewport.width - total_width) // 2)
            for index, definition in enumerate(definitions):
                x = self.character_content_left + width // 2 + index * (width + gap)
                self.character_cards.append(CharacterCard(self, definition, x, VIRTUAL_HEIGHT // 2, width, height))
            if self.character_scroll_max:
                for text, x, direction in (("<", 48, -1), (">", VIRTUAL_WIDTH - 48, 1)):
                    self.character_scroll_buttons.append(GameEntryStartButton(
                        self, text, x, VIRTUAL_HEIGHT // 2, 56, 64,
                        lambda direction=direction: self.scroll_characters(direction * 368),
                    ))
        except (OSError, ValueError, pygame.error) as error:
            self.destroy_character_ui()
            self.dialogue_box.set_dialogue("???", f"캐릭터를 불러오지 못했어. {error}")
            return
        self.destroy_dialogue_ui()
        self.mode = self.CHARACTER_MODE

    def select_character(self, code):
        self.character_name = code
        self.start_game()

    def scroll_characters(self, amount):
        self.character_scroll = max(0, min(self.character_scroll_max, self.character_scroll + amount))
        for index, card in enumerate(self.character_cards):
            card.set_transform(pos_x=self.character_content_left + 160 + index * 368 - self.character_scroll)
            card.is_hovered = False
        if self.ui_focus in self.character_cards:
            self.ui_focus = None

    def destroy_character_ui(self):
        for card in self.character_cards:
            card.destroy()
        self.character_cards = []
        for button in self.character_scroll_buttons:
            button.destroy()
        self.character_scroll_buttons = []
        self.character_scroll = 0
        self.character_scroll_max = 0

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
        dungeon_inventory = DungeonInventory(game_seed=seed, character_name=self.character_name)
        try:
            floor_random = dungeon_inventory.get_floor_random(1)
            dungeon_map = DungeonMapGenerator(
                dungeon_inventory.get_map_random_generator(1),
                floor_random,
            ).generate()
        except ValueError as error:
            self.show_dialogue()
            self.dialogue_box.set_dialogue("???", f"던전을 만들지 못했어. {error}")
            return
        self.game.activate_dungeon(DungeonScene(self.game, dungeon_map, dungeon_inventory))

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
        self.destroy_character_ui()
        self.switch_scene(TitleScene(self.game))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            if self.mode == self.SEED_MODE:
                self.cancel_seed_settings()
            elif self.mode == self.CHARACTER_MODE:
                self.show_dialogue()
            else:
                self.return_to_title()
            return
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)
        if self.mode == self.CHARACTER_MODE and self.character_scroll_max:
            if game_events.get(ARROW_LEFT, {}).get("keydown"):
                self.scroll_characters(-368)
            if game_events.get(ARROW_RIGHT, {}).get("keydown"):
                self.scroll_characters(368)
            if wheel_move and mouse_position is not None and self.character_viewport.collidepoint(mouse_position):
                self.scroll_characters(-wheel_move * 120)

    def scene_draw(self):
        self.game.virtual_screen.fill((18, 22, 29))
        if self.mode == self.CHARACTER_MODE:
            title = self.button_font.render("캐릭터 선택", True, (244, 252, 252))
            self.game.virtual_screen.blit(title, title.get_rect(center=(VIRTUAL_WIDTH // 2, 44)))
            hint_text = "캐릭터를 클릭하여 시작 · ESC 돌아가기"
            if self.character_scroll_max:
                hint_text += " · 좌우 버튼 / 방향키 / 휠로 이동"
            hint = self.seed_label_font.render(hint_text, True, (170, 188, 199))
            self.game.virtual_screen.blit(hint, hint.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT - 40)))
        super().scene_draw()
