"""적이 소유하는 불변 (코드, 가중치) 드롭 표."""

from math import isfinite


def validate_drop_table(value):
    if not isinstance(value, (list, tuple)):
        raise ValueError("드롭 표는 (코드, 가중치) 목록이어야 합니다.")
    result = []
    for entry in value:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError("드롭 항목에는 코드와 가중치가 필요합니다.")
        code, weight = entry
        if not ((type(code) is str and code.strip()) or (type(code) is int and code in (0, 1))):
            raise ValueError("드롭 코드는 아이템 코드, 0(없음), 1(랜덤)이어야 합니다.")
        if type(weight) not in (int, float) or not isfinite(weight) or weight < 0:
            raise ValueError("드롭 가중치는 유한한 0 이상의 숫자여야 합니다.")
        result.append((code, weight))
    if not isfinite(sum(weight for _, weight in result)):
        raise ValueError("드롭 가중치 합이 유한해야 합니다.")
    return tuple(result)
