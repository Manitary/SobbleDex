import enum
from dataclasses import dataclass, field
from typing import Any, Self


class QueryType(enum.StrEnum):
    ANY = enum.auto()
    STAGE = enum.auto()

    @classmethod
    def _missing_(cls, value: object) -> Self:
        if isinstance(value, str):
            if value in dir(cls):
                return cls[value]
        return cls["ANY"]


@dataclass
class UserQuery:
    type: QueryType
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
