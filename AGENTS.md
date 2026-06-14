# Project Instructions

이 저장소는 Pygame 기반 2D 게임 템플릿이다. 파일을 읽고 쓸 때 한국어가 포함될 수 있으므로 UTF-8 인코딩을 우선 사용한다.

## Structure

- `main.py`는 배포/일반 실행 진입점이며 `Game`을 실행한다.
- `develop.py`는 개발 실행 진입점이며 `DebugGame`과 HUD를 실행한다.
- `settings.py`에는 사용자 설정, 입력 상수, 개발 설정을 둔다.
- `core/`는 Pygame 초기화, 메인 루프, 입력 수집, 화면 출력, 사운드 같은 실행 환경을 담당한다.
- `scenes/`는 화면 단위 로직, overlay, scene 전환을 담당한다.
- `ui/`는 transform, renderer, UI 상호작용 기반 클래스를 담당한다.
- `assets/`는 이미지, 폰트, 사운드 리소스를 둔다.
- `data/`는 저장 데이터와 런타임 데이터를 둔다.
- `utilities/`는 여러 모듈에서 재사용하는 보조 함수를 둔다.

## General Rules

- Pygame 이벤트 큐는 `Game.read_inputs()`에서만 읽는다. scene이나 UI 내부에서 `pygame.event.get()`을 다시 호출하지 않는다.
- 게임 로직과 렌더링 좌표는 기본적으로 `virtual_screen` 기준 좌표를 사용한다.
- 실제 화면 크기는 사용자가 창 테두리로 조절하는 방식이 아니라 내부 코드에서 제공한 해상도 값으로만 변경한다.
- `pygame.RESIZABLE`을 사용하지 않는다.
- 런타임에 바뀔 수 있는 설정은 값 직접 import보다 `import settings` 후 `settings.X` 또는 helper 함수로 읽는다.
- 객체를 화면에서 제거할 때 listener list를 직접 수정하지 말고 해당 객체의 `destroy()`를 호출한다.
- package `__init__.py`에는 실제 외부 사용 요소만 공개한다. 상속용 base class는 필요한 파일에서 직접 경로로 import하는 것을 기본으로 한다.

## Scene-Based Implementations

- `Renderer`, `UIElement`처럼 기반 클래스를 상속해서 scene별 구현체를 만들 때는 부모 클래스가 있는 관리 root folder 아래에 scene별 하위 폴더를 만든다.
- 새 element 구현체를 만들기 전에 해당 root folder의 `global` 폴더를 확인해서 이미 재사용 가능한 요소가 있는지 먼저 살핀다.
- 파일 경로는 `{root_folder}/{scene_name}/{element_name}.py` 형태를 사용한다. 예: `ui/title_scene/start_button.py`.
- 여러 scene에서 함께 쓸 가능성이 큰 공용 구현체는 scene name 폴더가 아니라 `{root_folder}/global/{element_name}.py`에서 관리한다.
- 해당 root folder의 `__init__.py`에는 `# scene_name` 주석을 만들고, 그 아래에 해당 scene의 구현체 import를 모아둔다.
- global 구현체 import는 `__init__.py`의 `# global` 주석 아래에 모아둔다.
- 나중에 `ui/` 외의 다른 관리 폴더가 생겨도 같은 방식으로 scene별 구현체를 배치한다.

## Verification

- 기본 확인은 `.venv\Scripts\python.exe -m compileall core scenes ui settings.py main.py develop.py`를 사용한다.
- 데이터 파일을 수정했다면 UTF-8로 읽히는지와 JSON 문법이 유효한지 확인한다.
