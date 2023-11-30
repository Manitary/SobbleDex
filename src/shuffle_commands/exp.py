import itertools
from typing import Any

import discord

import db
import settings
from koduck import KoduckContext
from models import Payload

from . import decorators
from .shuffle_commands import lookup_pokemon


@decorators.allow_space_delimiter()
async def exp(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | Payload | None:
    if not args:
        return Payload(content=settings.message_exp_no_param)
    # parse params
    _query = args[0]
    query_pokemon = ""
    # ? split into two functions for digit and string?
    try:
        query_bp = int(_query)
        assert query_bp in range(30, 91, 10)
    except ValueError:
        query_pokemon = await lookup_pokemon(context, _query=_query)
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return
        pokemon_ = db.query_pokemon(query_pokemon)
        assert pokemon_
        query_bp = pokemon_.bp
    except AssertionError:
        return Payload(content=settings.message_exp_invalid_param)

    exp_table = db.query_exp(query_bp)

    if len(args) == 1:
        desc = settings.message_exp_result_3.format(query_bp)
        desc += "\n```\n"
        desc += "\n".join(
            "".join(f"{x:>7}" for x in group)
            for group in itertools.batched(exp_table, 10)
        )
        desc += "\n```"
        desc += settings.message_exp_result_4.format(query_bp)
        desc += "\n```\n"
        desc += "\n".join(
            "".join(f"{(xp1-xp2):>7}" for xp1, xp2 in group)
            for group in itertools.batched(zip(exp_table, [0] + exp_table), 10)
        )
        desc += "\n```"
        return Payload(content=desc)

    try:
        query_level_1, query_level_2 = (
            (1, int(args[1])) if len(args) == 2 else (int(args[1]), int(args[2]))
        )
    except ValueError:
        return Payload(content=settings.message_exp_invalid_param_2)

    if query_level_1 not in range(1, 31) or query_level_2 not in range(1, 31):
        return Payload(content=settings.message_exp_invalid_param_2)

    # retrieve data
    ap_table = db.query_ap(query_bp)
    start_exp = exp_table[query_level_1 - 1]
    end_exp = exp_table[query_level_2 - 1]
    start_ap = ap_table[query_level_1 - 1]
    end_ap = ap_table[query_level_2 - 1]

    if _query.isdigit():
        return Payload(
            content=settings.message_exp_result.format(
                query_bp,
                end_exp - start_exp,
                query_level_1,
                start_ap,
                query_level_2,
                end_ap,
            ),
        )

    return Payload(
        content=settings.message_exp_result_2.format(
            query_pokemon,
            query_bp,
            end_exp - start_exp,
            query_level_1,
            start_ap,
            query_level_2,
            end_ap,
        ),
    )
