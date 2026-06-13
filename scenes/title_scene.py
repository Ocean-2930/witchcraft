from .scene import Scene
from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.ui import UIElement


class TitleScene(Scene):
    def scene_initialize(self):
        center_x = VIRTUAL_WIDTH // 2
        center_y = VIRTUAL_HEIGHT // 2

        self.center_box = UIElement(self, pos_x=center_x, pos_y=center_y, width=160, height=160)

    def scene_draw(self):
        self.game.virtual_screen.fill((20, 18, 28))
        super().scene_draw()
