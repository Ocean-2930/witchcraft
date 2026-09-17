import pygame

from ui.renderer import Renderer


class MaterialNotice(Renderer):
    """재료 슬롯 위에 잠시 나타났다 사라지는 합성 오류 안내."""

    draw_layer = 250

    def __init__(self, scene):
        super().__init__(scene, 0, 0, 1, 1)
        self.font = scene.item_font
        self.message = ""
        self.remaining = 0
        self.anchor = (0, 0)

    def show(self, message, slot_rect):
        self.message = message
        self.anchor = slot_rect.midtop
        self.remaining = 2.0

    def hide(self):
        self.message = ""
        self.remaining = 0

    def advance(self, delta_time):
        self.remaining = max(0, self.remaining - delta_time)
        if not self.remaining:
            self.message = ""

    def draw(self, screen):
        if not self.message:
            return
        text = self.font.render(self.message, True, (255, 155, 155))
        surface = pygame.Surface((text.get_width() + 20, text.get_height() + 16), pygame.SRCALPHA)
        pygame.draw.rect(surface, (35, 19, 24, 245), surface.get_rect(), border_radius=5)
        pygame.draw.rect(surface, (180, 85, 95), surface.get_rect(), 1, border_radius=5)
        surface.blit(text, (10, 8))
        surface.set_alpha(min(255, int(self.remaining / 0.4 * 255)))
        rect = surface.get_rect(midbottom=(self.anchor[0], self.anchor[1] - 8))
        rect.clamp_ip(screen.get_rect().inflate(-16, -16))
        screen.blit(surface, rect)
