import pygame

from .scene import Scene


class TitleScene(Scene):
    def scene_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quit()

    def scene_draw(self):
        self.game.screen.fill((20, 18, 28))
