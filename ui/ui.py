from .renderer import Renderer
from .transform import Transform


class UIElement(Transform):
    def __init__(self, scene=None, renderer: Renderer = None, pos_x=None, pos_y=None, width=None, height=None, background=True):
        self.owns_renderer = renderer is None

        if renderer is None:
            if scene is None:
                raise ValueError("UIElement requires a scene when renderer is not provided.")

            renderer = Renderer(scene, pos_x, pos_y, width, height)
        else:
            pos_x, pos_y, width, height = renderer.get_transform()

            if scene is None:
                scene = renderer.scene

        if scene is None:
            raise ValueError("UIElement requires a scene.")

        super().__init__(pos_x, pos_y, width, height)

        self.scene = scene
        self.renderer = renderer
        self.sub_ui = []
        self.background = background

        self.scene.ui_listener.append(self)

        if self.background:
            self.scene.background_listeners.append(self)
        else:
            self.scene.update_listeners.append(self)

    def on_transform_updated(self):
        self.renderer.set_transform(*self.get_transform())
        self.update_sub_ui()

    def add_sub_ui(self, ui_element, pos_x, pos_y):
        """
        !! caution !!
        all child ui must be made after parent ui as scene operates UI element in reversed registration order 
        """
        self.sub_ui.append((ui_element, pos_x, pos_y))
        self.update_sub_ui()

    def update_sub_ui(self):
        for ui_element, pos_x, pos_y in self.sub_ui:
            _, _, width, height = ui_element.get_transform()
            ui_element.set_transform(self.rect.left + pos_x, self.rect.top + pos_y, width, height)
    
    def pos_check(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def background_update(self, delta_time, game_events, mouse_position, wheel_move):
        self.update(delta_time, game_events, mouse_position, wheel_move)

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.ui_element_update(delta_time, game_events, mouse_position, wheel_move)

    def ui_element_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass

    def destroy(self):
        self.scene.detach_listeners(self)

        if self.owns_renderer:
            self.renderer.destroy()

        for ui_element, _, _ in self.sub_ui:
            ui_element.destroy()

    def on_left_click(self):
        pass

    def on_wheel_click(self):
        pass

    def on_right_click(self):
        pass

    def on_enter(self):
        pass

    def on_hover(self, delta_time, game_events, mouse_position, wheel_move):
        pass

    def on_exit(self):
        pass
    
