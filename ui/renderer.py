import pygame

from settings import get_frame_duration
from .transform import Transform


class Renderer(Transform):
    def __init__(self, scene, pos_x, pos_y, width, height, image_route=None):
        super().__init__(pos_x, pos_y, width, height)

        self.scene = scene
        self.__base_image = None
        self.image = None

        if image_route is not None:
            self.set_base_image(image_route)

        self.scene.draw_listeners.append(self)

    def on_transform_updated(self):
        self.refresh_image()

    def refresh_image(self):
        if self.__base_image is None:
            self.image = None
            return

        _, _, width, height = self.get_transform()
        self.image = pygame.transform.smoothscale(self.__base_image, (int(width), int(height)))

    def set_base_image(self, base_image):
        if base_image is None:
            self.__base_image = None
            self.image = None
            return

        if isinstance(base_image, str):
            base_image = pygame.image.load(base_image).convert_alpha()

        self.__base_image = base_image
        self.refresh_image()

    def get_base_image(self):
        return self.__base_image

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(
                screen,
                (100, 150, 255),
                self.rect
            )

    def background_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.update(delta_time, game_events, mouse_position, wheel_move)

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.renderer_update(delta_time, game_events, mouse_position, wheel_move)

    def renderer_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass

    def destroy(self):
        self.scene.detach_listeners(self)


class AnimatedRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, image_route, frame_lengths=None, background=True, loop=True):
        super().__init__(scene, pos_x, pos_y, width, height)

        self.__base_images = []
        self.__images = []
        self.__frame_lengths = []
        self.delta_time = 0
        self.index = 0
        self.frame_duration = get_frame_duration()
        self.loop = loop
        self.status = True

        self.set_base_images(image_route)
        self.set_frame_lengths(frame_lengths)

        self.background = background

        if self.background:
            self.scene.background_listeners.append(self)
        else:
            self.scene.update_listeners.append(self)

    def get_base_images(self):
        return self.__base_images

    def get_images(self):
        return self.__images

    def get_frame_lengths(self):
        return self.__frame_lengths

    def set_frame_lengths(self, frame_lengths=None):
        if frame_lengths is None:
            self.__frame_lengths = [1 for _ in self.__images]
            return

        self.__frame_lengths = [max(1, frame_length) for frame_length in frame_lengths]

        if len(self.__frame_lengths) < len(self.__images):
            self.__frame_lengths.extend([1 for _ in range(len(self.__images) - len(self.__frame_lengths))])
        elif len(self.__frame_lengths) > len(self.__images):
            self.__frame_lengths = self.__frame_lengths[:len(self.__images)]

    def set_base_images(self, base_images):
        self.__base_images = []
        self.__images = []

        if base_images is None:
            self.set_base_image(None)
            self.__frame_lengths = []
            return

        _, _, width, height = self.get_transform()

        for base_image in base_images:
            if isinstance(base_image, str):
                base_image = pygame.image.load(base_image).convert_alpha()

            self.__base_images.append(base_image)
            self.__images.append(pygame.transform.smoothscale(base_image, (int(width), int(height))))

        if self.__images:
            self.index = min(self.index, len(self.__images) - 1)
            self.image = self.__images[self.index]
        else:
            self.image = None

        self.set_frame_lengths(self.__frame_lengths)

    def on_transform_updated(self):
        self.refresh_image()

    def refresh_image(self):
        self.set_base_images(self.__base_images)

    def animation_proceed(self, delta_time):
        if not self.status or not self.__images:
            return

        self.delta_time += delta_time

        while self.delta_time >= self.frame_duration * self.__frame_lengths[self.index]:
            self.delta_time -= self.frame_duration * self.__frame_lengths[self.index]

            if self.loop:
                self.index = (self.index + 1) % len(self.__images)
            elif self.index >= len(self.__images) - 1:
                self.index = len(self.__images) - 1
                self.status = False
                break
            else:
                self.index += 1

        self.image = self.__images[self.index]

    def background_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.update(delta_time, game_events, mouse_position, wheel_move)

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.animation_proceed(delta_time)
        self.animated_renderer_update(delta_time, game_events, mouse_position, wheel_move)

    def animated_renderer_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass


class ShiftRenderer(Renderer):
    def __init__(self, scene, pos_x, pos_y, width, height, background=True):
        super().__init__(scene, pos_x, pos_y, width, height)

        self.animations = {}
        self.shifts = {}
        self.delta_time = 0
        self.index = 0
        self.frame_duration = get_frame_duration()
        self.status = True
        self.current = None
        self.formal = None
        self.next_animation = None

        self.background = background

        if self.background:
            self.scene.background_listeners.append(self)
        else:
            self.scene.update_listeners.append(self)

    def add_animation(self, key, images, frame_lengths=None, loop=True, next_animation=None):
        base_images = self.load_base_images(images)
        images = self.scale_images(base_images)

        self.animations[key] = {
            "base_images": base_images,
            "images": images,
            "frame_lengths": self.get_animation_frame_lengths(images, frame_lengths),
            "loop": loop,
            "next_animation": next_animation,
        }

    def get_animation_frame_lengths(self, images, frame_lengths=None):
        if frame_lengths is None:
            return [1 for _ in images]

        frame_lengths = [max(1, frame_length) for frame_length in frame_lengths]

        if len(frame_lengths) < len(images):
            frame_lengths.extend([1 for _ in range(len(images) - len(frame_lengths))])
        elif len(frame_lengths) > len(images):
            frame_lengths = frame_lengths[:len(images)]

        return frame_lengths

    def add_shift(self, key, start, end):
        self.shifts[key] = {
            "start": start,
            "end": end,
        }

    def set_start(self, key):
        if key not in self.animations:
            return

        self.set_animation(key)

    def shift(self, key):
        if key not in self.shifts or key not in self.animations:
            return

        shift = self.shifts[key]

        if self.current != shift["start"]:
            return

        self.next_animation = shift["end"]
        self.set_animation(key, update_formal=False)

    def set_animation(self, key, update_formal=True):
        animation = self.animations[key]

        self.current = key
        self.index = 0
        self.delta_time = 0
        self.status = True

        if animation["loop"] and update_formal:
            self.formal = key

        if animation["images"]:
            self.image = animation["images"][self.index]
        else:
            self.image = None

    def on_transform_updated(self):
        self.refresh_image()

    def refresh_image(self):
        for animation in self.animations.values():
            animation["images"] = self.scale_images(animation["base_images"])

        if self.current is None or self.current not in self.animations:
            self.image = None
            return

        images = self.animations[self.current]["images"]

        if images:
            self.index = min(self.index, len(images) - 1)
            self.image = images[self.index]
        else:
            self.image = None

    def load_base_images(self, images):
        base_images = []

        for image in images:
            if isinstance(image, str):
                image = pygame.image.load(image).convert_alpha()

            base_images.append(image)

        return base_images

    def scale_images(self, images):
        _, _, width, height = self.get_transform()
        return [pygame.transform.smoothscale(image, (int(width), int(height))) for image in images]

    def animation_proceed(self, delta_time):
        if self.current is None or self.current not in self.animations:
            return

        animation = self.animations[self.current]
        images = animation["images"]
        frame_lengths = animation["frame_lengths"]

        if not self.status or not images:
            self.finish_animation()
            return

        self.delta_time += delta_time

        while self.delta_time >= self.frame_duration * frame_lengths[self.index]:
            self.delta_time -= self.frame_duration * frame_lengths[self.index]

            if animation["loop"]:
                self.index = (self.index + 1) % len(images)
            elif self.index >= len(images) - 1:
                self.index = len(images) - 1
                self.status = False
                break
            else:
                self.index += 1

        self.image = images[self.index]

        if not self.status:
            self.finish_animation()

    def finish_animation(self):
        if self.next_animation is not None:
            next_animation = self.next_animation
            self.next_animation = None

            if next_animation in self.animations:
                self.set_animation(next_animation)
                return

        animation = self.animations[self.current]
        next_animation = animation["next_animation"]

        if next_animation is not None and next_animation in self.animations:
            self.set_animation(next_animation)
            return

        self.return_formal()

    def return_formal(self):
        if self.formal is None or self.current == self.formal or self.formal not in self.animations:
            return

        self.set_animation(self.formal)

    def background_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.update(delta_time, game_events, mouse_position, wheel_move)

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.animation_proceed(delta_time)
        self.shift_renderer_update(delta_time, game_events, mouse_position, wheel_move)

    def shift_renderer_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass
