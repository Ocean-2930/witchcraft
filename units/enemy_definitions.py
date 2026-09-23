"""적 생성용 기본 능력치. 실행 중 상태 및 AI 동작은 Enemy가 소유한다."""

from dataclasses import fields
from functools import lru_cache
import json
from math import isfinite
from pathlib import Path
from types import MappingProxyType

from .unit_base import UnitBase
from .variable import MIN_MAX_HP, MIN_MAX_MP, MIN_SPEED_STEP, MAX_SPEED_STEP


DEFINITIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "definitions" / "enemies.json"
SPAWN_ENEMY_CODES = ("basic_monster", "cave_bat", "goblin")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"중복된 적 정의 키: {key}")
        result[key] = value
    return result


def load_enemy_definitions(path: Path):
    """UnitBase 및 재화 지급량 필드를 허용하며 정의와 내부 능력치 모두 읽기 전용으로 반환한다."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(data, dict) or not data:
            raise ValueError("최상위 값은 비어 있지 않은 객체여야 합니다.")
        definitions = {}
        for code, row in data.items():
            try:
                if not code.strip() or not isinstance(row, dict):
                    raise ValueError("적 코드와 정의 객체가 필요합니다.")
                rewards = {key: row.get(key, 0) for key in ("drop_gold", "drop_harmony_stones")}
                for key, value in rewards.items():
                    if type(value) is not int or value < 0:
                        raise ValueError(f"{key}는 0 이상의 정수여야 합니다.")
                base = UnitBase(**{key: value for key, value in row.items() if key not in rewards})
                if not isinstance(base.name, str) or not base.name.strip():
                    raise ValueError("name은 비어 있지 않은 문자열이어야 합니다.")
                for field in fields(UnitBase):
                    if field.name == "name":
                        continue
                    value = getattr(base, field.name)
                    valid_type = type(value) is int if field.type == "int" else type(value) in (int, float)
                    if not valid_type or not isfinite(value):
                        raise ValueError(f"{field.name}의 숫자 타입 또는 값이 올바르지 않습니다.")
                if base.max_hp < MIN_MAX_HP or base.max_mp < MIN_MAX_MP:
                    raise ValueError("최대 체력·마나가 허용 범위 밖입니다.")
                for speed in (base.attack_speed, base.move_speed):
                    if not MIN_SPEED_STEP <= speed <= MAX_SPEED_STEP:
                        raise ValueError("속도 단계가 허용 범위 밖입니다.")
                definitions[code] = MappingProxyType({**{field.name: getattr(base, field.name) for field in fields(UnitBase)}, **rewards})
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"{code}: {exc}") from exc
        return MappingProxyType(definitions)
    except (OSError, ValueError) as exc:
        raise ValueError(f"적 정의 파일 오류 ({path}): {exc}") from exc


@lru_cache(maxsize=1)
def _definitions():
    return load_enemy_definitions(DEFINITIONS_PATH)


def get_enemy_definition(code: str):
    try:
        return _definitions()[code]
    except KeyError as exc:
        raise ValueError(f"적 정의가 없습니다 ({DEFINITIONS_PATH}): {code}") from exc
