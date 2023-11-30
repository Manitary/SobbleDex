import itertools
from typing import Any

import discord

import db
import settings
from koduck import KoduckContext

from .decorators import allow_space_delimiter, min_param


@allow_space_delimiter()
@min_param(num=1, error=settings.message_ap_no_param)
async def ap(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    try:
        query_bp = int(args[0])
        assert query_bp in range(30, 91, 10)
    except (ValueError, AssertionError):
        return await context.send_message(content=settings.message_ap_invalid_param)

    ap_list = db.query_ap(int(query_bp))

    if len(args) >= 2:
        try:
            query_level = int(args[1])
            assert 1 <= query_level <= 30
        except (ValueError, AssertionError):
            return await context.send_message(
                content=settings.message_ap_invalid_param_2,
            )
        return await context.send_message(content=str(ap_list[query_level - 1]))

    desc = (
        "```"
        + "\n".join(
            " ".join(f"{x:>3}" for x in group)
            for group in itertools.batched(ap_list, 10)
        )
        + "```"
    )
    return await context.send_message(content=desc)
