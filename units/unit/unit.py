from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from random import Random

from .damage_block import DamageBlock
from .variable import (
    BASE_TURN_COST,
    LUCK_BASE,
    LUCK_DIVISOR,
    MAX_DROP_BONUS,
    MAX_REWARD_RATE,
    MAX_SPEED_STEP,
    MIN_DROP_BONUS,
    MIN_MAX_HP,
    MIN_MAX_MP,
    MIN_REWARD_RATE,
    MIN_SPEED_STEP,
    SPEED_MULTIPLIER_BASE,
    SPEED_STEP_DIVISOR,
)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


@dataclass(frozen=True)
class AttackResult:
    hit: bool
    critical_type: str
    damage: int
    hit_rate: float
    calculated_hit_rate: float
    critical_rate: float
    critical_raw_rate: float


@dataclass(frozen=True)
class DamagePreview:
    normal_damage: int
    under_critical_damage: int
    critical_damage: int
    miss_probability: float
    normal_probability: float
    under_critical_probability: float
    critical_probability: float
    hit_rate: float
    calculated_hit_rate: float
    critical_rate: float
    critical_raw_rate: float


@dataclass
class Unit:
    name: str
    max_hp: int
    attack_power: int
    max_mp: int = 0
    defense: int = 0
    penetration: int = 0
    accuracy: int = 0
    evasion: int = 0
    attack_speed: int = 0
    move_speed: int = 0
    luck: int = 0
    overloaded: int = 0
    critical_chance: float = 0.0
    critical_defense: float = 0.0
    critical_damage: float = 0.0
    damage_increase: float = 0.0
    incoming_damage_reduction: float = 0.0
    equipment_drop_rate: float = 0.0
    gold_drop_amount: float = 0.0
    hp: int | None = None
    mp: int | None = None
    skills: list = field(default_factory=list)
    buffs: list = field(default_factory=list)

    def __post_init__(self):
        self.max_hp = max(MIN_MAX_HP, self.max_hp)
        self.max_mp = max(MIN_MAX_MP, self.max_mp)
        self.attack_speed = clamp(self.attack_speed, MIN_SPEED_STEP, MAX_SPEED_STEP)
        self.move_speed = clamp(self.move_speed, MIN_SPEED_STEP, MAX_SPEED_STEP)

        if self.hp is None:
            self.hp = self.max_hp
        else:
            self.hp = clamp(self.hp, 0, self.max_hp)

        if self.mp is None:
            self.mp = self.max_mp
        else:
            self.mp = clamp(self.mp, 0, self.max_mp)

    @property
    def is_alive(self):
        return self.hp > 0

    @property
    def attack_turn_cost(self):
        return self.get_speed_turn_cost(self.attack_speed)

    @property
    def move_turn_cost(self):
        return self.get_speed_turn_cost(self.move_speed)

    @property
    def luck_multiplier(self):
        return LUCK_BASE ** (self.luck / LUCK_DIVISOR)

    def heal(self, amount):
        if amount <= 0 or not self.is_alive:
            return 0

        before_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before_hp

    def recover_mp(self, amount):
        if amount <= 0:
            return 0

        before_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - before_mp

    def spend_mp(self, amount):
        if amount < 0 or self.mp < amount:
            return False

        self.mp -= amount
        return True

    def add_skill(self, skill):
        self.skills.append(skill)
        return skill

    def remove_skill(self, skill):
        if skill not in self.skills:
            return False

        self.skills.remove(skill)
        return True

    def add_buff(self, buff):
        self.buffs.append(buff)
        return buff

    def remove_buff(self, buff):
        if buff not in self.buffs:
            return False

        self.buffs.remove(buff)
        return True

    def take_damage(self, damage):
        damage = max(0, damage)

        if damage <= 0 or not self.is_alive:
            return 0

        self.hp = max(0, self.hp - damage)
        return damage

    def make_damage_block(self, target, **kwargs):
        return DamageBlock(self, target, **kwargs)

    def attack(self, target, skill_coefficient=1.0, rng=None, damage_block=None):
        if damage_block is None:
            damage_block = self.make_damage_block(target, skill_coefficient=skill_coefficient)

        return damage_block.apply(rng)

    def calculate_attack(self, target, skill_coefficient=1.0, rng=None):
        damage_block = self.make_damage_block(target, skill_coefficient=skill_coefficient)
        return damage_block.apply(rng)

    def peek_damage_block(self, damage_block):
        hit_rate, calculated_hit_rate, critical_rate, critical_raw_rate = self.get_damage_block_rates(damage_block)
        critical_damage_conversion = max(0.0, critical_raw_rate - DamageBlock.MAX_CRITICAL_RATE)
        damage_increase_conversion = -max(0.0, DamageBlock.MIN_CRITICAL_RATE - critical_raw_rate)
        preview_random_modifier = self.get_preview_random_damage_modifier(damage_block)
        critical_probability = 0.0
        under_critical_probability = 0.0

        if critical_rate > 0:
            critical_probability = hit_rate * critical_rate / 100
        elif critical_rate < 0:
            under_critical_probability = hit_rate * abs(critical_rate) / 100

        normal_probability = hit_rate - critical_probability - under_critical_probability

        return DamagePreview(
            normal_damage=self.get_attack_damage(
                damage_block,
                "normal",
                critical_damage_conversion,
                damage_increase_conversion,
                preview_random_modifier,
            ),
            under_critical_damage=self.get_attack_damage(
                damage_block,
                "under_critical",
                critical_damage_conversion,
                damage_increase_conversion,
                preview_random_modifier,
            ),
            critical_damage=self.get_attack_damage(
                damage_block,
                "critical",
                critical_damage_conversion,
                damage_increase_conversion,
                preview_random_modifier,
            ),
            miss_probability=DamageBlock.MAX_HIT_RATE - hit_rate,
            normal_probability=normal_probability,
            under_critical_probability=under_critical_probability,
            critical_probability=critical_probability,
            hit_rate=hit_rate,
            calculated_hit_rate=calculated_hit_rate,
            critical_rate=critical_rate,
            critical_raw_rate=critical_raw_rate,
        )

    def apply_damage_block(self, damage_block, rng=None):
        rng = rng or Random()
        hit_rate, calculated_hit_rate, critical_rate, critical_raw_rate = self.get_damage_block_rates(damage_block)

        if rng.random() * 100 > hit_rate:
            return AttackResult(
                hit=False,
                critical_type="miss",
                damage=0,
                hit_rate=hit_rate,
                calculated_hit_rate=calculated_hit_rate,
                critical_rate=0.0,
                critical_raw_rate=0.0,
            )

        critical_type = self.roll_critical_type(critical_rate, rng)
        critical_damage_conversion = max(0.0, critical_raw_rate - DamageBlock.MAX_CRITICAL_RATE)
        damage_increase_conversion = -max(0.0, DamageBlock.MIN_CRITICAL_RATE - critical_raw_rate)
        damage = self.get_attack_damage(
            damage_block,
            critical_type,
            critical_damage_conversion,
            damage_increase_conversion,
            self.get_random_damage_modifier(damage_block, rng),
        )

        return AttackResult(
            hit=True,
            critical_type=critical_type,
            damage=damage,
            hit_rate=hit_rate,
            calculated_hit_rate=calculated_hit_rate,
            critical_rate=critical_rate,
            critical_raw_rate=critical_raw_rate,
        )

    def calculate_damage_block(self, damage_block, rng=None):
        return self.apply_damage_block(damage_block, rng)

    def get_damage_block_rates(self, damage_block):
        target = damage_block.defender
        calculated_hit_rate = self.get_calculated_hit_rate(target, damage_block.accuracy_bonus)
        hit_rate = clamp(calculated_hit_rate, DamageBlock.MIN_HIT_RATE, DamageBlock.MAX_HIT_RATE)
        critical_raw_rate = self.get_critical_raw_rate(target, calculated_hit_rate, damage_block.critical_chance_bonus)
        critical_rate = clamp(
            critical_raw_rate,
            DamageBlock.MIN_CRITICAL_RATE,
            DamageBlock.MAX_CRITICAL_RATE,
        )
        return hit_rate, calculated_hit_rate, critical_rate, critical_raw_rate

    def get_attack_damage(
        self,
        damage_block,
        critical_type,
        critical_damage_conversion,
        damage_increase_conversion,
        random_modifier,
    ):
        target = damage_block.defender
        base_damage = damage_block.base_damage

        if base_damage is None:
            base_damage = self.attack_power

        base_damage = base_damage * damage_block.skill_coefficient + damage_block.flat_damage_bonus
        damage = (
            base_damage
            * self.get_defense_modifier(target, damage_block.penetration_bonus)
            * self.get_excess_penetration_modifier(target, damage_block.penetration_bonus)
            * self.get_critical_modifier(
                critical_type,
                critical_damage_conversion,
                damage_block.critical_damage_bonus,
            )
            * self.get_damage_increase_modifier(damage_increase_conversion, damage_block.damage_increase_bonus)
            * self.get_overloaded_damage_modifier()
            * damage_block.outgoing_damage_modifier
            * target.get_incoming_damage_modifier(damage_block.incoming_damage_reduction_bonus)
            * damage_block.incoming_damage_modifier
            * target.get_overloaded_damage_modifier()
            * random_modifier
        )

        return max(1, floor(damage))

    def get_calculated_hit_rate(self, target, accuracy_bonus=0):
        accuracy_difference = self.accuracy + accuracy_bonus - target.evasion
        accuracy_advantage = max(0, accuracy_difference)
        evasion_advantage = max(0, -accuracy_difference)

        return (
            DamageBlock.BASE_HIT_RATE
            + min(accuracy_advantage, DamageBlock.HIT_RATE_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.HIT_RATE_HIGH_EFFICIENCY_STEP
            + max(0, accuracy_advantage - DamageBlock.HIT_RATE_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.HIT_RATE_LOW_EFFICIENCY_STEP
            - min(evasion_advantage, DamageBlock.HIT_RATE_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.HIT_RATE_HIGH_EFFICIENCY_STEP
            - max(0, evasion_advantage - DamageBlock.HIT_RATE_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.HIT_RATE_LOW_EFFICIENCY_STEP
        )

    def get_critical_raw_rate(self, target, calculated_hit_rate, critical_chance_bonus=0.0):
        derived_critical_rate = max(0.0, calculated_hit_rate - DamageBlock.MAX_HIT_RATE) - max(
            0.0,
            DamageBlock.MIN_HIT_RATE - calculated_hit_rate,
        )
        return derived_critical_rate + self.critical_chance + critical_chance_bonus - target.critical_defense

    def get_defense_modifier(self, target, penetration_bonus=0):
        effective_defense = max(0, target.defense - (self.penetration + penetration_bonus))
        return DamageBlock.DEFENSE_BASE_VALUE / (DamageBlock.DEFENSE_BASE_VALUE + effective_defense)

    def get_excess_penetration_modifier(self, target, penetration_bonus=0):
        excess_penetration = max(0, self.penetration + penetration_bonus - target.defense)
        return (
            1
            + min(excess_penetration, DamageBlock.EXCESS_PENETRATION_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.EXCESS_PENETRATION_HIGH_EFFICIENCY_DAMAGE_RATE
            + max(0, excess_penetration - DamageBlock.EXCESS_PENETRATION_HIGH_EFFICIENCY_LIMIT)
            * DamageBlock.EXCESS_PENETRATION_LOW_EFFICIENCY_DAMAGE_RATE
        )

    def get_critical_modifier(self, critical_type, critical_damage_conversion=0.0, critical_damage_bonus=0.0):
        if critical_type == "critical":
            critical_damage = max(
                DamageBlock.MIN_CRITICAL_DAMAGE,
                DamageBlock.BASE_CRITICAL_DAMAGE
                + self.critical_damage
                + critical_damage_bonus
                + critical_damage_conversion,
            )
            return 1 + critical_damage / 100
        if critical_type == "under_critical":
            return DamageBlock.UNDER_CRITICAL_DAMAGE_MODIFIER

        return 1.0

    def get_damage_increase_modifier(self, damage_increase_conversion=0.0, damage_increase_bonus=0.0):
        damage_increase = max(
            DamageBlock.MIN_DAMAGE_INCREASE,
            self.damage_increase + damage_increase_bonus + damage_increase_conversion,
        )
        return 1 + damage_increase / 100

    def get_incoming_damage_modifier(self, incoming_damage_reduction_bonus=0.0):
        incoming_damage_reduction = min(
            self.incoming_damage_reduction + incoming_damage_reduction_bonus,
            DamageBlock.MAX_INCOMING_DAMAGE_REDUCTION,
        )
        return 1 - incoming_damage_reduction / 100

    @staticmethod
    def get_random_damage_modifier(damage_block, rng):
        if damage_block.random_modifier is not None:
            return damage_block.random_modifier
        if not damage_block.use_random_modifier:
            return 1.0

        return rng.uniform(DamageBlock.MIN_RANDOM_DAMAGE_MODIFIER, DamageBlock.MAX_RANDOM_DAMAGE_MODIFIER)

    @staticmethod
    def get_preview_random_damage_modifier(damage_block):
        if damage_block.random_modifier is not None:
            return damage_block.random_modifier

        return 1.0

    def get_overloaded_damage_modifier(self):
        return 1 + self.overloaded * DamageBlock.OVERLOADED_DAMAGE_RATE

    def get_equipment_drop_rate(self, base_drop_rate):
        drop_rate_modifier = 1 + clamp(self.equipment_drop_rate, MIN_DROP_BONUS, MAX_DROP_BONUS) / 100
        return clamp(base_drop_rate * self.luck_multiplier * drop_rate_modifier, MIN_REWARD_RATE, MAX_REWARD_RATE)

    def get_gold_drop_amount(self, base_gold_amount):
        gold_modifier = 1 + clamp(self.gold_drop_amount, MIN_DROP_BONUS, MAX_DROP_BONUS) / 100
        return floor(base_gold_amount * self.luck_multiplier * gold_modifier)

    @staticmethod
    def roll_critical_type(critical_rate, rng):
        if critical_rate > 0 and rng.random() * 100 <= critical_rate:
            return "critical"
        if critical_rate < 0 and rng.random() * 100 <= abs(critical_rate):
            return "under_critical"

        return "normal"

    @staticmethod
    def get_speed_turn_cost(speed_step):
        return round(
            BASE_TURN_COST
            / (SPEED_MULTIPLIER_BASE ** (clamp(speed_step, MIN_SPEED_STEP, MAX_SPEED_STEP) / SPEED_STEP_DIVISOR))
        )
