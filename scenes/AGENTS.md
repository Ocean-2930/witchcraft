# Scene Instructions

`scenes/`는 화면 단위 로직, overlay scene, scene 전환, listener 흐름을 담당한다.

## Scene Lifecycle

- 새 화면은 `Scene`을 상속하고 보통 별도 `scene_name.py` 파일로 만든다.
- 초기 객체 생성과 상태값 설정은 `scene_initialize()`에 둔다.
- overlay 여부와 상관없이 돌아야 하는 로직은 `scene_background_update(...)`에 둔다.
- overlay가 없을 때만 돌아야 하는 로직은 `scene_update(...)`에 둔다.
- 직접 그릴 것이 있으면 `scene_draw()`를 오버라이드하고, listener도 그려야 하면 원하는 위치에서 `super().scene_draw()`를 호출한다.

## Listeners

- `background_listeners` 객체는 `background_update(...)`를 가져야 한다.
- `update_listeners` 객체는 `update(...)`를 가져야 한다.
- `draw_listeners` 객체는 `draw(screen)`을 가져야 한다.
- `ui_listener` 객체는 `pos_check(...)`, focus hook, click hook을 가져야 한다.
- 객체 제거는 직접 list 조작 대신 각 객체의 `destroy()`를 호출한다.

## UI Focus

- `operate_ui(...)`는 `ui_listener`를 뒤에서부터 검사한다.
- 나중에 생성된 UI가 먼저 focus를 잡는다.
- 클릭 우선순위는 왼클릭, 오른클릭, 휠클릭 순서다.

## UI Separation

- 재사용 가치가 있는 패널, 슬롯, 버튼, 게이지, 제목, 팝업, 툴팁 같은 시각·상호작용 요소는 scene 파일에서 직접 선언하거나 그리지 않고 `ui/`에서 관리한다.
- scene 전용 UI는 `ui/{scene_name}/` 아래에 `Renderer` 또는 `UIElement` 구현체로 분리한다.
- 여러 scene에서 재사용할 UI는 새로 만들기 전에 `ui/global/`을 확인하고, 공용 구현체는 `ui/global/`에 둔다.
- scene은 분리된 UI를 생성하고 상태, 데이터, callback을 전달하며 게임 로직과 UI 흐름만 조정한다.
- `scene_draw()`의 직접 출력은 화면 배경, 월드 자체의 렌더링, 일회성 개발·디버그 표시처럼 UI 클래스로 분리할 실익이 없는 경우로 제한한다.

## Exports

- `scenes/__init__.py`에는 실제 외부에서 바로 사용할 scene만 공개한다.
- 개발용 HUD처럼 `DebugGame`에서만 직접 쓰는 요소는 export하지 않는다.
