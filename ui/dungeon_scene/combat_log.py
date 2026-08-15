import pygame

from ui.renderer import Renderer


class CombatLogRenderer(Renderer):
    """던전 전투 로그를 최신 항목이 아래에 오도록 표시한다."""

    draw_layer = 60
    PADDING_X = 14
    PADDING_Y = 12
    LINE_HEIGHT = 25

    def __init__(
        self,
        scene,
        log_getter,
        pos_x,
        pos_y,
        width,
        max_log_count,
    ):
        self.log_getter = log_getter
        self.max_log_count = max(1, int(max_log_count))
        self.log_font = pygame.font.SysFont("malgungothic", 15)
        height = (
            self.PADDING_Y * 2
            + self.LINE_HEIGHT * self.max_log_count
        )
        super().__init__(scene, pos_x, pos_y, width, height)

    def draw(self, screen):
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (16, 20, 25, 208),
            panel.get_rect(),
            border_radius=6,
        )
        pygame.draw.rect(
            panel,
            (105, 116, 125, 220),
            panel.get_rect(),
            width=2,
            border_radius=6,
        )

        logs = list(self.log_getter())[-self.max_log_count :]
        bottom = self.rect.height - self.PADDING_Y
        for index, message in enumerate(reversed(logs)):
            text = self.log_font.render(str(message), True, (226, 231, 235))
            text_rect = text.get_rect(
                left=self.PADDING_X,
                bottom=bottom - index * self.LINE_HEIGHT,
            )
            panel.blit(text, text_rect)

        screen.blit(panel, self.rect)
