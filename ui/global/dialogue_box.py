import pygame

from settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from ui.renderer import Renderer
from ui.ui import UIElement


class DialogueBoxRenderer(Renderer):
    draw_layer = 100

    def __init__(self, scene, pos_x, pos_y, width, height, dialogue_box):
        super().__init__(scene, pos_x, pos_y, width, height)
        self.dialogue_box = dialogue_box

    def draw(self, screen):
        dialogue_box = self.dialogue_box
        if not dialogue_box.visible:
            return

        pygame.draw.rect(screen, (13, 15, 22), self.rect, border_radius=10)
        pygame.draw.rect(
            screen,
            (126, 111, 154),
            self.rect,
            width=2,
            border_radius=10,
        )

        if dialogue_box.speaker:
            self.draw_speaker_name(screen)

        dialogue_box.draw_text(screen)

    def draw_speaker_name(self, screen):
        dialogue_box = self.dialogue_box
        name_surface = dialogue_box.name_font.render(
            dialogue_box.speaker,
            True,
            (248, 244, 255),
        )
        name_width = max(148, name_surface.get_width() + 40)
        name_rect = pygame.Rect(
            self.rect.left + 24,
            self.rect.top - 25,
            name_width,
            50,
        )

        pygame.draw.rect(screen, (47, 39, 66), name_rect, border_radius=8)
        pygame.draw.rect(
            screen,
            (147, 126, 180),
            name_rect,
            width=2,
            border_radius=8,
        )
        screen.blit(name_surface, name_surface.get_rect(center=name_rect.center))


class DialogueBox(UIElement):
    def __init__(
        self,
        scene,
        speaker="",
        text="",
        pos_x=VIRTUAL_WIDTH // 2,
        pos_y=VIRTUAL_HEIGHT - 110,
        width=VIRTUAL_WIDTH - 96,
        height=172,
    ):
        self.speaker = speaker
        self.text = text
        self.visible = True
        self.name_font = pygame.font.SysFont("malgungothic", 22, bold=True)
        self.text_font = pygame.font.SysFont("malgungothic", 22)
        renderer = DialogueBoxRenderer(
            scene,
            pos_x,
            pos_y,
            width,
            height,
            self,
        )
        super().__init__(scene, renderer=renderer, background=False)

    def set_dialogue(self, speaker, text):
        self.speaker = speaker
        self.text = text

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def pos_check(self, mouse_pos):
        return False

    def draw_text(self, screen):
        left = self.rect.left + 32
        top = self.rect.top + 40
        available_width = self.rect.width - 64
        available_height = self.rect.bottom - 24 - top
        line_height = self.text_font.get_linesize() + 5
        maximum_lines = max(1, available_height // line_height)
        lines = self.wrap_text(self.text, available_width)
        visible_lines = lines[:maximum_lines]

        if len(lines) > maximum_lines and visible_lines:
            visible_lines[-1] = self.ellipsize(visible_lines[-1], available_width)

        for index, line in enumerate(visible_lines):
            text_surface = self.text_font.render(line, True, (225, 220, 235))
            screen.blit(text_surface, (left, top + index * line_height))

    def wrap_text(self, text, available_width):
        lines = []
        current = ""

        for character in text:
            if character == "\n":
                lines.append(current)
                current = ""
                continue

            candidate = current + character
            if current and self.text_font.size(candidate)[0] > available_width:
                lines.append(current)
                current = character
            else:
                current = candidate

        if current or not lines:
            lines.append(current)

        return lines

    def ellipsize(self, text, available_width):
        while text and self.text_font.size(text + "…")[0] > available_width:
            text = text[:-1]
        return text + "…"

    def destroy(self):
        super().destroy()
        self.renderer.destroy()
