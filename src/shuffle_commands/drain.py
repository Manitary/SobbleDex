from math import floor
from typing import Any

import discord

import settings
from koduck import KoduckContext

from .decorators import allow_space_delimiter, min_param


@allow_space_delimiter()
@min_param(num=2, error=settings.message_drain_list_no_param)
async def drain_list(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    # first arg hp, second arg moves
    try:
        hp = int(args[0])
        moves = int(args[1])
        assert hp > 0 and moves > 0
    except (ValueError, AssertionError):
        return await context.send_message(
            content=settings.message_drain_list_invalid_param,
        )

    if moves > 55:
        return await context.send_message(
            content=settings.message_drain_list_invalid_param_2,
        )

    output = f"```\nhp:    {hp}\nmoves: {moves}\n\n"

    for i in range(moves):
        drain_amount = floor(float(hp) * 0.1)
        output += f"{moves-i:>2}: {drain_amount:>5} ({hp:>6} => {hp-drain_amount:>6})\n"
        hp -= drain_amount

    output += "```"

    return await context.send_message(content=output)
