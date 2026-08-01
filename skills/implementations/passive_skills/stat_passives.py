from skills.passive_effect import StatIncreaseEffect
from skills.skill_base import SkillBase


STAT_PASSIVE_DEFINITIONS = (
    ("max_hp", "체력 증가", "passive_max_hp", 10),
    ("attack_power", "공격력 증가", "passive_attack_power", 5),
    ("max_mp", "마나 증가", "passive_max_mp", 5),
    ("defense", "방어력 증가", "passive_defense", 3),
    ("penetration", "관통력 증가", "passive_penetration", 2),
    ("accuracy", "명중 증가", "passive_accuracy", 2),
    ("evasion", "회피 증가", "passive_evasion", 2),
    ("attack_speed", "공격 속도 증가", "passive_attack_speed", 2),
    ("move_speed", "이동 속도 증가", "passive_move_speed", 1),
    ("luck", "행운 증가", "passive_luck", 1),
    ("overloaded", "과부화 증가", "passive_overloaded", 5),
    ("critical_chance", "치명타 확률 증가", "passive_critical_chance", 1.0),
    ("critical_evasion", "치명타 회피 증가", "passive_critical_evasion", 1.0),
    ("critical_damage", "치명타 피해 증가", "passive_critical_damage", 2.0),
    ("critical_damage_reduction", "치명타 피해 감소 증가", "passive_critical_damage_reduction", 2.0),
    ("damage_increase", "피해 증가", "passive_damage_increase", 1.0),
    ("incoming_damage_reduction", "받는 피해 감소 증가", "passive_incoming_damage_reduction", 1.0),
    ("equipment_drop_rate", "장비 드롭률 증가", "passive_equipment_drop_rate", 1.0),
    ("gold_drop_amount", "골드 획득량 증가", "passive_gold_drop_amount", 2.0),
)


def create_stat_passive_skills():
    return [
        SkillBase(
            name=name,
            skill_code=skill_code,
            description=f"레벨마다 {name} 수치를 {amount:g} 증가시킨다.",
            max_level=5,
            requires_direction=False,
            effects=[
                StatIncreaseEffect(
                    stat_name=stat_name,
                    amount_per_level=amount,
                )
            ],
        )
        for stat_name, name, skill_code, amount in STAT_PASSIVE_DEFINITIONS
    ]


STAT_PASSIVE_SKILLS = create_stat_passive_skills()
