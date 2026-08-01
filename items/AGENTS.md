# Items Instructions

`items/`는 아이템 원형, 장비 계층, 사용 아이템, 런타임 아이템 인스턴스를 담당한다.

## Model

- 공통 아이템 데이터와 스프라이트 조회는 `Item`에 둔다.
- 장비 공통 동작은 `Equip`, 소비·사용 동작은 `UsableItem`을 기준으로 확장한다.
- 보유 수량, 강화처럼 개별 보유 상태는 아이템 원형과 분리하여 `ItemInstance`에서 관리한다.
- 스킬이 포함된 장비는 허용 개수와 병합 조건을 `SkilledEquip` 계층에서 일관되게 처리한다.

## Content Layout

- 실제 소비·사용 아이템 구현은 `items/items/{item_name}.py`에 둔다.
- 실제 장비 구현은 종류에 따라 `items/equips/weapons/`, `items/equips/sub_weapons/`, `items/equips/armors/`, `items/equips/accessories/`에 둔다.
- 실제 스킬 구현은 이 패키지가 아니라 `skills/implementations/` 아래의 종류별 폴더에 둔다.
- 새 실 아이템·장비 구현을 `items/` 루트에 직접 추가하지 않는다. 루트에는 공통 계층과 런타임 인스턴스만 둔다.

## Dependencies

- 순환 import를 피하기 위한 타입 전용 의존성은 `TYPE_CHECKING` 아래에서 import한다.
- 아이템 사용이나 장착으로 unit 또는 skill 상태를 바꿀 때는 관련 `units/`, `skills/` 코드와 호출부를 함께 확인한다.

## Exports

- 외부에서 직접 생성하거나 타입 판별에 사용하는 아이템 클래스만 `items/__init__.py`와 `__all__`에 공개한다.
- 새 아이템을 추가할 때 기존 아이템 계층으로 표현할 수 있는지 먼저 확인하고, 단일 아이템에만 필요한 동작은 공통 부모 클래스에 넣지 않는다.
