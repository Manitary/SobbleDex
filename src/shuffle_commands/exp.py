import itertools
from typing import Any

import constants
import db
import settings
from koduck import KoduckContext
from models import Payload

from .decorators import allow_space_delimiter, min_param
from .shuffle_commands import lookup_pokemon


@min_param(1, settings.message_exp_no_param)
@allow_space_delimiter()
async def exp(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    pokemon, bp = await _get_pokemon_bp(context, args[0])

    if bp not in constants.pokemon_bps:
        return Payload(content=settings.message_exp_invalid_param)

    if len(args) == 1:
        return Payload(content=await _exp_table_str(bp))

    try:
        level_start, level_end = (
            (1, int(args[1])) if len(args) == 2 else (int(args[1]), int(args[2]))
        )
        assert level_start in constants.pokemon_levels
        assert level_end in constants.pokemon_levels
    except (ValueError, AssertionError):
        return Payload(content=settings.message_exp_invalid_param_2)

    ap_start, ap_end = await _ap_start_end(bp, level_start, level_end)
    exp_diff = await _exp_diff(bp, level_start, level_end)

    data = (pokemon, bp, exp_diff, level_start, ap_start, level_end, ap_end)

    if pokemon:
        # ? currently does not check whether the pokemon can reach the given level
        return Payload(content=settings.message_exp_result_2.format(*data))

    return Payload(content=settings.message_exp_result.format(*data[1:]))


async def _exp_table_str(bp: int) -> str:
    exp_table = db.query_exp(bp)
    desc = (
        f"{settings.message_exp_result_3.format(bp)}\n"
        f"```\n{"\n".join(
            "".join(f"{x:>7}" for x in group)
            for group in itertools.batched(exp_table, 10)
        )}\n```"
        f"{settings.message_exp_result_4.format(bp)}\n"
        f"```\n{"\n".join(
            "".join(f"{(xp1-xp2):>7}" for xp1, xp2 in group)
            for group in itertools.batched(zip(exp_table, [0] + exp_table), 10)
        )}\n```"
    )
    return desc


async def _exp_diff(bp: int, lvl_start: int, lvl_end: int) -> int:
    exp_table = db.query_exp(bp)
    return exp_table[lvl_end - 1] - exp_table[lvl_start - 1]


async def _ap_start_end(bp: int, lvl_start: int, lvl_end: int) -> tuple[int, int]:
    ap_table = db.query_ap(bp)
    return ap_table[lvl_start - 1], ap_table[lvl_end - 1]


async def _get_pokemon_bp(context: KoduckContext, query: str) -> tuple[str, int]:
    pokemon_name = ""
    try:
        query_bp = int(query)
    except ValueError:
        query_pokemon = await lookup_pokemon(context, _query=query)
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return "", 0
        pokemon_ = db.query_pokemon(query_pokemon)
        assert pokemon_
        pokemon_name = pokemon_.pokemon
        query_bp = pokemon_.bp
    return pokemon_name, query_bp
