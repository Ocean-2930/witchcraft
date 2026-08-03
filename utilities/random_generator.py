from random import Random
from typing import MutableSequence, Sequence, TypeAlias, TypeVar


RandomSeed: TypeAlias = int | float | str | bytes | bytearray
T = TypeVar("T")


class RandomGenerator:
    """현재 난수를 다음 발급 상태로 보관하는 결정적 난수 생성기."""

    def __init__(self, seed: RandomSeed | None = None) -> None:
        seed_generator = Random(seed)
        self._current_random = seed_generator.random()

    @property
    def current_random(self) -> float:
        """다음 난수 발급에 사용할 현재 상태를 반환한다."""
        return self._current_random

    def random(self, count: int | None = None) -> float | list[float]:
        """난수를 하나 발급하거나, count가 주어지면 그 수만큼 발급한다."""
        if count is None:
            return self._issue_one()
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count는 정수여야 합니다.")
        if count < 1:
            raise ValueError("count는 1 이상이어야 합니다.")

        return [self._issue_one() for _ in range(count)]

    def randint(self, start: int, end: int) -> int:
        """start와 end를 모두 포함하는 정수 난수를 발급한다."""
        if isinstance(start, bool) or not isinstance(start, int):
            raise TypeError("start는 정수여야 합니다.")
        if isinstance(end, bool) or not isinstance(end, int):
            raise TypeError("end는 정수여야 합니다.")
        if start > end:
            raise ValueError("start는 end보다 클 수 없습니다.")

        return start + int(self._issue_one() * (end - start + 1))

    def choice(self, values: Sequence[T]) -> T:
        """비어 있지 않은 시퀀스에서 값 하나를 발급한다."""
        if not values:
            raise IndexError("비어 있는 시퀀스에서는 값을 선택할 수 없습니다.")

        return values[self.randint(0, len(values) - 1)]

    def shuffle(self, values: MutableSequence[T]) -> None:
        """시퀀스를 현재 난수 흐름으로 제자리에서 섞는다."""
        for index in range(len(values) - 1, 0, -1):
            target = self.randint(0, index)
            values[index], values[target] = values[target], values[index]

    def _issue_one(self) -> float:
        generator = Random(self._current_random)
        issued_random = generator.random()
        self._current_random = generator.random()
        return issued_random
