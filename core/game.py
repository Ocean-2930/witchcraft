import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from scenes import TitleScene


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Game Template")

        self.clock = pygame.time.Clock()
        self.running = True

        self.current_scene = TitleScene(self)

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def run(self):
        while self.running:
            events = pygame.event.get()

            self.current_scene.handle_events(events)
            self.current_scene.update()
            self.current_scene.draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
    
    def quit(self):
        self.running = False
