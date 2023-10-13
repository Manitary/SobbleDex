import enum
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Self

import pytz

RE_MOVES_EXP = re.compile(r"(\d+) \(Mobile: (\d+)\)")


class MyStrEnum(enum.StrEnum):
    @classmethod
    def _missing_(cls, value: object) -> Self:
        if isinstance(value, str):
            value = value.upper().replace(" ", "_")
            if value in dir(cls):
                return cls[value]
        raise ValueError(f"Invalid event type: {value}")


class CostType(MyStrEnum):
    HEART = "Heart"
    COIN = "Coin"


class EventType(MyStrEnum):
    MONTHLY = "Monthly"
    DAILY = "Daily"
    MEOWTH = "Meowth"
    CHALLENGE = "Challenge"
    COMPETITIVE = "Competitive"
    SAFARI = "Safari"
    ESCALATION = "Escalation"


class RepeatType(MyStrEnum):
    MONTHLY = "Monthly"
    YEARLY = "Yearly"
    WEEKLY = "Weekly"
    ROTATION = "Rotation"


class StageType(MyStrEnum):
    MAIN = "Main"
    EXPERT = "Expert"
    EVENT = "Event"
    ALL = "all"


class PokemonType(MyStrEnum):
    NORMAL = "Normal"
    FIGHTING = "Fighting"
    FLYING = "Flying"
    POISON = "Poison"
    GROUND = "Ground"
    ROCK = "Rock"
    BUG = "Bug"
    GHOST = "Ghost"
    STEEL = "Steel"
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    PSYCHIC = "Psychic"
    ICE = "Ice"
    DRAGON = "Dragon"
    DARK = "Dark"
    FAIRY = "Fairy"


class PuzzleStage(MyStrEnum):
    PUZZLE = "Puzzle"
    NORMAL = "Normal"


class Param(enum.IntEnum):
    IGNORE = 0
    INCLUDE = 1
    EXCLUDE = 2


class SkillType(MyStrEnum):
    OFFENSIVE = "Offensive"
    DEFENSIVE = "Defensive"
    MEGA_BOOST = "Mega Boost"


class SkillBonus(MyStrEnum):
    MULTIPLY_DAMAGE = "Multiply Damage"
    ACTIVATION_RATE = "Activation Rate"
    ADD_DAMAGE = "Add Damage"


@dataclass
class Setting:
    key: str
    value: str
    tier: int


@dataclass
class Command:
    command_name: str
    module_name: str
    method_name: str
    command_type: str
    command_tier: int
    description: str


@dataclass(frozen=True)
class RealCommand:
    function: Callable[..., Any]
    type: str
    tier: int


@dataclass
class StageCost:
    type: CostType
    amount: int

    def to_str(self, emojify: Callable[[str], str]) -> str:
        if self.type == CostType.HEART and self.amount == 1:
            return ""
        return " ({} x{})".format(emojify(f"[{self.type}]"), self.amount)


class RotationEvent:
    def __init__(
        self,
        stage_type: str,
        pokemon: str,
        stage_ids: str,
        cost_unlock: str,
        encounter_rates: str,
    ) -> None:
        self.stage_type = EventType(stage_type)
        self.pokemon = pokemon
        self.stage_ids = tuple(map(int, stage_ids.split("/")))
        self.cost_unlock = cost_unlock
        self.encounter_rates: tuple[float, ...] = (
            tuple(map(float, encounter_rates.split("/")))
            if encounter_rates != "Nothing"
            else tuple()
        )

    def str_unlock(self, emojify: Callable[[str], str]) -> str:
        if self.cost_unlock == "Nothing":
            return ""
        return " ({} {})".format(
            emojify(self.cost_unlock.split()[1]),
            self.cost_unlock.split()[2],
        )


class EventPokemon:
    def __init__(
        self,
        stage_type: str,
        pokemon: str,
        repeat_type: str,
        repeat_param_1: int,
        repeat_param_2: int,
        date_start: str,
        date_end: str,
        duration: str,
    ) -> None:
        self.stage_type = EventType(stage_type)
        self.pokemon = pokemon.split("/")
        self.repeat_type = RepeatType(repeat_type)
        self.repeat_param_1 = repeat_param_1
        self.repeat_param_2 = repeat_param_2
        self.date_start = date_start.split("/")
        self.date_end = date_end.split("/")
        self.duration = int(duration.split()[0])

    @property
    def this_year_start_date(self) -> datetime:
        return datetime(
            datetime.now(tz=pytz.utc).year,
            self.repeat_param_1,
            self.repeat_param_2,
            tzinfo=pytz.utc,
        )

    @property
    def start_time(self) -> datetime:
        return datetime(*map(int, self.date_start), tzinfo=pytz.utc)

    @property
    def end_time(self) -> datetime:
        return datetime(*map(int, self.date_end), tzinfo=pytz.utc)

    def latest_start_time_for(self, date: datetime) -> datetime:
        num_rotations = (date - self.end_time).days // 168 + 1
        return self.start_time + timedelta(168) * num_rotations


class Drop:
    def __init__(self, item: str, amount: int, rate: float) -> None:
        self.item = item
        self.amount = amount
        self.rate = rate

    def __bool__(self) -> bool:
        return self.item != "Nothing"


class EventStageRotation:
    def __init__(
        self,
        cost_type: str,
        attempt_cost: int,
        drops: list[Drop],
        items_available: str,
    ) -> None:
        self.cost = StageCost(CostType(cost_type), attempt_cost)
        self.drops = drops
        self.items_available = items_available

    @property
    def cost_type(self) -> str:
        return self.cost.type.value

    @property
    def attempt_cost(self) -> int:
        return self.cost.amount

    def str_drops(self, emojify: Callable[[str], str], compact: bool = False) -> str:
        if not any(self.drops):
            return ""
        if (
            compact
            and len({d.item for d in self.drops}) == 1
            and len({d.amount for d in self.drops}) == 1
        ):
            return " [{}{} {}% / {}% / {}%]".format(
                emojify(f"[{self.drops[0].item}]"),
                f" x{self.drops[0].amount}" if self.drops[0].amount != 1 else "",
                self.drops[0].rate,
                self.drops[1].rate,
                self.drops[2].rate,
            )
        return " [{}{} {}% / {}{} {}% / {}{} {}%]".format(
            emojify(f"[{self.drops[0].item}]"),
            f" x{self.drops[0].amount}" if self.drops[0].amount != 1 else "",
            self.drops[0].rate,
            emojify(f"[{self.drops[1].item}]"),
            f" x{self.drops[1].amount}" if self.drops[1].amount != 1 else "",
            self.drops[1].rate,
            emojify(f"[{self.drops[2].item}]"),
            f" x{self.drops[2].amount}" if self.drops[2].amount != 1 else "",
            self.drops[2].rate,
        )


class Stage:
    def __init__(
        self,
        id: int,
        pokemon: str,
        hp: int,
        hp_mobile: int,
        moves: str,
        seconds: int,
        exp: str,
        base_catch: int,
        bonus_catch: int,
        base_catch_mobile: int,
        bonus_catch_mobile: int,
        default_supports: str,
        s_rank: int,
        a_rank: int,
        b_rank: int,
        num_s_ranks_to_unlock: int,
        is_puzzle_stage: str,
        extra_hp: int,
        layout_index: int,
        cost_type: str,
        attempt_cost: int,
        drop_1_item: str,
        drop_2_item: str,
        drop_3_item: str,
        drop_1_amount: int,
        drop_2_amount: int,
        drop_3_amount: int,
        drop_1_rate: float,
        drop_2_rate: float,
        drop_3_rate: float,
        items_available: str,
        rewards: str,
        rewards_UX: str,
        cd1: str,
        cd2: str,
        cd3: str,
        stage_type: StageType,
    ) -> None:
        self.id = id
        self.pokemon = pokemon
        self.hp = hp
        self.hp_mobile = hp_mobile
        try:
            self.moves = self.moves_mobile = int(moves)
        except ValueError as e:
            match = RE_MOVES_EXP.match(moves)
            if not match:
                raise e
            self.moves = int(match.group(1))
            self.moves_mobile = int(match.group(2))
        self.seconds = seconds
        try:
            self.exp = self.exp_mobile = int(exp)
        except ValueError as e:
            match = RE_MOVES_EXP.match(exp)
            if not match:
                raise e
            self.exp = int(match.group(1))
            self.exp_mobile = int(match.group(2))
        self.base_catch = base_catch
        self.bonus_catch = bonus_catch
        self.base_catch_mobile = base_catch_mobile
        self.bonus_catch_mobile = bonus_catch_mobile
        self.default_supports = default_supports.split("/")
        self.s_rank = s_rank
        self.a_rank = a_rank
        self.b_rank = b_rank
        self.s_unlock = num_s_ranks_to_unlock
        self.is_puzzle_stage = PuzzleStage(is_puzzle_stage)
        self.extra_hp = extra_hp
        self.layout_index = layout_index
        self.cost = StageCost(CostType(cost_type), attempt_cost)
        self.drops = [
            Drop(drop_1_item, drop_1_amount, drop_1_rate),
            Drop(drop_2_item, drop_2_amount, drop_2_rate),
            Drop(drop_3_item, drop_3_amount, drop_3_rate),
        ]
        self.items = items_available.split("/")
        self.rewards = rewards
        self.rewards_ux = rewards_UX
        self.disruptions = [cd1, cd2, cd3]
        self.stage_type = stage_type

    @property
    def string_id(self) -> str:
        if self.stage_type == StageType.MAIN:
            return str(self.id)
        if self.stage_type == StageType.EXPERT:
            return f"ex{self.id}"
        if self.stage_type == StageType.EVENT:
            return f"s{self.id}"
        raise ValueError("Cannot generate stage id")


@dataclass
class Pokemon:
    id: str
    pokemon: str
    dex: int
    type: PokemonType
    bp: int
    rml: int
    max_ap: int
    skill: str
    ss: str
    icons: int = 0
    msu: int = 0
    mega_power: int = 99
    fake: bool = False

    @property
    def ss_skills(self) -> list[str]:
        return self.ss.split("/")

    @property
    def all_skills(self) -> list[str]:
        return [self.skill] + self.ss_skills

    @property
    def evo_speed(self) -> int:
        return self.icons - self.msu


@dataclass
class EBStretch:
    pokemon: str
    start_level: int
    end_level: int
    stage_index: int


@dataclass
class EBReward:
    pokemon: str
    level: int
    reward: str
    amount: int
    alternative: str


class Event:
    def __init__(
        self,
        id: int,
        stage_type: str,
        pokemon: str,
        stage_ids: str,
        repeat_type: str,
        repeat_param_1: int,
        repeat_param_2: int,
        date_start: str,
        date_end: str,
        duration: str,
        cost_unlock: str,
        notes: str,
        encounter_rates: str,
    ) -> None:
        self.id = id
        self.event_type = EventType(stage_type)
        self.pokemon = pokemon.split("/")
        self.stage_ids = list(map(int, stage_ids.split("/")))
        self.repeat_type = RepeatType(repeat_type)
        self.repeat_param_1 = repeat_param_1
        self.repeat_param_2 = repeat_param_2
        self.date_start = date_start.split("/")
        self.date_end = date_end.split("/")
        self.duration = duration
        self.cost_unlock = "" if cost_unlock == "Nothing" else cost_unlock
        self.notes = "" if notes == "Nothing" else notes
        self.encounter_rates = (
            list(map(float, encounter_rates.split("/")))
            if encounter_rates != "Nothing"
            else []
        )

    @property
    def date_start_datetime(self) -> datetime:
        return datetime(*map(int, self.date_start), tzinfo=pytz.utc)

    @property
    def date_end_datetime(self) -> datetime:
        return datetime(*map(int, self.date_end), tzinfo=pytz.utc)

    @property
    def next_appearance(self) -> tuple[datetime, datetime]:
        num_cycles = (
            datetime.now(tz=pytz.utc) - self.date_end_datetime
        ).days // 168 + 1
        next_start = self.date_start_datetime + num_cycles * timedelta(168)
        next_end = self.date_end_datetime + num_cycles * timedelta(168)
        return next_start, next_end


@dataclass
class SMReward:
    level: int
    reward: str
    amount: int
    reward_repeat: str
    amount_repeat: int


class Reminder:
    def __init__(self, user_id: int, weeks: str, pokemon: str) -> None:
        self.user_id = user_id
        self.weeks = list(map(int, weeks.split(", ")))
        self.pokemon = pokemon.split(", ")

    def remove_week(self, week: int) -> None:
        self.weeks.remove(week)

    def remove_pokemon(self, pokemon: str) -> None:
        self.pokemon.remove(pokemon)

    @property
    def weeks_str(self) -> str:
        return ", ".join(map(str, self.weeks))

    @property
    def pokemon_str(self) -> str:
        return ", ".join(self.pokemon)


class Skill:
    def __init__(
        self,
        id: int,
        skill: str,
        description: str,
        rate1: int,
        rate2: int,
        rate3: int,
        type: str,
        multiplier: float,
        bonus_effect: str,
        bonus1: float,
        bonus2: float,
        bonus3: float,
        bonus4: float,
        sp1: int,
        sp2: int,
        sp3: int,
        sp4: int,
        notes: str,
    ) -> None:
        self.id = id
        self.skill = skill
        self.description = description
        self.rates = (rate1, rate2, rate3)
        self.type = SkillType(type)
        self.multiplier = multiplier
        self.bonus_effect = SkillBonus(bonus_effect)
        self.bonus = (bonus1, bonus2, bonus3, bonus4)
        self.sp_cost = (sp1, sp2, sp3, sp4)
        self.notes = notes or ""

    @property
    def sp_cost_partial(self) -> tuple[int, ...]:
        return (
            (self.sp_cost[0],)
            + tuple(map(lambda x: x[0] - x[1], zip(self.sp_cost[1:], self.sp_cost)))
            + (self.sp_cost[-1],)
        )


class TypeInfo:
    def __init__(
        self,
        id: int,
        type: str,
        se: str,
        nve: str,
        weak: str,
        resist: str,
        status_immune: str,
    ) -> None:
        self.id = id
        self.type = PokemonType(type)
        self.se = se
        self.nve = nve
        self.weak = weak
        self.resist = resist
        self.status_immune = status_immune
