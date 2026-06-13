class Scene:
    def __init__(self, game):
        self.game = game

        self.parent_scene = None
        self.overlay_scene = None

        self.background_listeners = []
        self.update_listeners = []
        self.draw_listeners = []

        self.scene_initialize()

    def scene_initialize(self):
        pass

    def update(self, delta_time, game_events, mouse_position, wheel_move):
        self.scene_background_update(delta_time, game_events, mouse_position, wheel_move)

        if self.overlay_scene is None:
            self.scene_update(delta_time, game_events, mouse_position, wheel_move)
        else:
            self.overlay_scene.update(delta_time, game_events, mouse_position, wheel_move)

    def scene_background_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass

    def scene_update(self, delta_time, game_events, mouse_position, wheel_move):
        pass

    def draw(self):
        self.scene_draw()

        if self.overlay_scene:
            self.overlay_scene.draw()

    def scene_draw(self):
        pass

    def add_overlay(self, overlay_scene):
        self.overlay_scene = overlay_scene
        overlay_scene.parent_scene = self

    def exit_scene(self):
        if self.parent_scene is None:
            self.game.quit()
            return

        parent = self.parent_scene
        self.parent_scene = None
        parent.overlay_scene = None

"""
고정 + 애니메이션
UI +

1. UI

2. 애니메이션

3. 음성

이 3개를 제어하는 방법을 생각하고 여기에 넣어야 한다
"""
