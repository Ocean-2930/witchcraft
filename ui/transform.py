import pygame


class Transform:
    def __init__(self, pos_x, pos_y, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (pos_x, pos_y)

    def get_transform(self):
        return (*self.rect.center, self.rect.width, self.rect.height)

    def get_root_transform(self):
        return (*self.rect.topleft, self.rect.width, self.rect.height)

    def get_root(self):
        return self.rect.topleft

    def get_head(self):
        return self.rect.bottomright

    def set_transform(self, pos_x=None, pos_y=None, width=None, height=None):
        if pos_x is None:
            pos_x = self.rect.centerx
        if pos_y is None:
            pos_y = self.rect.centery
        if width is None:
            width = self.rect.width
        if height is None:
            height = self.rect.height

        self.rect.size = (width, height)
        self.rect.center = (pos_x, pos_y)

        self.on_transform_updated()

    def on_transform_updated(self):
        pass
