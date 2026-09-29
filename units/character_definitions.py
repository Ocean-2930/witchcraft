"""캐릭터 선택 화면의 표시 순서와 이름을 읽는다."""

import json
from math import isfinite
from pathlib import Path


DEFINITIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "definitions" / "characters.json"

# 공통 단발 모션 키와 표시 이름. 시트 파일명은 {motion}.png를 사용한다.
COMMON_CHARACTER_MOTIONS = {
    "attack": "공격",
    "buff": "버프",
    "magic": "마법",
    "skill": "기술",
    "hit": "피격",
    "death": "사망",
    "dodge": "회피",
    "guard": "방어",
}


def load_character_definitions():
    data = json.loads(DEFINITIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("캐릭터 정의는 비어 있지 않은 객체여야 합니다.")
    for key, row in data.items():
        if not isinstance(row, dict) or row.get("code") != key:
            raise ValueError(f"캐릭터 코드가 일치하지 않습니다: {key}")
        if not isinstance(row.get("name"), str) or not row["name"].strip():
            raise ValueError(f"캐릭터 이름이 필요합니다: {key}")
        motions = row.get("motions", {})
        if not isinstance(motions, dict):
            raise ValueError(f"motions는 객체여야 합니다: {key}")
        for motion, config in motions.items():
            if not isinstance(motion, str) or not motion.isidentifier() or not isinstance(config, dict):
                raise ValueError(f"모션 설정이 올바르지 않습니다: {key}")
            if set(config) - {"scale", "anchor", "offset", "frame_offsets"}:
                raise ValueError(f"알 수 없는 모션 설정: {key}/{motion}")
            scale = config.get("scale", 1.0)
            if type(scale) not in (int, float) or not isfinite(scale) or scale <= 0:
                raise ValueError(f"모션 scale은 유한한 양수여야 합니다: {key}/{motion}")
            for field in ("anchor", "offset"):
                if field in config:
                    validate_motion_vector(config[field])
            offsets = config.get("frame_offsets", [])
            if not isinstance(offsets, list) or len(offsets) not in (0, 8):
                raise ValueError("frame_offsets는 비어 있거나 8개여야 합니다.")
            for offset in offsets:
                validate_motion_vector(offset)
    return tuple(data.values())


def validate_motion_vector(value):
    if (not isinstance(value, list) or len(value) != 2
            or any(type(v) not in (int, float) or not isfinite(v) for v in value)):
        raise ValueError("모션 좌표는 유한한 숫자 두 개의 배열이어야 합니다.")


def load_character_motion_settings(code):
    for row in load_character_definitions():
        if row["code"] == code:
            return row.get("motions", {})
    raise ValueError(f"등록되지 않은 캐릭터: {code}")
