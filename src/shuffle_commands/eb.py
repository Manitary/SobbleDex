from typing import Any

import discord

import db
import embed_formatters
import settings
import utils
from koduck import KoduckContext
from models import Payload, QueryType, StageType, UserQuery

from .decorators import allow_space_delimiter
from .lookup import lookup_pokemon


@allow_space_delimiter()
async def eb_details(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    assert context.koduck
    assert context.message
    if not args or args[0].isdigit():
        eb_pokemon = utils.current_eb_pokemon()
        args = (eb_pokemon,) + args

    query_level = 0
    if len(args) >= 2:
        query_level = args[1]
        try:
            query_level = int(query_level)
            assert query_level > 0
        except (ValueError, AssertionError):
            return Payload(content=settings.message_eb_invalid_param)

    # parse params
    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return Payload()

    # verify that queried pokemon is in EB table
    eb_details_2 = db.query_eb_pokemon(query_pokemon)
    if not eb_details_2:
        return Payload(content=settings.message_eb_no_result.format(query_pokemon))

    # no level param = return the eb info embed
    if not query_level:
        return Payload(embed=embed_formatters.format_eb_details_embed(eb_details_2))

    # optional level param = return a stage embed
    leg = next(x for x in eb_details_2 if x.end_level < 0 or x.end_level > query_level)

    # extra string to show level range of this eb stage
    if leg.start_level == leg.end_level - 1:
        level_range = f" (Level {leg.start_level})"
    elif leg.end_level < 0:
        level_range = f" (Levels {leg.start_level}+ ({query_level}))"
    else:
        level_range = (
            f" (Levels {leg.start_level} to {leg.end_level-1} ({query_level}))"
        )

    shorthand = kwargs.get("shorthand", False)
    eb_starting_board = kwargs.get("startingboard", False)

    eb_stage = db.query_stage_by_index(leg.stage_index, StageType.EVENT)
    _eb_rewards = db.query_eb_rewards_pokemon(query_pokemon)
    eb_reward = ""
    for entry in _eb_rewards:
        if entry.level == query_level:
            eb_reward = f"[{entry.reward}] x{entry.amount}" + (
                f" {entry.alternative}" if entry.alternative else ""
            )
            break

    user_id = context.message.author.id
    query_history = context.koduck.query_history[user_id]
    query_history[-1] = UserQuery(QueryType.STAGE, (f"s{eb_stage.id}",), kwargs)

    if eb_starting_board:
        # ! can this ever be reached?
        # (i.e. how do you pass asking for just the starting board to an eb?)
        return Payload(embed=embed_formatters.format_starting_board_embed(eb_stage))

    return Payload(
        embed=embed_formatters.format_stage_embed(
            eb_stage,
            eb_data=(
                level_range,
                query_level - leg.start_level,
                eb_reward,
                query_level,
            ),
            shorthand=shorthand,
        ),
    )


async def eb_details_shorthand(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload:
    kwargs["shorthand"] = True
    payload = await eb_details(context, *args, **kwargs)
    assert isinstance(payload, dict)
    return payload


async def eb_rewards(context: KoduckContext, *args: str) -> Payload:
    if not args:
        query_pokemon = utils.current_eb_pokemon()
    else:
        query_pokemon = await lookup_pokemon(context, _query=args[0])

    if not query_pokemon:
        print("Unrecognized Pokemon")
        return Payload()

    _eb_rewards = db.query_eb_rewards_pokemon(query_pokemon)
    if not _eb_rewards:
        return Payload(
            content=settings.message_eb_rewards_no_result.format(query_pokemon),
        )

    return Payload(embed=embed_formatters.format_eb_rewards_embed(_eb_rewards))
