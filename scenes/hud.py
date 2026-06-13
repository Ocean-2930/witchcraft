import pygame

from .scene import Scene


class Hud(Scene):
    def scene_initialize(self):
        self.font = pygame.font.Font(None, 24)
        self.text_color = (255, 255, 255)
        self.line_height = 22
        self.delta_time = 0.0
        self.game_events = {}
        self.mouse_position = None
        self.wheel_move = 0

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.delta_time = delta_time
        self.game_events = game_events
        self.mouse_position = mouse_position
        self.wheel_move = wheel_move

    def scene_draw(self):
        lines = [
            f"delta_time: {self.delta_time:.4f}",
            f"mouse_position: {self.mouse_position}",
            f"wheel_move: {self.wheel_move}",
            "game_events:",
        ]

        for key, value in self.game_events.items():
            lines.append(f"  {key}: {value}")

        for index, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            self.game.virtual_screen.blit(text_surface, (12, 12 + index * self.line_height))
