import pygame

from ui.renderer import Renderer


class HotbarRenderer(Renderer):
    draw_layer = 50
    LABELS = (
        ("1", "2", "3", "4"),
        ("Q", "W", "E", "R"),
    )

    def __init__(self, scene, pos_x, pos_y, slot_size, slot_gap, item_getter):
        width = slot_size * 4 + slot_gap * 3
        height = slot_size * 2 + slot_gap
        super().__init__(scene, pos_x, pos_y, width, height)

        self.slot_size = slot_size
        self.slot_gap = slot_gap
        self.item_getter = item_getter
        self.active_label = None
        self.font = pygame.font.SysFont("malgungothic", 16, bold=True)

    def set_active_label(self, label):
        self.active_label = label

    def draw(self, screen):
        for row_index, row in enumerate(self.LABELS):
            for column_index, label in enumerate(row):
                slot_rect = pygame.Rect(
                    self.rect.left + column_index * (self.slot_size + self.slot_gap),
                    self.rect.top + row_index * (self.slot_size + self.slot_gap),
                    self.slot_size,
                    self.slot_size,
                )

                is_active = label == self.active_label
                fill_color = (78, 66, 54) if is_active else (38, 42, 46)
                border_color = (236, 200, 124) if is_active else (140, 146, 148)
                text_color = (255, 238, 190) if is_active else (230, 234, 232)

                pygame.draw.rect(screen, fill_color, slot_rect, border_radius=4)
                pygame.draw.rect(screen, border_color, slot_rect, width=2, border_radius=4)

                item_instance = self.item_getter(label)
                item = getattr(item_instance, "item", None)
                item_sprite = (
                    item.get_sprite(item.item_code)
                    if item is not None
                    else None
                )
                if item_sprite is not None:
                    image_size = (self.slot_size - 16, self.slot_size - 16)
                    image = pygame.transform.smoothscale(item_sprite, image_size)
                    image_rect = image.get_rect(center=slot_rect.center)
                    screen.blit(image, image_rect)

                if item_instance is not None:
                    stack_surface = self.font.render(
                        str(item_instance.stack),
                        True,
                        (246, 224, 148),
                    )
                    stack_rect = stack_surface.get_rect(
                        bottomright=(slot_rect.right - 7, slot_rect.bottom - 5)
                    )
                    screen.blit(stack_surface, stack_rect)

                text_surface = self.font.render(label, True, text_color)
                text_rect = text_surface.get_rect(
                    topleft=(slot_rect.left + 6, slot_rect.top + 4)
                )
                screen.blit(text_surface, text_rect)
