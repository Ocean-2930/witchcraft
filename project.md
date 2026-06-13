# Pygame 2D Template Guide

이 문서는 현재 프로젝트 구조와 기본 클래스 사용 규칙을 정리한다. 코드는 작은 2D 게임을 빠르게 시작하기 위한 템플릿이며, `Scene`, `Renderer`, `UIElement`를 상속해서 기능을 추가하는 흐름을 기본으로 한다.

---

## 파일 구조

```text
project-root/
├─ .project/
├─ assets/
├─ core/
│  ├─ game.py
│  └─ debug_game.py
├─ data/
│  └─ data.json
├─ scenes/
│  ├─ __init__.py
│  ├─ scene.py
│  ├─ title_scene.py
│  └─ hud.py
├─ ui/
│  ├─ __init__.py
│  ├─ transform.py
│  ├─ renderer.py
│  └─ ui.py
├─ utilities/
│  └─ __init__.py
├─ develop.py
├─ main.py
├─ project.md
└─ settings.py
```

- `.project`: 기획, 메모, 설계 문서를 보관하는 폴더다.
- `assets`: 이미지, 폰트, 사운드 같은 게임 리소스를 보관한다.
- `core`: 게임 루프와 실행 환경을 관리한다.
- `data`: 사용자 데이터, 저장 데이터, 설정 데이터 같은 런타임 데이터를 보관한다.
- `scenes`: 화면 단위 로직과 화면 전환 로직을 관리한다.
- `ui`: 위치, 렌더링, UI 상호작용 기반 클래스를 관리한다.
- `utilities`: 여러 곳에서 재사용할 보조 함수를 두는 공간이다.

각 패키지의 `__init__.py`는 import 편의성을 위해 공개할 클래스만 정리한다. 개발 전용 파일이나 배포 때 빠질 수 있는 클래스는 굳이 package export에 넣지 않는다.

상속해서 새 클래스를 만들기 위한 base class는 `__init__.py`에 올리지 않는 것을 기본 규칙으로 한다. 예를 들어 `Scene`, `Renderer`, `UIElement`처럼 상속 재료로 쓰는 클래스는 필요한 파일에서 직접 경로로 import하고, 상속과 구성이 끝난 실제 사용 요소만 package import 대상으로 공개한다.

---

## 실행 진입점

`main.py`는 일반 실행 진입점이다.

```python
from core.game import Game

game = Game()
game.run()
```

`develop.py`는 개발 실행 진입점이다.

```python
from core.debug_game import DebugGame

game = DebugGame()
game.run()
```

배포 기준은 `main.py`와 `Game`이다. 입력 상태를 화면에 출력하는 HUD는 `develop.py`, `DebugGame`, `scenes/hud.py` 쪽에만 연결되어 있다.

---

## settings.py

프로젝트 전역 설정을 둔다.

사용자 설정:

- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: 실제 윈도우 크기다.
- `get_screen_size()`: `(SCREEN_WIDTH, SCREEN_HEIGHT)` 튜플을 반환한다.

게임 입력 상수:

- `MOUSE_LEFT`
- `MOUSE_MIDDLE`
- `MOUSE_RIGHT`
- `ARROW_UP`
- `ARROW_DOWN`
- `ARROW_LEFT`
- `ARROW_RIGHT`

개발 설정:

- `FPS`
- `get_frame_duration()`
- `VIRTUAL_WIDTH`
- `VIRTUAL_HEIGHT`
- `VIRTUAL_SIZE`
- `BACKGROUND_COLOR`
- `LETTERBOX_COLOR`

주의할 점:

- 런타임에 값이 바뀔 수 있는 사용자 설정은 `from settings import SCREEN_WIDTH`처럼 값 자체를 가져오기보다 `import settings` 후 `settings.get_screen_size()`처럼 읽는 편이 안전하다.
- `get_frame_duration()`은 `FPS` 기준으로 `round(1 / FPS, 4)` 값을 계산하고 캐싱한다. 이미 캐싱된 뒤 `FPS`를 바꾸면 기존 캐시가 남을 수 있다.
- `pygame.RESIZABLE`은 사용하지 않는다. 현재 윈도우 크기는 settings 값 기준으로 고정된다.

---

## core/game.py

`Game`은 Pygame 초기화, 입력 수집, 씬 업데이트, 렌더링, 종료를 담당한다.

주요 속성:

- `clock`: `delta_time` 계산에 사용한다.
- `running`: 메인 루프 실행 여부다.
- `screen`: 실제 윈도우 surface다.
- `virtual_screen`: 게임이 먼저 그려지는 가상 해상도 surface다.
- `display_scale`: 실제 윈도우에 맞춘 가상 화면 스케일이다.
- `display_offset`: letterbox 영역을 고려한 출력 위치다.
- `display_size`: 실제 윈도우에 출력될 가상 화면 크기다.
- `scene`: 현재 메인 씬이다.
- `game_events`: 추적할 키 입력 목록이다.
- `formal_events`: 직전 프레임 입력 상태다.

흐름:

```text
run()
├─ update()
│  ├─ read_inputs()
│  └─ update_scene(...)
└─ draw()
   ├─ virtual_screen.fill(BACKGROUND_COLOR)
   ├─ scene.draw()
   └─ present()
```

상속할 때:

- 일반적으로 `run()`을 바꾸지 않는다.
- 씬 업데이트 순서를 바꾸고 싶으면 `update_scene(...)`을 오버라이드한다.
- 렌더링 순서를 바꾸고 싶으면 `draw()`를 오버라이드한다.
- 종료는 `quit()`을 호출해서 `running = False`로 처리한다.

외부에서 자주 쓰는 함수:

- `window_to_virtual(window_pos)`: 실제 윈도우 좌표를 가상 화면 좌표로 변환한다. letterbox 영역이면 `None`을 반환한다.
- `resize_window()`: settings의 화면 크기를 읽고, `display_scale`, `display_size`, `display_offset`을 갱신한다.
- `quit()`: 메인 루프 종료를 요청한다.

주의할 점:

- 입력은 `Game.read_inputs()`에서 한 번만 수집한다. scene 내부에서 `pygame.event.get()`을 다시 호출하면 이벤트가 소모되어 입력 흐름이 꼬일 수 있다.
- `present()`는 매 프레임 호출되지만, 화면비와 출력 크기 계산은 `resize_window()`에서 처리한다.
- 게임 로직은 가능하면 `virtual_screen` 기준 좌표를 사용한다.

---

## core/debug_game.py

`DebugGame`은 `Game`을 상속한 개발용 실행 클래스다.

역할:

- `self.hud = Hud(self)`를 추가한다.
- `update_scene(...)`에서 메인 씬 업데이트 후 HUD 업데이트를 실행한다.
- `draw()`에서 메인 씬을 그린 뒤 HUD를 그린다.

상속할 때:

- 개발 중 표시할 보조 화면이나 디버그 도구는 `DebugGame` 쪽에 붙인다.
- 배포 대상 로직은 가능하면 `Game` 또는 실제 scene에 둔다.

---

## scenes/scene.py

`Scene`은 모든 화면의 기본 클래스다.

주요 속성:

- `game`: 현재 씬을 실행하는 `Game` 객체다.
- `parent_scene`: overlay 씬일 때 부모 씬이다.
- `overlay_scene`: 현재 씬 위에 올라온 overlay 씬이다.
- `ui_focus`: 현재 마우스 focus를 가진 UI다.
- `ui_listener`: UI focus, hover, click 처리를 받을 객체 목록이다.
- `background_listeners`: overlay 여부와 상관없이 업데이트되는 객체 목록이다.
- `update_listeners`: overlay가 없을 때 일반 업데이트되는 객체 목록이다.
- `draw_listeners`: draw 단계에서 그려질 객체 목록이다.

생명주기:

```text
Scene.__init__()
└─ scene_initialize()

update(...)
├─ scene_background_update(...)
├─ operate_ui(...)
└─ scene_update(...)

draw()
├─ scene_draw()
└─ overlay_scene.draw()
```

상속할 때 권장 순서:

1. `scene_initialize()`에 초기 객체 생성, renderer 생성, UI 생성, 상태값 초기화를 둔다.
2. 항상 돌아야 하는 로직은 `scene_background_update(...)`에 둔다.
3. overlay가 없을 때만 돌아야 하는 일반 로직은 `scene_update(...)`에 둔다.
4. 직접 그릴 것이 있으면 `scene_draw()`를 오버라이드한다.
5. `scene_draw()`를 오버라이드하면서 listener도 그리고 싶으면 마지막이나 원하는 위치에서 `super().scene_draw()`를 호출한다.

UI 처리:

- `operate_ui(...)`는 `ui_listener`를 뒤에서부터 검사한다.
- 처음 `pos_check(mouse_position)`이 통과한 UI가 focus가 된다.
- focus가 바뀌면 이전 UI의 `on_exit()`, 새 UI의 `on_enter()`가 호출된다.
- 현재 focus에는 `on_hover(...)`가 호출된다.
- 클릭은 한 프레임에 하나만 처리한다. 우선순위는 왼클릭, 오른클릭, 휠클릭 순서다.

외부에서 자주 쓰는 함수:

- `add_overlay(overlay_scene)`: 현재 씬 위에 overlay 씬을 올린다.
- `switch_scene(new_scene)`: `game.scene`을 새 씬으로 바꾼다.
- `exit_scene()`: overlay면 부모로 돌아가고, 부모가 없으면 `game.quit()`을 호출한다.
- `detach_listeners(obj)`: 모든 listener 목록에서 해당 객체를 제거한다.

주의할 점:

- listener 목록에 직접 넣은 객체는 목록에 맞는 메서드를 가져야 한다.
- `background_listeners`: `background_update(...)`
- `update_listeners`: `update(...)`
- `draw_listeners`: `draw(screen)`
- `ui_listener`: `pos_check(...)`, `on_enter()`, `on_hover(...)`, `on_exit()`, click hook들
- 객체를 삭제할 때는 직접 list에서 빼기보다 각 객체의 `destroy()`를 호출한다. 내부에서 `detach_listeners(...)`가 호출된다.

---

## scenes/title_scene.py

`TitleScene`은 현재 `Game`의 초기 씬이다.

역할:

- `Scene`을 상속한다.
- `scene_draw()`에서 배경색을 채운 뒤 `super().scene_draw()`로 draw listener를 그린다.

확장할 때:

- 시작 화면 UI, 로고, 메뉴, 시작 버튼은 `scene_initialize()`에서 생성한다.
- 입력과 상태 변화는 `scene_update(...)`에 둔다.

---

## scenes/hud.py

`Hud`는 개발용 입력 출력 씬이다.

역할:

- `Scene`을 상속한다.
- `scene_update(...)`에서 `delta_time`, `game_events`, `mouse_position`, `wheel_move`를 저장한다.
- `scene_draw()`에서 저장된 입력 상태를 화면 왼쪽 위에 출력한다.

주의할 점:

- `Hud`는 개발용이므로 `scenes/__init__.py`에서 export하지 않는다.
- `DebugGame`에서 직접 import해서 사용한다.

---

## ui/transform.py

`Transform`은 위치와 크기를 `pygame.Rect`로 관리하는 공통 기반 클래스다. `Renderer`와 `UIElement`가 상속한다.

생성:

```python
Transform(pos_x, pos_y, width, height)
```

`pos_x`, `pos_y`는 center 좌표로 사용된다.

외부 접근용 함수:

- `get_transform()`: `(center_x, center_y, width, height)`를 반환한다.
- `get_root_transform()`: `(left, top, width, height)`를 반환한다.
- `get_root()`: `rect.topleft`를 반환한다.
- `get_head()`: `rect.bottomright`를 반환한다.
- `set_transform(pos_x=None, pos_y=None, width=None, height=None)`: 전달된 값만 갱신하고, 마지막에 `on_transform_updated()`를 호출한다.

상속할 때:

- transform 변경에 반응해야 하면 `on_transform_updated()`를 오버라이드한다.
- `set_transform()` 자체를 바꾸기보다 `on_transform_updated()` 훅을 사용하는 편이 안전하다.

---

## ui/renderer.py

renderer 계열은 화면에 그려지는 시각 요소다. 모두 `Transform`을 상속하고, 생성 시 스스로 scene listener에 등록된다.

### Renderer

기본 이미지 renderer다.

```python
Renderer(scene, pos_x, pos_y, width, height, image_route=None)
```

역할:

- `scene.draw_listeners`에 자동 등록된다.
- 이미지가 있으면 이미지를 그리고, 없으면 기본 사각형을 그린다.
- `set_transform(...)`이 호출되면 `refresh_image()`를 통해 현재 크기에 맞게 이미지를 다시 스케일한다.

외부 접근용 함수:

- `set_base_image(base_image)`: 이미지 경로 문자열 또는 `pygame.Surface`를 원본 이미지로 설정한다. `None`이면 이미지를 비운다.
- `get_base_image()`: 원본 이미지를 반환한다.
- `refresh_image()`: 원본 이미지를 현재 transform 크기에 맞게 스케일한다.
- `draw(screen)`: 현재 이미지를 `screen`에 그린다.
- `destroy()`: scene listener에서 제거한다.

상속할 때:

- 프레임마다 실행할 로직은 `renderer_update(...)`에 작성한다.
- `update(...)`는 공통 흐름이므로 보통 직접 바꾸지 않는다.
- transform 변경 후 이미지 갱신 방식만 바꿀 때는 `refresh_image()`를 오버라이드한다.

### AnimatedRenderer

이미지 리스트를 순서대로 재생하는 renderer다.

```python
AnimatedRenderer(
    scene,
    pos_x,
    pos_y,
    width,
    height,
    image_route,
    frame_lengths=None,
    background=True,
    loop=True,
)
```

역할:

- `Renderer`를 상속한다.
- `image_route`는 이미지 경로 문자열 또는 `pygame.Surface`의 list다.
- 원본 이미지 list와 스케일된 이미지 list를 따로 관리한다.
- `frame_lengths`는 각 이미지가 몇 프레임 길이로 유지될지 정하는 int list다.
- `loop=False`면 마지막 이미지가 자기 frame length만큼 표시된 뒤 `status`가 `False`가 된다.

등록 방식:

- 항상 `draw_listeners`에는 등록된다.
- `background=True`면 `background_listeners`에 등록된다.
- `background=False`면 `update_listeners`에 등록된다.

외부 접근용 함수:

- `get_base_images()`: 원본 이미지 list를 반환한다.
- `get_images()`: 스케일된 이미지 list를 반환한다.
- `get_frame_lengths()`: frame length list를 반환한다.
- `set_base_images(base_images)`: 이미지 list를 다시 설정하고 현재 크기로 스케일한다.
- `set_frame_lengths(frame_lengths=None)`: frame length list를 설정한다. 부족하면 `1`로 채우고, 길면 잘라낸다.
- `animation_proceed(delta_time)`: 누적 시간에 따라 프레임을 진행한다.
- `destroy()`: 상속받은 `Renderer.destroy()`로 listener에서 제거된다.

상속할 때:

- 프레임마다 추가 로직이 필요하면 `animated_renderer_update(...)`를 오버라이드한다.
- 재생 진행 전체를 바꿔야 할 때만 `animation_proceed(...)`를 바꾼다.
- transform 변경 시 이미지 list 재스케일은 `refresh_image()`에서 처리된다.

### ShiftRenderer

여러 애니메이션 상태와 상태 전환을 관리하는 renderer다.

```python
ShiftRenderer(scene, pos_x, pos_y, width, height, background=True)
```

역할:

- `Renderer`를 상속한다.
- 여러 animation을 key로 등록한다.
- 현재 animation, 마지막 loop animation, shift 후 이동할 animation을 관리한다.
- 상태 머신 성격이 강하므로 `AnimatedRenderer`를 직접 상속하지 않고 별도 구조를 유지한다.

주요 속성:

- `animations`: animation dict 저장소다.
- `shifts`: shift 규칙 저장소다.
- `current`: 현재 animation key다.
- `formal`: 마지막으로 들른 `loop=True` animation key다.
- `next_animation`: shift animation 종료 뒤 우선 이동할 animation key다.
- `status`: 현재 non-loop animation 진행 상태다.

외부 접근용 함수:

- `add_animation(key, images, frame_lengths=None, loop=True, next_animation=None)`: animation을 등록한다.
- `add_shift(key, start, end)`: `start` 상태에서 `key` animation을 재생한 뒤 `end`로 이동하는 shift를 등록한다.
- `set_start(key)`: 시작 animation을 지정한다.
- `shift(key)`: 현재 상태가 shift의 `start`와 맞으면 shift animation을 실행한다.
- `set_animation(key, update_formal=True)`: 현재 animation을 직접 변경한다.
- `refresh_image()`: 등록된 모든 animation 이미지를 현재 transform 크기에 맞게 다시 스케일한다.
- `animation_proceed(delta_time)`: 현재 animation을 진행한다.
- `finish_animation()`: non-loop animation 종료 후 이동 대상을 결정한다.
- `return_formal()`: 마지막 loop animation으로 돌아간다.
- `destroy()`: 상속받은 `Renderer.destroy()`로 listener에서 제거된다.

non-loop animation 종료 후 이동 우선순위:

1. `shift(...)`에서 설정된 `self.next_animation`
2. `add_animation(..., next_animation=...)`에 지정된 animation
3. 마지막 `loop=True` animation인 `formal`

상속할 때:

- 프레임마다 추가 로직이 필요하면 `shift_renderer_update(...)`를 오버라이드한다.
- 상태 전환 규칙을 바꾸고 싶으면 `finish_animation()` 또는 `return_formal()`을 검토한다.
- animation 진행 시간 계산을 바꿔야 할 때만 `animation_proceed(...)`를 바꾼다.

주의할 점:

- `ShiftRenderer`는 animation별 원본 이미지 list와 스케일된 이미지 list를 함께 저장한다.
- `set_transform(...)`으로 크기가 바뀌면 `on_transform_updated()`와 `refresh_image()`를 통해 등록된 모든 animation 이미지를 현재 크기에 맞게 다시 스케일한다.

---

## ui/ui.py

`UIElement`는 UI 상호작용 영역과 UI 업데이트 훅을 관리한다. 시각 출력은 연결된 `Renderer`가 담당한다.

생성:

```python
UIElement(
    scene=None,
    renderer=None,
    pos_x=None,
    pos_y=None,
    width=None,
    height=None,
    background=True,
)
```

초기화 규칙:

- `renderer`를 받으면 `renderer.get_transform()`을 기준으로 자신의 transform을 맞춘다.
- `scene`이 없고 `renderer`가 있으면 `renderer.scene`을 사용한다.
- `renderer`를 받지 않으면 전달받은 `scene`, `pos_x`, `pos_y`, `width`, `height`로 기본 `Renderer`를 직접 만든다.
- 직접 만든 renderer는 `owns_renderer=True`로 관리하며, `destroy()` 때 함께 제거한다.

등록 방식:

- 생성 시 `scene.ui_listener`에 자동 등록된다.
- `background=True`면 `background_listeners`에 등록된다.
- `background=False`면 `update_listeners`에 등록된다.
- `Renderer`와 `UIElement`는 각각 자기 listener 등록 책임을 가진다. UIElement가 renderer를 대신 업데이트하거나 그리지 않는다.

외부 접근용 함수:

- `add_sub_ui(ui_element, pos_x, pos_y)`: 부모 UI의 왼쪽 위 기준 offset 위치에 child UI의 center를 맞춘다.
- `update_sub_ui()`: 부모 transform 기준으로 child UI 위치를 다시 계산한다.
- `pos_check(mouse_pos)`: `self.rect.collidepoint(mouse_pos)`를 반환한다.
- `destroy()`: 자신을 listener에서 제거하고, 소유 renderer와 sub UI를 제거한다.

상속할 때:

- 프레임마다 UI 로직이 필요하면 `ui_element_update(...)`를 오버라이드한다.
- 클릭 반응은 `on_left_click()`, `on_right_click()`, `on_wheel_click()`을 오버라이드한다.
- focus 반응은 `on_enter()`, `on_hover(...)`, `on_exit()`을 오버라이드한다.
- transform 변경 후 renderer와 sub UI 위치 갱신은 `on_transform_updated()`가 담당하므로, 이 메서드를 바꿀 때는 기존 동기화 흐름을 유지해야 한다.

sub UI 주의사항:

- scene은 `ui_listener`를 뒤에서부터 검사하므로 나중에 생성된 UI가 먼저 focus를 잡는다.
- 부모 UI를 먼저 만들고, 자식 UI를 나중에 만든 뒤 `add_sub_ui(...)`로 연결하는 순서를 지키는 것이 안전하다.
- 부모가 움직이면 `on_transform_updated()`를 통해 sub UI 위치도 함께 갱신된다.

삭제 주의사항:

- UI를 화면에서 제거할 때는 반드시 `destroy()`를 호출한다.
- 직접 listener list에서 제거하면 소유 renderer나 sub UI가 남을 수 있다.

---

## 상속 훅 요약

새 기능을 만들 때는 기존 공통 흐름을 유지하고, 아래 훅만 바꾸는 것을 기본으로 한다.

```text
Scene
├─ scene_initialize()
├─ scene_background_update(...)
├─ scene_update(...)
└─ scene_draw()

Renderer
├─ renderer_update(...)
└─ refresh_image()

AnimatedRenderer
├─ animated_renderer_update(...)
└─ animation_proceed(...)

ShiftRenderer
├─ shift_renderer_update(...)
├─ finish_animation()
└─ return_formal()

UIElement
├─ ui_element_update(...)
├─ on_left_click()
├─ on_right_click()
├─ on_wheel_click()
├─ on_enter()
├─ on_hover(...)
└─ on_exit()
```

필수로 상속해야 하는 것은 상황별로 다르다.

- 새 화면을 만들면 `Scene`을 상속하고 보통 `scene_initialize()`, `scene_update()`, `scene_draw()` 중 필요한 것만 구현한다.
- 정적 이미지를 화면에 두면 `Renderer`를 직접 쓰거나 상속한다.
- 단일 애니메이션이면 `AnimatedRenderer`를 사용하거나 상속한다.
- 상태 전환이 있는 애니메이션이면 `ShiftRenderer`를 사용하거나 상속한다.
- 클릭, hover, focus 처리가 필요하면 `UIElement`를 사용하거나 상속한다.

---

## Listener와 destroy 규칙

현재 구조에서는 객체가 자신을 scene listener에 직접 등록한다.

- `Renderer`: `draw_listeners`
- `AnimatedRenderer`: `draw_listeners`와 `background_listeners` 또는 `update_listeners`
- `ShiftRenderer`: `draw_listeners`와 `background_listeners` 또는 `update_listeners`
- `UIElement`: `ui_listener`와 `background_listeners` 또는 `update_listeners`

삭제할 때는 `destroy()`를 호출한다.

```python
renderer.destroy()
ui_element.destroy()
```

`destroy()`는 내부에서 `scene.detach_listeners(self)`를 호출한다. `UIElement`는 자신이 만든 renderer와 sub UI도 함께 제거한다.

주의할 점:

- `destroy()` 없이 객체 참조만 지우면 scene listener에 남아 계속 update 또는 draw될 수 있다.
- 외부에서 받은 renderer를 사용하는 UIElement는 그 renderer를 소유하지 않는다. 이 경우 renderer 삭제 책임은 renderer를 만든 쪽에 있다.
- listener 순서는 UI focus와 draw/update 순서에 영향을 준다. 생성 순서가 곧 처리 순서에 영향을 준다고 보고 관리한다.

---

## 렌더링 구조

게임은 먼저 `virtual_screen`에 그린 뒤 실제 `screen`에 스케일해서 출력한다.

```text
Game.draw()
├─ virtual_screen.fill(BACKGROUND_COLOR)
├─ scene.draw()
└─ present()
   ├─ virtual_screen을 display_size로 smoothscale
   ├─ screen을 LETTERBOX_COLOR로 fill
   ├─ display_offset 위치에 blit
   └─ pygame.display.flip()
```

일반 scene이나 renderer는 가능하면 `game.virtual_screen`에 그린다. 실제 `screen`에 직접 그리면 letterbox, scale, 좌표 변환 흐름과 어긋날 수 있다.

---

## 입력 구조

입력은 `Game.read_inputs()`에서 수집되어 scene으로 전달된다.

```python
delta_time, game_events, mouse_position, wheel_move
```

- `delta_time`: 직전 프레임 이후 경과 시간이다.
- `game_events`: 입력별 `status`, `keydown`, `keyup` dict다.
- `mouse_position`: 가상 화면 기준 마우스 좌표다. letterbox 영역이면 `None`이다.
- `wheel_move`: 현재 프레임의 휠 이동량이다.

`game_events` 구조:

```python
{
    key: {
        "status": bool,
        "keydown": bool,
        "keyup": bool,
    }
}
```

scene과 UI는 이 값을 전달받아 사용한다. scene 내부에서 Pygame 이벤트 큐를 다시 읽지 않는다.
