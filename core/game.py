import ctypes
from ctypes import wintypes

import pygame
import settings

from scenes import TitleScene

# game event import
from settings import (
    MOUSE_LEFT,
    MOUSE_MIDDLE,
    MOUSE_RIGHT,
    TEXT_INPUT,

    ARROW_UP,
    ARROW_DOWN,
    ARROW_LEFT,
    ARROW_RIGHT,
    BACKSPACE,
    ENTER,
    ESCAPE,
    TAB,
    KEY_1,
    KEY_2,
    KEY_3,
    KEY_4,
    KEY_Q,
    KEY_W,
    KEY_E,
    KEY_R,
    KEY_T
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


class MonitorInfo(ctypes.Structure):
    _fields_ = (
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    )


class Sound:
    def __init__(self, sound_path: str, weight: float):
        self.player = pygame.mixer.Sound(sound_path)
        self.weight = weight

    def play(self):
        self.player.set_volume(settings.SFX * self.weight)
        self.player.play()


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption("Witchcraft")

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
        self.game_events = [
            ARROW_UP,
            ARROW_DOWN,
            ARROW_LEFT,
            ARROW_RIGHT,
            BACKSPACE,
            ENTER,
            ESCAPE,
            TAB,
            KEY_1,
            KEY_2,
            KEY_3,
            KEY_4,
            KEY_Q,
            KEY_W,
            KEY_E,
            KEY_R,
            KEY_T,
        ]
        self.formal_events = { k:False for k in self.game_events }
        self.formal_events[MOUSE_LEFT] = False
        self.formal_events[MOUSE_MIDDLE] = False
        self.formal_events[MOUSE_RIGHT] = False

        # set scene
        self.fixed_seed = None
        self.scene = TitleScene(self)

    def run(self):
        while self.running:
            self.update()
            self.draw()

        pygame.quit()

    def background_music_play(self, music_path: str):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)
        self.change_volume()

    def background_music_stop(self):
        pygame.mixer.music.stop()

    def background_music_pause(self):
        pygame.mixer.music.pause()

    def background_music_unpause(self):
        pygame.mixer.music.unpause()

    def change_volume(self):
        pygame.mixer.music.set_volume(settings.BGM)

    def sound_load(self, sound_path: str, weight: float):
        return Sound(sound_path, weight)

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
        game_events[TEXT_INPUT] = "".join(
            event.text for event in events if event.type == pygame.TEXTINPUT
        )

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
        display_flags = pygame.FULLSCREEN if settings.FULLSCREEN else 0
        screen_size = (0, 0) if settings.FULLSCREEN else settings.get_screen_size()
        self.screen = pygame.display.set_mode(screen_size, display_flags)

        if not settings.FULLSCREEN:
            self.center_window()

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

    def center_window(self):
        if not hasattr(ctypes, "windll"):
            return

        user32 = ctypes.windll.user32
        self.configure_window_api(user32)

        window_info = pygame.display.get_wm_info()
        window_handle = window_info.get("window") or window_info.get("hwnd")

        if not window_handle:
            return

        work_area = self.get_window_work_area(window_handle)
        window_rect = self.get_window_rect(window_handle)

        if work_area is None or window_rect is None:
            return

        work_left, work_top, work_right, work_bottom = work_area
        window_left, window_top, window_right, window_bottom = window_rect
        window_width = window_right - window_left
        window_height = window_bottom - window_top
        work_width = work_right - work_left
        work_height = work_bottom - work_top

        position_x = work_left + max(0, (work_width - window_width) // 2)
        position_y = work_top + max(0, (work_height - window_height) // 2)

        swp_no_size = 0x0001
        swp_no_z_order = 0x0004
        swp_no_activate = 0x0010
        flags = swp_no_size | swp_no_z_order | swp_no_activate

        user32.SetWindowPos(
            int(window_handle),
            0,
            position_x,
            position_y,
            0,
            0,
            flags,
        )

    def get_window_rect(self, window_handle):
        user32 = ctypes.windll.user32
        self.configure_window_api(user32)

        rect = wintypes.RECT()

        if not user32.GetWindowRect(int(window_handle), ctypes.byref(rect)):
            return None

        return (rect.left, rect.top, rect.right, rect.bottom)

    def get_window_work_area(self, window_handle):
        user32 = ctypes.windll.user32
        self.configure_window_api(user32)

        monitor_default_to_nearest = 0x00000002
        monitor_handle = user32.MonitorFromWindow(
            int(window_handle),
            monitor_default_to_nearest,
        )

        if not monitor_handle:
            return None

        monitor_info = MonitorInfo()
        monitor_info.cbSize = ctypes.sizeof(MonitorInfo)

        if not user32.GetMonitorInfoW(monitor_handle, ctypes.byref(monitor_info)):
            return None

        work_area = monitor_info.rcWork
        return (work_area.left, work_area.top, work_area.right, work_area.bottom)

    def configure_window_api(self, user32):
        user32.SetWindowPos.argtypes = (
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        )
        user32.SetWindowPos.restype = wintypes.BOOL
        user32.GetWindowRect.argtypes = (
            wintypes.HWND,
            ctypes.POINTER(wintypes.RECT),
        )
        user32.GetWindowRect.restype = wintypes.BOOL
        user32.MonitorFromWindow.argtypes = (
            wintypes.HWND,
            wintypes.DWORD,
        )
        user32.MonitorFromWindow.restype = wintypes.HANDLE
        user32.GetMonitorInfoW.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(MonitorInfo),
        )
        user32.GetMonitorInfoW.restype = wintypes.BOOL

    def set_screen_size(self, width, height):
        settings.FULLSCREEN = False
        settings.SCREEN_WIDTH = width
        settings.SCREEN_HEIGHT = height
        self.resize_window()

    def set_fullscreen(self):
        settings.FULLSCREEN = True
        self.resize_window()

    def quit(self):
        self.running = False
