# Core Instructions

`core/`는 Pygame 초기화, 메인 루프, 입력 수집, 화면 크기 계산, 사운드 제어를 담당한다.

## Game Loop

- 일반적으로 `Game.run()`은 변경하지 않는다.
- 씬 업데이트 순서를 바꿀 때는 `update_scene(...)`을 오버라이드한다.
- 렌더링 순서를 바꿀 때는 `draw()`를 오버라이드한다.
- 종료는 `quit()`을 호출해서 `running = False`로 처리한다.

## Input

- 입력은 `Game.read_inputs()`에서 한 번만 수집한다.
- scene, UI, renderer 내부에서 `pygame.event.get()`을 다시 호출하지 않는다.
- `mouse_position`은 `window_to_virtual(...)`을 거친 가상 화면 좌표이며 letterbox 영역이면 `None`이다.

## Display

- `virtual_screen`은 고정 가상 해상도 surface다.
- 실제 `screen`에는 `present()`에서 `virtual_screen`을 `display_size`로 스케일해서 그린다.
- 화면 크기 변경은 `set_screen_size(width, height)`를 통해 처리한다.
- `pygame.RESIZABLE`과 `VIDEORESIZE` 기반 사용자 드래그 리사이즈는 제공하지 않는다.

## Sound

- 배경음악 볼륨은 `settings.BGM`을 런타임에 읽어 적용한다.
- 효과음 볼륨은 `settings.SFX * weight`로 계산한다.
