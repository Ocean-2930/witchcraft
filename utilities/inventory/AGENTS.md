# Inventory Instructions

`utilities/inventory/`는 보유 아이템, 장비 슬롯, hotbar 아이템 연결을 담당한다.

## Model

- `ItemInventory`는 아이템 인스턴스의 보관과 수량 제거를 담당한다.
- 아이템 소유 여부와 제거는 내용 동등성(`==`)이 아니라 실제 `ItemInstance` 객체 identity로 판정한다.
- `DungeonInventory`는 한 번의 던전 진행에서 사용하는 아이템, 장비 슬롯, hotbar 연결을 단일 소유한다.
- `DungeonInventory.learnable_skills`는 티어, 스킬 인스턴스와 개별 투자 상한을 묶은 `LearnableSkill` 목록을 관리한다.
- 장착과 해제처럼 여러 컬렉션을 함께 바꾸는 연산은 scene에서 직접 수정하지 않고 `DungeonInventory` 메서드로 처리한다.

## Dependencies

- 아이템 정의는 `items`, 스킬 정의는 `skills`, 유닛 기본 능력치는 `units.unit_base`에서 가져온다.
- scene과 UI를 import하거나 listener 및 입력 상태를 직접 참조하지 않는다.

## Exports

- 외부에서 인벤토리를 구성하고 조작하는 데 필요한 모델만 `utilities/inventory/__init__.py`에 공개한다.
