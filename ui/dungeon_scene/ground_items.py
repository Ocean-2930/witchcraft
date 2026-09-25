import pygame

from ui.renderer import Renderer


class GroundItemsRenderer(Renderer):
    """한 타일의 바닥 아이템을 최대 세 장의 겹친 아이콘으로 표시한다."""

    draw_layer = -90
    ICON_SIZE = 32
    MAX_ICONS = 3

    def __init__(self, scene, pos_x, pos_y, items_getter):
        self.items_getter = items_getter
        self.scaled_images = {}
        super().__init__(scene, pos_x, pos_y, 48, 42)

    def draw(self, screen):
        items = self.items_getter()[:self.MAX_ICONS]
        for index, instance in enumerate(items):
            code = instance.item.item_code
            if code not in self.scaled_images:
                source = instance.item.get_sprite(code)
                if source is None:
                    continue
                width, height = source.get_size()
                scale = self.ICON_SIZE / max(width, height)
                self.scaled_images[code] = pygame.transform.smoothscale(
                    source, (max(1, round(width * scale)), max(1, round(height * scale)))
                )
            image = self.scaled_images[code]
            offset = index - (len(items) - 1) / 2
            center = (round(self.rect.centerx + offset * 9), round(self.rect.centery + offset * 5))
            screen.blit(image, image.get_rect(center=center))
