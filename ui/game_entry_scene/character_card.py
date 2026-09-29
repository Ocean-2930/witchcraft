from pathlib import Path

import pygame

from ui.renderer import Renderer
from ui.ui import UIElement


class CharacterCardRenderer(Renderer):
    def __init__(self, scene, x, y, width, height, card):
        self.card = card
        path = Path(__file__).resolve().parents[2] / "assets" / "images" / "characters" / card.code / "full_shot.png"
        source = pygame.image.load(str(path)).convert_alpha()
        scale = min((width - 24) / source.get_width(), (height - 92) / source.get_height())
        self.portrait = pygame.transform.smoothscale(
            source, (max(1, round(source.get_width() * scale)), max(1, round(source.get_height() * scale)))
        )
        super().__init__(scene, x, y, width, height)

    def draw(self, screen):
        previous_clip = screen.get_clip()
        screen.set_clip(previous_clip.clip(self.card.scene.character_viewport))
        try:
            self.draw_card(screen)
        finally:
            screen.set_clip(previous_clip)

    def draw_card(self, screen):
        image_area = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height - 68)
        border_color = (232, 234, 238) if self.card.is_hovered else (174, 178, 186)
        background_color = (48, 51, 57) if self.card.is_hovered else (32, 35, 41)
        pygame.draw.rect(screen, background_color, image_area)
        screen.blit(self.portrait, self.portrait.get_rect(midbottom=(image_area.centerx, image_area.bottom - 12)))
        pygame.draw.rect(screen, border_color, image_area, width=2)
        label = pygame.Rect(self.rect.left, self.rect.bottom - 56, self.rect.width, 56)
        color = (104, 108, 116) if self.card.is_hovered else (70, 74, 82)
        pygame.draw.rect(screen, color, label)
        pygame.draw.rect(screen, border_color, label, width=2)
        text = self.card.scene.button_font.render(self.card.name, True, (242, 243, 245))
        screen.blit(text, text.get_rect(center=label.center))


class CharacterCard(UIElement):
    def __init__(self, scene, definition, x, y, width, height):
        self.code = definition["code"]
        self.name = definition["name"]
        self.is_hovered = False
        renderer = CharacterCardRenderer(scene, x, y, width, height, self)
        super().__init__(scene, renderer=renderer)

    def on_enter(self):
        self.is_hovered = True

    def pos_check(self, mouse_pos):
        return self.scene.character_viewport.collidepoint(mouse_pos) and super().pos_check(mouse_pos)

    def on_exit(self):
        self.is_hovered = False

    def on_left_click(self):
        self.scene.select_character(self.code)

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
