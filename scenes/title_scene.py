from .scene import Scene


class TitleScene(Scene):
    def scene_draw(self):
        self.game.virtual_screen.fill((20, 18, 28))
