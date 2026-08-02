from skills.active_skill import ActiveSkill


class AttackSkill(ActiveSkill):
    """정면 한 칸의 대상에게 공격력 1배 피해를 주는 기본 공격."""

    def __init__(
        self,
        name="공격",
        skill_code="attack",
        max_level=5,
    ):
        super().__init__(
            name=name,
            skill_code=skill_code,
            description="한 칸 앞의 적에게 공격력 1배의 피해를 준다.",
            skill_coefficient=1.0,
            range_vectors=[(0, -1)],
            allow_diagonal=True,
            max_level=max_level,
        )

    def get_description(self, level: int) -> str:
        return "한 칸 앞의 적에게 공격력 1배의 피해를 준다."
