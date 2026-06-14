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

## Verification

- 기본 확인은 `.venv\Scripts\python.exe -m compileall core scenes ui settings.py main.py develop.py`를 사용한다.
- 데이터 파일을 수정했다면 UTF-8로 읽히는지와 JSON 문법이 유효한지 확인한다.
