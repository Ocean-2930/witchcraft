import pygame

# user settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def get_screen_size() -> tuple[int, int]:
    return (SCREEN_WIDTH, SCREEN_HEIGHT)

# game events
MOUSE_LEFT = "mouse_left"
MOUSE_MIDDLE = "mouse_middle"
MOUSE_RIGHT = "mouse_right"

ARROW_UP = pygame.K_UP
ARROW_DOWN = pygame.K_DOWN
ARROW_LEFT = pygame.K_LEFT
ARROW_RIGHT = pygame.K_RIGHT

# develop settings
FPS = 60
__FRAME_DURATION = 0
def get_frame_duration() -> float:
    global __FRAME_DURATION

    if __FRAME_DURATION == 0:
        __FRAME_DURATION = round(1 / FPS, 4)

    return __FRAME_DURATION

VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
VIRTUAL_SIZE = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
BACKGROUND_COLOR = (30, 30, 30)
LETTERBOX_COLOR = (0, 0, 0)
