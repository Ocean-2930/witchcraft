"""캐릭터 선택 화면의 표시 순서와 이름을 읽는다."""

import json
from pathlib import Path


DEFINITIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "definitions" / "characters.json"


def load_character_definitions():
    data = json.loads(DEFINITIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("캐릭터 정의는 비어 있지 않은 객체여야 합니다.")
    for key, row in data.items():
        if not isinstance(row, dict) or row.get("code") != key:
            raise ValueError(f"캐릭터 코드가 일치하지 않습니다: {key}")
        if not isinstance(row.get("name"), str) or not row["name"].strip():
            raise ValueError(f"캐릭터 이름이 필요합니다: {key}")
    return tuple(data.values())
