# UI Instructions

`ui/`는 `Transform`, `Renderer`, `AnimatedRenderer`, `ShiftRenderer`, `UIElement`를 관리한다.

## Transform

- 위치 기준은 center 좌표다.
- transform 변경 반응은 `set_transform()`을 바꾸기보다 `on_transform_updated()` 훅을 사용한다.

## Renderer

- renderer 계열은 `Transform`을 상속하고 생성 시 스스로 scene listener에 등록된다.
- 모든 renderer는 `draw_listeners`에 등록된다.
- `AnimatedRenderer`와 `ShiftRenderer`는 `background=True`면 `background_listeners`, 아니면 `update_listeners`에 추가 등록된다.
- 이미지 경로 또는 `pygame.Surface`를 받을 수 있다.
- 크기가 바뀌면 원본 이미지를 현재 transform 크기에 맞춰 다시 스케일한다.

## UIElement

- `UIElement`는 상호작용 영역을 담당하고 시각 출력은 연결된 `Renderer`가 담당한다.
- renderer를 받지 않으면 반드시 scene, pos, size를 받아 기본 `Renderer`를 직접 만든다.
- renderer를 받으면 renderer의 transform과 scene을 기준으로 초기화한다.
- `background=True`면 `background_listeners`, 아니면 `update_listeners`에 등록된다.
- UI 제거는 반드시 `destroy()`를 호출한다.
- 자신이 만든 renderer는 `destroy()` 때 함께 제거한다. 외부에서 받은 renderer는 만든 쪽이 제거 책임을 가진다.

## Sub UI

- 부모 UI를 먼저 만들고 자식 UI를 나중에 만든 뒤 `add_sub_ui(...)`로 연결한다.
- scene은 `ui_listener`를 뒤에서부터 검사하므로 생성 순서가 focus 순서에 영향을 준다.

## Reuse

- 새 UI를 만들기 전에 `ui/global/`뿐 아니라 다른 `ui/{scene_name}/` 폴더에 유사한 구현이 있는지 확인한다.
- 다른 scene에서 사용하던 UI가 현재 scene에서도 재사용 가능하다고 판단되면 같은 구현을 새로 만들지 않는다.
- 이 경우 기존 UI를 원래 scene 폴더에 둔 채 다른 scene에서 가져오지 말고 `ui/global/`로 이동한다.
- 기존 scene과 새 scene은 모두 `ui/global/`로 이동한 하나의 공용 구현을 import해서 사용하도록 수정한다.
- 공용화할 때 특정 scene에 종속된 이름, 상태 접근, callback을 제거하고 필요한 데이터와 동작은 생성자 인자로 받도록 정리한다.

## Exports

- `Renderer`, `AnimatedRenderer`, `ShiftRenderer`, `UIElement`처럼 상속해서 쓰는 클래스는 루트 `AGENTS.md`의 scene별 구현체 관리 규칙을 따른다.
- 새 UI/renderer 클래스는 `ui/scene_name/ui_name.py`에 선언한다.
- 실제 scene에서 import할 요소는 `ui/__init__.py`에 등록한다.
- `ui/__init__.py`에서는 `# scene_name` 주석 아래에 해당 scene의 import를 모아둔다.
- `Renderer`는 직접 사용 빈도가 높으므로 package export 대상이다.
