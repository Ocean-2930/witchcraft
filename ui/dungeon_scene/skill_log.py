import pygame

from ui.renderer import Renderer


class SkillLogRenderer(Renderer):
    draw_layer = 50

    def __init__(self, scene, pos_x, pos_y, width, height):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.text = ""
        self.font = pygame.font.SysFont("malgungothic", 18, bold=True)

    def set_text(self, text):
        self.text = text

    def draw(self, screen):
        if not self.text:
            return

        pygame.draw.rect(screen, (18, 22, 25), self.rect, border_radius=4)
        pygame.draw.rect(screen, (126, 132, 134), self.rect, width=2, border_radius=4)

        text_surface = self.font.render(self.text, True, (238, 234, 220))
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
