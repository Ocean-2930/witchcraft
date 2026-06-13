from core.game import Game
from scenes.hud import Hud
from settings import BACKGROUND_COLOR


class DebugGame(Game):
    def __init__(self):
        super().__init__()
        self.hud = Hud(self)

    def update_scene(self, delta_time, game_events, mouse_position, wheel_move):
        self.scene.update(delta_time, game_events, mouse_position, wheel_move)
        self.hud.update(delta_time, game_events, mouse_position, wheel_move)

    def draw(self):
        self.virtual_screen.fill(BACKGROUND_COLOR)
        self.scene.draw()
        self.hud.draw()
        self.present()
