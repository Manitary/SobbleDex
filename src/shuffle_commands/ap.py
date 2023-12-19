import itertools
from typing import Any

import db
import settings
from exceptions import InvalidBP, InvalidLevel
from koduck import KoduckContext
from models import Payload

from .decorators import allow_space_delimiter, min_param


@allow_space_delimiter()
@min_param(num=1, error=settings.message_ap_no_param)
async def ap(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    try:
        bp = int(args[0])
    except ValueError:
        return Payload(content=settings.message_ap_invalid_param)

    if len(args) == 1:
        try:
            content = _ap_table_string(bp)
        except InvalidBP:
            content = settings.message_ap_invalid_param
    else:
        try:
            content = str(_ap_at_level(bp, int(args[1])))
        except InvalidBP:
            content = settings.message_ap_invalid_param
        except (ValueError, InvalidLevel):
            content = settings.message_ap_invalid_param_2

    return Payload(content=content)


def _ap_table_string(bp: int) -> str:
    return (
        "```"
        + "\n".join(
            " ".join(f"{x:>3}" for x in group)
            for group in itertools.batched(db.query_ap(bp), 10)
        )
        + "```"
    )


def _ap_at_level(bp: int, level: int) -> int:
    return db.get_ap_at_level(bp, level)
