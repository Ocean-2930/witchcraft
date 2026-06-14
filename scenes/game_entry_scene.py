import pygame

from .scene import Scene
from settings import ESCAPE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui import GameEntryStartButton, PauseButton


class GameEntryScene(Scene):
    def scene_initialize(self):
        self.button_font = pygame.font.SysFont("malgungothic", 32, bold=True)

        self.start_button = GameEntryStartButton(
            self,
            "게임 시작",
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            280,
            64,
            self.start_game,
        )
        self.pause_button = PauseButton(
            self,
            VIRTUAL_WIDTH - 42,
            42,
            48,
            48,
            self.open_pause,
        )

    def start_game(self):
        from .dungeon_scene import DungeonScene

        self.switch_scene(DungeonScene(self.game))

    def open_pause(self):
        from .pause_scene import PauseScene

        self.add_overlay(PauseScene(self.game))

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        if game_events[ESCAPE]["keydown"]:
            self.open_pause()

        super().scene_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_draw(self):
        screen = self.game.virtual_screen
        screen.fill((18, 22, 29))

        super().scene_draw()
