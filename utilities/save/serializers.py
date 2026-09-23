"""실행 코드나 UI 참조를 포함하지 않는 버전 2 저장 형식 (버전 1 읽기 호환)."""

from dataclasses import asdict, fields
from math import isfinite

from items import BluePotion, SimpleSword, ItemInstance, EquipmentInstance
from items.equip import Equip
from skills import AttackSkill, STAT_PASSIVE_SKILLS, SkillInstance
from units import Player, Enemy, EnemyMode
from units.unit import Unit
from utilities.dungeon.map_generator import DungeonMap, Room, MapConnection, EventTile
from utilities.dungeon.combat_timer import CombatTimerEntry
from utilities.inventory import DungeonInventory, ItemInventory, LearnableSkill
from utilities.random_generator import RandomGenerator
from .session import GameSession


# 새 콘텐츠는 클래스 경로 대신 안정적인 코드와 생성 함수를 등록한다.
ITEM_FACTORIES = {cls().item_code: cls for cls in (BluePotion, SimpleSword)}
SKILL_DEFINITIONS = {skill.skill_code: skill for skill in (AttackSkill(), *STAT_PASSIVE_SKILLS)}
RNG_NAMES = ("map", "enemy", "item", "battle")


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("정수 값의 범위가 올바르지 않습니다.")
    return value


def plain(value):
    """버프·이벤트 상태는 JSON 값만 허용하고 임의 객체를 조용히 버리지 않는다."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float and isfinite(value):
        return value
    if type(value) is list:
        return [plain(v) for v in value]
    if type(value) is dict and all(type(k) is str for k in value):
        return {k: plain(v) for k, v in value.items()}
    raise ValueError("버프·이벤트 상태에는 JSON으로 표현 가능한 값만 사용할 수 있습니다.")


def skill_data(instance):
    if instance is None:
        return None
    code = instance.skill.skill_code
    if code not in SKILL_DEFINITIONS:
        raise ValueError(f"저장에 등록되지 않은 스킬: {code}")
    return {"code": code, "level": instance.level, "stack": instance.stack}


def read_skill(data):
    if data is None:
        return None
    if type(data["level"]) is not int:
        raise ValueError("스킬 레벨은 정수여야 합니다.")
    return SkillInstance(SKILL_DEFINITIONS[data["code"]], data["level"], integer(data["stack"], 1))


def unit_data(unit):
    data = {f.name: getattr(unit, f.name) for f in fields(Unit)}
    if isinstance(unit, Enemy):
        data.update(drop_gold=integer(unit.drop_gold), drop_harmony_stones=integer(unit.drop_harmony_stones))
    data["buffs"] = plain(unit.buffs)
    return data


def read_unit(data, enemy=False, legacy=False):
    rewards = {}
    if enemy:
        data = dict(data)
        for key in ("drop_gold", "drop_harmony_stones"):
            # 버전 1의 기존 적은 재화 지급량이 없었으므로 0으로 이관한다.
            rewards[key] = integer(data.pop(key, 0) if legacy else data.pop(key))
    if set(data) != {f.name for f in fields(Unit)} or type(data["name"]) is not str:
        raise ValueError("유닛 데이터가 올바르지 않습니다.")
    for key, value in data.items():
        if key not in ("name", "buffs"):
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError("유닛 능력치가 올바르지 않습니다.")
    integer(data["tile_x"])
    integer(data["tile_y"])
    if data["max_hp"] < 1 or data["max_mp"] < 0 or data["hp"] < 0 or data["mp"] < 0:
        raise ValueError("유닛 체력·마나가 올바르지 않습니다.")
    if type(data["buffs"]) is not list:
        raise ValueError("버프 목록이 올바르지 않습니다.")
    plain(data["buffs"])
    unit = Enemy(name=data["name"], max_hp=data["max_hp"], attack_power=data["attack_power"]) if enemy else Player(data["name"])
    # 생성자의 보정 때문에 현재 HP/MP 등이 바뀌지 않도록 검증 후 그대로 복원한다.
    for key, value in {**data, **rewards}.items():
        setattr(unit, key, value)
    return unit


def to_data(session):
    inventory = session.inventory
    items = {}
    identities = {}

    def item_ref(item):
        if item is None:
            return None
        identity = id(item)
        if identity not in identities:
            key = f"item_{len(identities) + 1}"
            identities[identity] = key
            code = item.item.item_code
            if code not in ITEM_FACTORIES:
                raise ValueError(f"저장에 등록되지 않은 아이템: {code}")
            items[key] = {"code": code, "stack": item.stack,
                          "rows": [skill_data(row) for row in item.stat_rows] if isinstance(item, EquipmentInstance) else None}
        return identities[identity]

    inv = {
        "game_seed": inventory.game_seed,
        "floor_randoms": inventory.floor_randoms,
        "random_states": {name: [r.current_random for r in getattr(inventory, f"{name}_random_generators")] for name in RNG_NAMES},
        "player": unit_data(inventory.player),
        "capacity": inventory.item_inventory.capacity,
        "items": [item_ref(item) for item in inventory.item_inventory.items],
        "equipment": {slot: item_ref(getattr(inventory, slot)) for slot in inventory.EQUIPMENT_SLOTS},
        "hotbar_items": {label: item_ref(item) for label, item in inventory.hotbar_items.items()
                         if any(owned is item for owned in inventory.item_inventory.items)},
        "hotbar_skills": inventory.hotbar_skill_codes.copy(),
        "gold": inventory.gold, "harmony_stones": inventory.harmony_stones,
        "learnable_skills": [{"tier": entry.tier, "skill": skill_data(entry.skill), "max_level": entry.max_level} for entry in inventory.learnable_skills],
        "tier_points": {str(tier): points for tier, points in inventory.tier_skill_points.items()},
        "explored": {str(floor): sorted(positions) for floor, positions in inventory.explored_tiles_by_floor.items()},
    }
    floors = {}
    for floor, dungeon in session.floors.items():
        units = {id(inventory.player): "player"}
        units.update({id(enemy): f"enemy_{index}" for index, enemy in enumerate(dungeon.enemies)})
        floors[str(floor)] = {
            "tiles": dungeon.tiles, "rooms": [asdict(room) for room in dungeon.rooms],
            "connections": [asdict(connection) for connection in dungeon.connections],
            "hub_room_id": dungeon.hub_room_id, "up_stairs": dungeon.up_stairs,
            "down_stairs": dungeon.down_stairs, "seed": dungeon.seed,
            "initialized": dungeon.initialized,
            "events": [asdict(event) for event in dungeon.event_tiles],
            "event_states": plain(dungeon.event_states),
            "ground_items": [{"position": pos, "items": [item_ref(item) for item in pile]} for pos, pile in sorted(dungeon.ground_items.items())],
            "enemies": [{"unit": unit_data(enemy), "mode": enemy.ai_mode.value,
                         "patrol_target": enemy.patrol_target, "last_known_player_position": enemy.last_known_player_position} for enemy in dungeon.enemies],
            "timer": {"entries": [{"unit": units[id(entry.unit)], "remaining": entry.remaining} for entry in dungeon.combat_timer.entries],
                      "value": dungeon.combat_timer.turn_counter.value,
                      "interval": dungeon.combat_timer.turn_counter.interval,
                      "last_completed_turns": dungeon.combat_timer.last_completed_turns},
        }
    return {"save_version": 2, "current_floor": session.current_floor, "inventory": inv, "items": items, "floors": floors}


def from_data(data):
    if type(data["save_version"]) is not int or data["save_version"] not in (1, 2):
        raise ValueError("지원하지 않는 저장 버전입니다.")
    inv = data["inventory"]
    if type(inv["game_seed"]) not in (int, float, str):
        raise ValueError("지원하지 않는 시드 형식입니다.")
    inventory = DungeonInventory(game_seed=inv["game_seed"])
    inventory.player = read_unit(inv["player"])
    items = {}
    for key, entry in data["items"].items():
        item = ITEM_FACTORIES[entry["code"]]()
        stack = integer(entry["stack"], 1)
        if isinstance(item, Equip) != (entry["rows"] is not None):
            raise ValueError("아이템과 장비 데이터 형식이 일치하지 않습니다.")
        items[key] = (EquipmentInstance(item, stack, [read_skill(row) for row in entry["rows"]])
                      if entry["rows"] is not None else ItemInstance(item, stack))
    inventory.item_inventory = ItemInventory(integer(inv["capacity"]), [items[key] for key in inv["items"]])
    owned = list(inv["items"])
    for slot in inventory.EQUIPMENT_SLOTS:
        key = inv["equipment"][slot]
        item = items[key] if key is not None else None
        if item is not None:
            if not isinstance(item, EquipmentInstance) or slot not in inventory.EQUIPMENT_SLOTS_BY_TYPE[item.item.type]:
                raise ValueError("장비 슬롯이 올바르지 않습니다.")
            owned.append(key)
        setattr(inventory, slot, item)
    if len(set(owned)) != len(owned):
        raise ValueError("동일 아이템이 여러 보관 위치에 있습니다.")
    inventory.hotbar_items = {label: items[key] for label, key in inv["hotbar_items"].items()}
    if any(key not in inv["items"] for key in inv["hotbar_items"].values()):
        raise ValueError("단축키가 소유하지 않은 아이템을 참조합니다.")
    inventory.hotbar_skill_codes = inv["hotbar_skills"]
    if any(code not in SKILL_DEFINITIONS for code in inventory.hotbar_skill_codes.values()):
        raise ValueError("알 수 없는 단축키 스킬입니다.")
    inventory.gold = integer(inv["gold"])
    inventory.harmony_stones = integer(inv["harmony_stones"])
    inventory.learnable_skills = [LearnableSkill(integer(entry["tier"], 1), read_skill(entry["skill"]), entry["max_level"]) for entry in inv["learnable_skills"]]
    inventory.tier_skill_points = {integer(int(tier), 1): integer(points) for tier, points in inv["tier_points"].items()}
    inventory.floor_randoms = inv["floor_randoms"]
    if len(inventory.floor_randoms) != inventory.FLOOR_COUNT:
        raise ValueError("층 난수 개수가 올바르지 않습니다.")
    for state in inventory.floor_randoms:
        RandomGenerator.from_state(state)
    for name in RNG_NAMES:
        states = inv["random_states"][name]
        if len(states) != inventory.FLOOR_COUNT:
            raise ValueError("층 난수 상태 개수가 올바르지 않습니다.")
        setattr(inventory, f"{name}_random_generators", [RandomGenerator.from_state(state) for state in states])
    session = GameSession(inventory, current_floor=integer(data["current_floor"], 1))
    for floor_key, positions in inv["explored"].items():
        floor = int(floor_key)
        inventory._floor_index(floor)
        explored = set()
        for value in positions:
            if len(value) != 2:
                raise ValueError("발견 좌표가 올바르지 않습니다.")
            explored.add(tuple(integer(v) for v in value))
        inventory.explored_tiles_by_floor[floor] = explored
    for floor_key, entry in data["floors"].items():
        floor = integer(int(floor_key), 1)
        inventory._floor_index(floor)
        tiles = entry["tiles"]
        if not tiles or not tiles[0] or any(len(row) != len(tiles[0]) for row in tiles):
            raise ValueError("던전 격자가 올바르지 않습니다.")
        if any(type(tile) is not int or tile not in range(6) for row in tiles for tile in row):
            raise ValueError("알 수 없는 타일입니다.")

        def position(value, nullable=False):
            if value is None and nullable:
                return None
            if len(value) != 2:
                raise ValueError("좌표가 올바르지 않습니다.")
            x, y = (integer(v) for v in value)
            if not (x < len(tiles[0]) and y < len(tiles)):
                raise ValueError("좌표가 던전 범위를 벗어났습니다.")
            return (x, y)

        dungeon = DungeonMap(
            tiles=tuple(tuple(row) for row in tiles),
            rooms=tuple(Room(**room) for room in entry["rooms"]),
            connections=tuple(MapConnection(**{**c, "path": tuple(position(p) for p in c["path"])}) for c in entry["connections"]),
            hub_room_id=entry["hub_room_id"], up_stairs=position(entry["up_stairs"], True),
            down_stairs=position(entry["down_stairs"], True), seed=entry["seed"],
            player=inventory.player, initialized=entry["initialized"],
            event_tiles=[EventTile(**event) for event in entry["events"]],
        )
        room_ids = set()
        for room in dungeon.rooms:
            integer(room.room_id)
            integer(room.width, 1)
            integer(room.height, 1)
            position((room.x, room.y))
            position((room.right, room.bottom))
            if room.room_id in room_ids:
                raise ValueError("방 ID가 중복됩니다.")
            room_ids.add(room.room_id)
        for connection in dungeon.connections:
            if connection.room_a not in room_ids or connection.room_b not in room_ids:
                raise ValueError("통로의 방 참조가 올바르지 않습니다.")
        for event in dungeon.event_tiles:
            for pos in event.positions:
                position(pos)
        if entry["initialized"] is not True:
            raise ValueError("초기화되지 않은 던전 저장입니다.")
        dungeon.event_states = plain(entry["event_states"])
        if type(dungeon.event_states) is not dict:
            raise ValueError("이벤트 상태가 올바르지 않습니다.")
        for pile in entry["ground_items"]:
            pos = position(pile["position"])
            if pos in dungeon.ground_items:
                raise ValueError("바닥 아이템 좌표가 중복됩니다.")
            dungeon.ground_items[pos] = [items[key] for key in pile["items"]]
            owned.extend(pile["items"])
        units = {"player": inventory.player}
        for index, enemy_data in enumerate(entry["enemies"]):
            enemy = read_unit(enemy_data["unit"], enemy=True, legacy=data["save_version"] == 1)
            position((enemy.tile_x, enemy.tile_y))
            enemy.ai_mode = EnemyMode(enemy_data["mode"])
            enemy.patrol_target = position(enemy_data["patrol_target"], True)
            enemy.last_known_player_position = position(enemy_data["last_known_player_position"], True)
            dungeon.enemies.append(enemy)
            units[f"enemy_{index}"] = enemy
        timer = entry["timer"]
        references = [e["unit"] for e in timer["entries"]]
        if len(references) != len(set(references)) or set(references) != set(units):
            raise ValueError("전투 타이머 참조가 올바르지 않습니다.")
        dungeon.combat_timer.entries = [CombatTimerEntry(units[e["unit"]], integer(e["remaining"])) for e in timer["entries"]]
        dungeon.combat_timer.turn_counter.interval = integer(timer["interval"], 1)
        dungeon.combat_timer.turn_counter.value = integer(timer["value"])
        if timer["value"] >= timer["interval"]:
            raise ValueError("턴 카운터 범위가 올바르지 않습니다.")
        dungeon.combat_timer.last_completed_turns = integer(timer["last_completed_turns"])
        session.floors[floor] = dungeon
        for pos in inventory.get_explored_tiles(floor):
            position(pos)
        if floor == session.current_floor:
            x, y = position((inventory.player.tile_x, inventory.player.tile_y))
            if tiles[y][x] in (1, 4):
                raise ValueError("플레이어 위치가 이동 불가능한 타일입니다.")
    if session.current_floor not in session.floors or len(set(owned)) != len(owned):
        raise ValueError("현재 층 또는 아이템 소유 관계가 올바르지 않습니다.")
    return session
