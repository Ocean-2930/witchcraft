from settings import MOUSE_LEFT, MOUSE_MIDDLE, MOUSE_RIGHT


class Scene:
    def __init__(self, game):
        self.game = game

        self.parent_scene = None
        self.overlay_scene = None

        self.ui_focus = None
        self.ui_listener = []
        self.background_listeners = []
        self.update_listeners = []
        self.draw_listeners = []

        self.scene_initialize()

    def scene_initialize(self):
        pass

    def operate_ui(self, delta_time, game_events, mouse_position, wheel_move):
        previous_focus = self.ui_focus
        current_focus = None

        if mouse_position is not None:
            for ui in reversed(self.ui_listener):
                if ui.pos_check(mouse_position):
                    current_focus = ui
                    break

        self.ui_focus = current_focus

        if previous_focus != self.ui_focus:
            if previous_focus is not None:
                previous_focus.on_exit()

            if self.ui_focus is not None:
                self.ui_focus.on_enter()

        if self.ui_focus is None:
            return

        self.ui_focus.on_hover(delta_time, game_events, mouse_position, wheel_move)

        if game_events[MOUSE_LEFT]["keydown"]:
            self.ui_focus.on_left_click()
        elif game_events[MOUSE_RIGHT]["keydown"]:
            self.ui_focus.on_right_click()
        elif game_events[MOUSE_MIDDLE]["keydown"]:
            self.ui_focus.on_wheel_click()

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.scene_background_update(delta_time, game_events, mouse_position, wheel_move)

        if self.overlay_scene is None:
            self.operate_ui(delta_time, game_events, mouse_position, wheel_move)
            self.scene_update(delta_time, game_events, mouse_position, wheel_move)
        else:
            self.overlay_scene.update(delta_time, game_events, mouse_position, wheel_move)

    def scene_background_update(self, delta_time, game_events, mouse_position, wheel_move):
        for listener in self.background_listeners[:]:
            listener.background_update(delta_time, game_events, mouse_position, wheel_move)

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        for listener in self.update_listeners[:]:
            listener.update(delta_time, game_events, mouse_position, wheel_move)

    def draw(self):
        self.scene_draw()

        if self.overlay_scene:
            self.overlay_scene.draw()

    def scene_draw(self):
        for listener in self.draw_listeners[:]:
            listener.draw(self.game.virtual_screen)

    def detach_listeners(self, obj):
        for listeners in (self.ui_listener, self.background_listeners, self.update_listeners, self.draw_listeners):
            while obj in listeners:
                listeners.remove(obj)

    def add_overlay(self, overlay_scene):
        self.overlay_scene = overlay_scene
        overlay_scene.parent_scene = self

    def switch_scene(self, new_scene):
        self.game.scene = new_scene

    def exit_scene(self):
        if self.parent_scene is None:
            self.game.quit()
            return

        parent = self.parent_scene
        self.parent_scene = None
        parent.overlay_scene = None
