from pathlib import Path

import pygame

from ui.renderer import Renderer
from .textures import DUNGEON_TEXTURES


ASSET_DIRECTORY = Path("assets/images/ui/combat_timeline")


class CombatTimelineRenderer(Renderer):
    draw_layer = 50
    TICK_INTERVAL = 100
    MAX_BADGES = 8
    BADGE_SIZE = (27, 36)
    BADGE_GAP = 6
    DIVIDER_WIDTH = 18

    def __init__(
        self,
        scene,
        player_getter,
        turn_counter_getter,
        pos_x,
        pos_y,
        width=424,
        height=84,
        enemy_turns_getter=None,
    ):
        self.player_getter = player_getter
        self.turn_counter_getter = turn_counter_getter
        self.enemy_turns_getter = enemy_turns_getter or (lambda: ())
        self.profile_image = DUNGEON_TEXTURES.get_scaled(
            "player_profile",
            21,
            21,
        )
        self.badge_image = self.load_image("player_badge.png")
        self.enemy_badge_image = self.load_image("enemy_badge.png")
        self.action_images = {
            "attack": self.load_image("attack.png"),
            "move": self.load_image("move.png"),
        }
        self.tick_font = pygame.font.Font(None, 16)
        super().__init__(scene, pos_x, pos_y, width, height)

    @staticmethod
    def load_image(filename):
        return pygame.image.load(ASSET_DIRECTORY / filename).convert_alpha()

    def draw(self, screen):
        player = self.player_getter()
        turn_counter = self.turn_counter_getter()
        events = self.build_events(
            player.attack_turn_cost,
            player.move_turn_cost,
            self.enemy_turns_getter(),
        )
        tokens = self.build_timeline_tokens(events, turn_counter)
        token_widths = [
            self.BADGE_SIZE[0] if token[0] == "badge" else self.DIVIDER_WIDTH
            for token in tokens
        ]
        cursor_x = self.rect.left

        for token, token_width in zip(tokens, token_widths):
            center_x = cursor_x + token_width // 2
            if token[0] == "badge":
                self.draw_action_badge(
                    screen,
                    center_x,
                    token[1],
                    token[2],
                    token[3],
                )
            else:
                self.draw_tick_divider(
                    screen,
                    center_x,
                    token[1],
                )
            cursor_x += token_width + self.BADGE_GAP

    @classmethod
    def build_events(cls, attack_cost, move_cost, enemy_turns=()):
        return sorted(
            [
                (attack_cost, "attack", "player"),
                (move_cost, "move", "player"),
                *((turn_tick, "turn", "enemy") for turn_tick in enemy_turns),
            ],
            key=lambda event: (event[0], event[2] == "enemy", event[1]),
        )[:cls.MAX_BADGES]

    @classmethod
    def build_player_events(cls, attack_cost, move_cost):
        """플레이어 전용 호출을 위한 이전 인터페이스를 유지한다."""
        return cls.build_events(attack_cost, move_cost)

    @classmethod
    def build_timeline_tokens(cls, events, turn_counter):
        tokens = []
        next_divider = cls.TICK_INTERVAL - turn_counter

        for tick, action, owner in events:
            while next_divider < tick:
                tokens.append(("divider", next_divider))
                next_divider += cls.TICK_INTERVAL

            tokens.append(("badge", tick, action, owner))

            while next_divider == tick:
                tokens.append(("divider", next_divider))
                next_divider += cls.TICK_INTERVAL

        return tokens

    def draw_action_badge(self, screen, center_x, relative_tick, action, owner):
        tick_label = self.tick_font.render(
            str(relative_tick),
            True,
            (211, 220, 227),
        )
        screen.blit(
            tick_label,
            tick_label.get_rect(midtop=(center_x, self.rect.top)),
        )

        badge_image = self.enemy_badge_image if owner == "enemy" else self.badge_image
        badge = pygame.transform.smoothscale(badge_image, self.BADGE_SIZE)
        badge_rect = badge.get_rect(midtop=(center_x, self.rect.top + 15))
        screen.blit(badge, badge_rect)

        if owner == "player" and self.profile_image is not None:
            profile_rect = self.profile_image.get_rect(
                center=(badge_rect.centerx, badge_rect.top + 12)
            )
            screen.blit(self.profile_image, profile_rect)

        if owner == "enemy":
            return

        action_image = pygame.transform.smoothscale(self.action_images[action], (11, 11))
        action_rect = action_image.get_rect(
            bottomright=(badge_rect.right - 1, badge_rect.bottom - 4)
        )
        screen.blit(action_image, action_rect)

    def draw_tick_divider(self, screen, center_x, relative_tick):
        pygame.draw.line(
            screen,
            (174, 183, 191),
            (center_x, self.rect.top + 15),
            (center_x, self.rect.top + 52),
            width=2,
        )
        label = self.tick_font.render(str(relative_tick), True, (183, 192, 200))
        screen.blit(
            label,
            label.get_rect(midtop=(center_x, self.rect.top + 56)),
        )
