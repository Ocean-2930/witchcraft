# Data Instructions

`data/`는 저장 데이터, 사용자 데이터, 런타임 데이터 파일을 둔다.

## Rules

- JSON 파일은 UTF-8로 저장한다.
- 빈 JSON 파일은 만들지 않는다. placeholder가 필요하면 `{}` 또는 `[]`처럼 유효한 JSON을 사용한다.
- 데이터 스키마를 바꿀 때는 읽는 코드와 쓰는 코드를 함께 확인한다.
