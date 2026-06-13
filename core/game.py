import pygame
import settings

from scenes import TitleScene

# game event import
from settings import (
    MOUSE_LEFT,
    MOUSE_MIDDLE,
    MOUSE_RIGHT,

    ARROW_UP,
    ARROW_DOWN,
    ARROW_LEFT,
    ARROW_RIGHT
)

# develop setting import
from settings import (
    FPS,
    VIRTUAL_WIDTH,
    VIRTUAL_HEIGHT,
    VIRTUAL_SIZE,
    BACKGROUND_COLOR,
    LETTERBOX_COLOR,
)

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Pygame 2D Template")

        # set clock
        self.clock = pygame.time.Clock()

        # game running state
        self.running = True

        # display settings
        self.display_scale = 1.0
        self.display_offset = pygame.Vector2(0, 0)
        self.display_size = VIRTUAL_SIZE

        self.resize_window()
        self.virtual_screen = pygame.Surface(VIRTUAL_SIZE).convert()

        # game events formal status
        self.game_events = [ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT]
        self.formal_events = { k:False for k in self.game_events }
        self.formal_events[MOUSE_LEFT] = False
        self.formal_events[MOUSE_MIDDLE] = False
        self.formal_events[MOUSE_RIGHT] = False

        # set scene
        self.scene = TitleScene(self)

    def run(self):
        while self.running:
            self.update()
            self.draw()

        pygame.quit()

    def update(self):
        delta_time, game_events, mouse_position, wheel_move = self.read_inputs()
        self.update_scene(delta_time, game_events, mouse_position, wheel_move)

    def read_inputs(self):
        events = pygame.event.get()

        # read events
        wheel_move = 0
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            # read wheel movement
            if event.type == pygame.MOUSEWHEEL:
                wheel_move += event.y

        # read delta time
        delta_time = self.clock.tick(FPS) / 1000.0

        # detect pygame events
        game_events = {}

        # detect keyboard input
        keyboards = pygame.key.get_pressed()
        for k in self.game_events:
            buff = {}
            status = keyboards[k]

            buff["status"] = status
            buff["keydown"] = not self.formal_events[k] and status
            buff["keyup"] = self.formal_events[k] and not status

            game_events[k] = buff

            self.formal_events[k] = status

        # detect mouse input
        left, middle, right = pygame.mouse.get_pressed(3)
        game_events[MOUSE_LEFT] = {
            "status": left,
            "keydown": (not self.formal_events[MOUSE_LEFT]) and left,
            "keyup": (self.formal_events[MOUSE_LEFT]) and not left,
        }
        self.formal_events[MOUSE_LEFT] = left

        game_events[MOUSE_MIDDLE] = {
            "status": middle,
            "keydown": (not self.formal_events[MOUSE_MIDDLE]) and middle,
            "keyup": (self.formal_events[MOUSE_MIDDLE]) and not middle,
        }
        self.formal_events[MOUSE_MIDDLE] = middle

        game_events[MOUSE_RIGHT] = {
            "status": right,
            "keydown": (not self.formal_events[MOUSE_RIGHT]) and right,
            "keyup": (self.formal_events[MOUSE_RIGHT]) and not right,
        }
        self.formal_events[MOUSE_RIGHT] = right

        # read mouse_position
        mouse_position = self.window_to_virtual(pygame.mouse.get_pos())

        return delta_time, game_events, mouse_position, wheel_move

    def update_scene(self, delta_time, game_events, mouse_position, wheel_move):
        self.scene.update(delta_time, game_events, mouse_position, wheel_move)

    def draw(self):
        self.virtual_screen.fill(BACKGROUND_COLOR)
        self.scene.draw()
        self.present()

    def window_to_virtual(self, window_pos: tuple[int, int]) -> tuple[int, int] | None:
        window_x, window_y = window_pos

        offset_x = self.display_offset.x
        offset_y = self.display_offset.y
        scaled_width, scaled_height = self.display_size

        if not (
            offset_x <= window_x < offset_x + scaled_width
            and offset_y <= window_y < offset_y + scaled_height
        ):
            return None

        virtual_x = (window_x - offset_x) / self.display_scale
        virtual_y = (window_y - offset_y) / self.display_scale

        return (int(virtual_x), int(virtual_y))

    def present(self):
        scaled_surface = pygame.transform.smoothscale(self.virtual_screen, self.display_size)

        self.screen.fill(LETTERBOX_COLOR)

        self.screen.blit(scaled_surface, self.display_offset)

        pygame.display.flip()

    def resize_window(self):
        self.screen = pygame.display.set_mode(settings.get_screen_size())

        window_width, window_height = self.screen.get_size()

        scale_x = window_width / VIRTUAL_WIDTH
        scale_y = window_height / VIRTUAL_HEIGHT

        self.display_scale = min(scale_x, scale_y)

        scaled_width = max(1, int(VIRTUAL_WIDTH * self.display_scale))
        scaled_height = max(1, int(VIRTUAL_HEIGHT * self.display_scale))

        self.display_size = (scaled_width, scaled_height)

        offset_x = (window_width - scaled_width) // 2
        offset_y = (window_height - scaled_height) // 2

        self.display_offset.update(offset_x, offset_y)

    def set_screen_size(self, width, height):
        settings.SCREEN_WIDTH = width
        settings.SCREEN_HEIGHT = height
        self.resize_window()

    def quit(self):
        self.running = False
