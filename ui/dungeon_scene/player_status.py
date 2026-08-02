import pygame

from ui.renderer import Renderer


class PlayerStatusRenderer(Renderer):
    draw_layer = 50

    def __init__(
        self,
        scene,
        player_getter,
        pos_x,
        pos_y,
        profile_size=92,
        value_width=82,
        bar_width=220,
        profile_image=None,
    ):
        self.player_getter = player_getter
        self.profile_size = profile_size
        self.value_width = value_width
        self.bar_width = bar_width
        self.content_gap = 10
        self.bar_height = 32
        self.bar_gap = 12
        self.profile_image = profile_image
        self.label_font = pygame.font.SysFont("malgungothic", 15, bold=True)
        self.value_font = pygame.font.SysFont("malgungothic", 16, bold=True)
        self.profile_font = pygame.font.SysFont("malgungothic", 15, bold=True)

        width = (
            profile_size
            + self.content_gap
            + value_width
            + self.content_gap
            + bar_width
        )
        super().__init__(scene, pos_x, pos_y, width, profile_size)

    def draw(self, screen):
        player = self.player_getter()
        profile_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.profile_size,
            self.profile_size,
        )
        self.draw_profile(screen, profile_rect)

        bar_x = profile_rect.right + self.content_gap
        value_x = bar_x + self.bar_width + self.content_gap
        first_bar_y = self.rect.top + (
            self.profile_size - (self.bar_height * 2 + self.bar_gap)
        ) // 2

        self.draw_resource_row(
            screen,
            "HP",
            player.hp,
            player.max_hp,
            value_x,
            bar_x,
            first_bar_y,
            (190, 49, 55),
            (91, 30, 34),
        )
        self.draw_resource_row(
            screen,
            "MP",
            player.mp,
            player.max_mp,
            value_x,
            bar_x,
            first_bar_y + self.bar_height + self.bar_gap,
            (49, 105, 190),
            (29, 48, 87),
        )

    def draw_profile(self, screen, profile_rect):
        pygame.draw.rect(screen, (31, 39, 49), profile_rect, border_radius=5)

        if self.profile_image is not None:
            image = pygame.transform.smoothscale(
                self.profile_image,
                profile_rect.size,
            )
            screen.blit(image, profile_rect)
        else:
            text_surface = self.profile_font.render(
                "프로필",
                True,
                (151, 165, 177),
            )
            screen.blit(
                text_surface,
                text_surface.get_rect(center=profile_rect.center),
            )

        pygame.draw.rect(
            screen,
            (126, 139, 151),
            profile_rect,
            width=2,
            border_radius=5,
        )

    def draw_resource_row(
        self,
        screen,
        label,
        current,
        maximum,
        value_x,
        bar_x,
        bar_y,
        fill_color,
        empty_color,
    ):
        current = max(0, current)
        maximum = max(0, maximum)
        ratio = min(1.0, current / maximum) if maximum > 0 else 0.0

        value_rect = pygame.Rect(
            value_x,
            bar_y,
            self.value_width,
            self.bar_height,
        )
        value_surface = self.value_font.render(
            f"{current} / {maximum}",
            True,
            (239, 243, 246),
        )
        screen.blit(
            value_surface,
            value_surface.get_rect(midleft=value_rect.midleft),
        )

        bar_rect = pygame.Rect(
            bar_x,
            bar_y,
            self.bar_width,
            self.bar_height,
        )
        pygame.draw.rect(screen, empty_color, bar_rect, border_radius=5)

        fill_width = round(bar_rect.width * ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(
                bar_rect.left,
                bar_rect.top,
                fill_width,
                bar_rect.height,
            )
            pygame.draw.rect(screen, fill_color, fill_rect, border_radius=5)

        pygame.draw.rect(
            screen,
            (128, 139, 149),
            bar_rect,
            width=2,
            border_radius=5,
        )

        label_surface = self.label_font.render(
            label,
            True,
            (247, 240, 232),
        )
        screen.blit(
            label_surface,
            label_surface.get_rect(
                midleft=(bar_rect.left + 9, bar_rect.centery)
            ),
        )
