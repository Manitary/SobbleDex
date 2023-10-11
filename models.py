import enum
from dataclasses import dataclass
from typing import Callable, Self


class MyStrEnum(enum.StrEnum):
    @classmethod
    def _missing_(cls, value: object) -> Self:
        if isinstance(value, str):
            value = value.upper()
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


@dataclass
class Setting:
    key: str
    value: str
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
