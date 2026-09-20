from settings import ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import ChoiceBox, DialogueBox, MessageBackdropRenderer
from .scene import Scene


class MessageScene(Scene):
    """공용 대화·선택 UI를 사용하는 알림/확인 overlay."""

    def __init__(self, game, message, on_confirm=None):
        self.message = message
        self.on_confirm = on_confirm
        super().__init__(game)

    def scene_initialize(self):
        self.backdrop = MessageBackdropRenderer(self)
        self.dialogue = DialogueBox(self, "안내", self.message,
                                    pos_y=VIRTUAL_HEIGHT // 2 - 70, width=960)
        self.choices = ChoiceBox(
            self, ["취소", "삭제하고 새로 시작"] if self.on_confirm else ["확인"],
            self.select, pos_x=VIRTUAL_WIDTH // 2,
            pos_y=VIRTUAL_HEIGHT // 2 + 100,
        )

    def select(self, index, choice):
        self.exit_scene()
        if self.on_confirm is not None and index == 1:
            self.on_confirm()

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.exit_scene()
            return
        super().scene_update(delta_time, game_events, mouse_position, wheel_move)
