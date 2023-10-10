class RotationEvent:
    def __init__(
        self,
        stage_type: str,
        pokemon: str,
        stage_ids: str,
        cost_unlock: str,
        encounter_rates: str,
    ) -> None:
        self.stage_type = stage_type
        self.pokemon = pokemon
        self.stage_ids = tuple(map(int, stage_ids.split("/")))
        self.cost_unlock = cost_unlock
        self.encounter_rates: tuple[float, ...] = (
            tuple(map(float, encounter_rates.split("/")))
            if encounter_rates != "Nothing"
            else tuple()
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
        self.cost_type = cost_type
        self.attempt_cost = attempt_cost
        self.drops = drops
        self.items_available = items_available

    @property
    def cost(self) -> tuple[str, int]:
        return (self.cost_type, self.attempt_cost)
