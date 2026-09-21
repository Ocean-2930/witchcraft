"""UTF-8 아이템 정의를 한 번 읽고 검증한다. 변경 사항은 재시작 시 반영한다."""

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path


DEFINITIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "definitions" / "items.json"


@dataclass(frozen=True)
class ItemDefinition:
    name: str
    description: str
    flavor_text: str
    max_stack: int
    mp_recovery: int | None = None
    equip_type: str | None = None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"중복된 아이템 정의 키: {key}")
        result[key] = value
    return result


def load_definitions(path: Path) -> dict[str, ItemDefinition]:
    """잘못된 정의는 기본값으로 대체하지 않고 파일·아이템 코드와 함께 거부한다."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        if not isinstance(data, dict) or not data:
            raise ValueError("최상위 값은 비어 있지 않은 객체여야 합니다.")
        definitions = {}
        for code, row in data.items():
            try:
                if not code.strip() or not isinstance(row, dict):
                    raise ValueError("아이템 코드와 정의 객체가 필요합니다.")
                definition = ItemDefinition(**row)
                for field in ("name", "description", "flavor_text"):
                    if not isinstance(getattr(definition, field), str):
                        raise ValueError(f"{field}는 문자열이어야 합니다.")
                if not definition.name.strip():
                    raise ValueError("name은 비어 있을 수 없습니다.")
                if type(definition.max_stack) is not int or definition.max_stack < 1:
                    raise ValueError("max_stack은 1 이상의 정수여야 합니다.")
                recovery = definition.mp_recovery
                if recovery is not None and (type(recovery) is not int or recovery < 0):
                    raise ValueError("mp_recovery는 0 이상의 정수여야 합니다.")
                if definition.equip_type is not None:
                    if definition.equip_type not in ("weapon", "sub_weapon", "armor", "accessory"):
                        raise ValueError("지원하지 않는 equip_type입니다.")
                    if definition.max_stack != 1:
                        raise ValueError("장비의 max_stack은 1이어야 합니다.")
                # 설명과 실제 회복량이 서로 달라지지 않도록 같은 값을 사용한다.
                if "{mp_recovery}" in definition.description and recovery is None:
                    raise ValueError("설명에 사용할 mp_recovery가 필요합니다.")
                definitions[code] = definition
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{code}: {exc}") from exc
        return definitions
    except (OSError, ValueError) as exc:
        raise ValueError(f"아이템 정의 파일 오류 ({path}): {exc}") from exc


@lru_cache(maxsize=None)
def get_item_definition(code: str) -> ItemDefinition:
    try:
        return _definitions()[code]
    except KeyError as exc:
        raise ValueError(f"아이템 정의가 없습니다 ({DEFINITIONS_PATH}): {code}") from exc


@lru_cache(maxsize=1)
def _definitions() -> dict[str, ItemDefinition]:
    return load_definitions(DEFINITIONS_PATH)
