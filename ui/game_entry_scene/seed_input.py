import pygame

from settings import BACKSPACE, ENTER, TEXT_INPUT
from ui.renderer import Renderer
from ui.ui import UIElement


class SeedInputRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, seed_input):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.seed_input = seed_input

    def draw(self, screen):
        seed_input = self.seed_input
        if seed_input.error_text:
            border_color = (224, 92, 92)
        elif seed_input.is_active:
            border_color = (197, 244, 242)
        else:
            border_color = (105, 139, 145)

        pygame.draw.rect(screen, (13, 28, 33), self.rect, border_radius=7)
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=7)

        text_surface = seed_input.font.render(seed_input.text, True, (238, 246, 246))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        label_surface = seed_input.label_font.render("던전 시드", True, (168, 201, 203))
        label_rect = label_surface.get_rect(bottomleft=(self.rect.left, self.rect.top - 8))
        screen.blit(label_surface, label_rect)

        if seed_input.error_text:
            error_surface = seed_input.error_font.render(
                seed_input.error_text,
                True,
                (238, 123, 123),
            )
            error_rect = error_surface.get_rect(
                midtop=(self.rect.centerx, self.rect.bottom + 100)
            )
            screen.blit(error_surface, error_rect)


class SeedInput(UIElement):
    SEED_LENGTH = 16
    MIN_SEED = 10**15
    MAX_SEED = 10**16 - 1
    BACKSPACE_INITIAL_DELAY = 0.4
    BACKSPACE_REPEAT_INTERVAL = 0.05

    def __init__(
        self,
        scene,
        seed: int,
        pos_x: int,
        pos_y: int,
        width: int,
        height: int,
        on_submit=None,
    ):
        self._digits = ""
        self.text = str(seed)
        self.error_text = ""
        self.is_active = True
        self.backspace_elapsed = 0.0
        self.backspace_repeat_elapsed = 0.0
        self.font = scene.seed_font
        self.label_font = scene.seed_label_font
        self.error_font = scene.seed_error_font
        self.on_submit = on_submit
        renderer = SeedInputRenderer(scene, pos_x, pos_y, width, height, self)
        super().__init__(scene, renderer=renderer)
        pygame.key.start_text_input()

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        if not self.is_active:
            return

        input_text = "".join(character for character in game_events[TEXT_INPUT] if character.isdigit())
        if input_text:
            self._digits = (self._digits + input_text)[: self.SEED_LENGTH]
            self.error_text = ""
        if game_events[BACKSPACE]["keydown"]:
            self.delete_last_digit()
            self.backspace_elapsed = 0.0
            self.backspace_repeat_elapsed = 0.0
        elif game_events[BACKSPACE]["status"]:
            self.update_backspace_repeat(delta_time)
        else:
            self.backspace_elapsed = 0.0
            self.backspace_repeat_elapsed = 0.0
        if game_events[ENTER]["keydown"] and self.on_submit is not None:
            self.on_submit()

    def update_backspace_repeat(self, delta_time: float) -> None:
        self.backspace_elapsed += delta_time
        if self.backspace_elapsed < self.BACKSPACE_INITIAL_DELAY:
            return

        self.backspace_repeat_elapsed += delta_time
        while self.backspace_repeat_elapsed >= self.BACKSPACE_REPEAT_INTERVAL:
            self.backspace_repeat_elapsed -= self.BACKSPACE_REPEAT_INTERVAL
            self.delete_last_digit()

    def delete_last_digit(self) -> None:
        self._digits = self._digits[:-1]
        self.error_text = ""

    def get_seed(self) -> int:
        if not self._digits:
            raise ValueError("시드를 입력해 주세요.")
        seed = int(self._digits)
        if not 1 <= seed <= self.MAX_SEED:
            raise ValueError(f"시드는 1부터 {self.MAX_SEED}까지 입력할 수 있습니다.")
        return seed

    @property
    def text(self) -> str:
        padded_digits = self._digits.zfill(self.SEED_LENGTH)
        return "-".join(
            padded_digits[index : index + 4]
            for index in range(0, self.SEED_LENGTH, 4)
        )

    @text.setter
    def text(self, value: str) -> None:
        self._digits = "".join(character for character in str(value) if character.isdigit())[
            : self.SEED_LENGTH
        ]

    def replace_text(self, value: str) -> None:
        self.text = value
        self.error_text = ""

    def clear(self) -> None:
        self._digits = ""
        self.error_text = ""

    def set_error(self, message: str) -> None:
        self.error_text = message

    def on_left_click(self):
        self.is_active = True
        pygame.key.start_text_input()

    def deactivate(self):
        self.is_active = False
        pygame.key.stop_text_input()

    def destroy(self):
        self.deactivate()
        super().destroy()
        self.renderer.destroy()
