from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from units.unit import Unit


@dataclass
class CombatTimerEntry:
    unit: Unit
    remaining: int

    @property
    def is_ready(self):
        return self.remaining == 0


@dataclass
class TurnCounter:
    interval: int = 100
    value: int = 0

    def __post_init__(self):
        if self.interval <= 0:
            raise ValueError("턴 간격은 1 이상이어야 합니다.")
        self.value %= self.interval

    @property
    def ticks_until_next(self):
        return self.interval - self.value

    def advance(self, ticks: int):
        if ticks < 0:
            raise ValueError("턴 카운터의 진행 틱은 0 이상이어야 합니다.")

        total = self.value + ticks
        completed_turns, self.value = divmod(total, self.interval)
        return completed_turns


class CombatTimer:
    """던전 전투 유닛의 다음 행동까지 남은 정수 틱을 관리한다."""

    def __init__(self):
        self.entries: list[CombatTimerEntry] = []
        self.turn_counter = TurnCounter()

    def register(self, unit: Unit, turn_cost: int | None = None):
        entry = self.get_entry(unit)
        cost = unit.move_turn_cost if turn_cost is None else turn_cost
        self._validate_turn_cost(cost)

        if entry is None:
            entry = CombatTimerEntry(unit, cost)
            self.entries.append(entry)
        else:
            entry.remaining = cost

        return entry

    def unregister(self, unit: Unit):
        entry = self.get_entry(unit)
        if entry is None:
            return False

        self.entries.remove(entry)
        return True

    def schedule(self, unit: Unit, turn_cost: int):
        """행동을 마친 유닛을 선택한 행동의 비용으로 다시 예약한다."""
        self._validate_turn_cost(turn_cost)
        entry = self.get_entry(unit)
        if entry is None:
            raise ValueError("등록되지 않은 유닛은 예약할 수 없습니다.")

        entry.remaining = turn_cost

    def advance(self, ticks: int = 1):
        """모든 타이머를 줄이고 행동을 결정할 준비가 된 유닛을 반환한다."""
        if ticks < 0:
            raise ValueError("전투 타이머의 진행 틱은 0 이상이어야 합니다.")

        self.turn_counter.advance(ticks)
        for entry in self.entries:
            entry.remaining = max(0, entry.remaining - ticks)

        return self.ready_units

    def advance_to_next(self):
        """가장 가까운 행동 시점까지 진행하고 동시에 준비된 유닛을 반환한다."""
        if self.ready_units:
            return self.ready_units

        pending = [entry.remaining for entry in self.entries if entry.remaining > 0]
        if pending:
            self.advance(min(pending))
        return self.ready_units

    @property
    def ready_units(self):
        return [entry.unit for entry in self.entries if entry.is_ready]

    def get_entry(self, unit: Unit):
        return next((entry for entry in self.entries if entry.unit is unit), None)

    @staticmethod
    def _validate_turn_cost(turn_cost):
        if not isinstance(turn_cost, int) or isinstance(turn_cost, bool) or turn_cost <= 0:
            raise ValueError("행동 비용은 1 이상의 정수여야 합니다.")
