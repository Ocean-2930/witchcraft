# 클래스 상속 구조

이 문서는 다른 클래스가 상속하여 사용하는 부모 클래스들의 관계만 기록한다. 개별 화면 UI, 몬스터, 아이템처럼 구체적인 최종 구현 클래스는 나열하지 않는다.

## 실행 환경과 화면

```text
Game
└─ DebugGame

Scene
└─ 화면별 Scene 구현체
```

- `Game`은 일반 실행 루프를 제공하고 `DebugGame`은 scene 업데이트와 렌더링에 개발 HUD를 추가한다.
- `Scene`은 lifecycle, overlay, listener, UI focus 및 화면 전환의 공통 기반이다.

## UI

```text
Transform
├─ Renderer
│  ├─ AnimatedRenderer
│  └─ ShiftRenderer
└─ UIElement
   └─ InventorySlot
```

- `Transform`은 중심점 기반 위치와 크기를 관리한다.
- `Renderer` 계층은 시각 출력과 scene listener 등록을 담당한다.
- `UIElement` 계층은 상호작용 영역, focus hook, 연결된 renderer의 생명주기를 담당한다.
- `InventorySlot`은 인벤토리 슬롯 UI들이 공유하는 상호작용 기반이다.

## 게임 모델

```text
UnitBase
└─ Unit

Item
└─ Equip

SkillBase
└─ 능동 스킬 정의

SkillEffect
├─ 능동 효과 기반 구현
└─ PassiveEffect
   └─ StatIncreaseEffect
```

- `UnitBase`는 기초 능력치를, `Unit`은 체력·마나·버프와 전투 계산을 제공한다.
- `Item`은 공통 아이템 데이터를, `Equip`은 장비 공통 계약을 제공한다.
- `SkillBase`는 비용, 범위 및 효과 조합을 관리한다.
- `SkillEffect`는 판정, 미리보기 및 적용을 위한 효과 계약을 제공한다.
- `PassiveEffect`는 능력치 계산 흐름에서 적용되는 수동 효과 기반이고, `StatIncreaseEffect`는 지정한 단일 능력치를 레벨과 중첩에 비례해 증가시킨다.
