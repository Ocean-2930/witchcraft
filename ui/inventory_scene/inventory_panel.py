import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer


class InventoryPanelRenderer(Renderer):
    draw_layer = -100

    def __init__(self, scene, panel_width, panel_height):
        self.panel_width = panel_width
        self.panel_height = panel_height
        super().__init__(
            scene,
            VIRTUAL_WIDTH // 2,
            VIRTUAL_HEIGHT // 2,
            VIRTUAL_WIDTH,
            VIRTUAL_HEIGHT,
        )

    def draw(self, screen):
        dim_surface = pygame.Surface(
            (VIRTUAL_WIDTH, VIRTUAL_HEIGHT),
            pygame.SRCALPHA,
        )
        dim_surface.fill((4, 7, 11, 110))
        screen.blit(dim_surface, (0, 0))

        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA,
        )
        panel_surface.fill((22, 28, 36, 225))
        panel_rect = panel_surface.get_rect(
            center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2)
        )
        screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(
            screen,
            (132, 148, 164),
            panel_rect,
            width=2,
            border_radius=8,
        )
        pygame.draw.line(
            screen,
            (105, 119, 133),
            (panel_rect.left + 30, panel_rect.top + 104),
            (panel_rect.right - 30, panel_rect.top + 104),
            width=2,
        )
