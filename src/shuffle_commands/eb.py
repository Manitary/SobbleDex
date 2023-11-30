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
async def eb_details(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | Payload | None:
    assert context.koduck
    assert context.message
    if not args or args[0].isdigit():
        eb_pokemon = utils.current_eb_pokemon()
        args = (eb_pokemon,) + args

    query_level = 0
    if len(args) >= 2:
        query_level = args[1]
        try:
            if int(query_level) <= 0:
                return await context.send_message(
                    content=settings.message_eb_invalid_param,
                )
            query_level = int(query_level)
        except ValueError:
            return await context.send_message(
                content=settings.message_eb_invalid_param,
            )

    # parse params
    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # verify that queried pokemon is in EB table
    eb_details_2 = db.query_eb_pokemon(query_pokemon)
    if not eb_details_2:
        return await context.send_message(
            content=settings.message_eb_no_result.format(query_pokemon),
        )

    # optional level param which will return a stage embed instead
    if query_level <= 0:
        return await context.send_message(
            embed=embed_formatters.format_eb_details_embed(eb_details_2),
        )

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
            eb_reward = f"[{entry.reward}] x{entry.amount} {entry.alternative}"
            break

    user_id = context.message.author.id
    query_history = context.koduck.query_history[user_id]
    query_history[-1] = UserQuery(QueryType.STAGE, (f"s{eb_stage.id}",), kwargs)

    if eb_starting_board:
        return await context.send_message(
            embed=embed_formatters.format_starting_board_embed(eb_stage),
        )

    return await context.send_message(
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
) -> discord.Message | Payload | None:
    kwargs["shorthand"] = True
    return await eb_details(context, *args, **kwargs)


async def eb_rewards(context: KoduckContext, *args: str) -> discord.Message | None:
    if not args:
        query_pokemon = utils.current_eb_pokemon()
    else:
        # parse params
        query_pokemon = await lookup_pokemon(context, _query=args[0])
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return

    # retrieve data
    _eb_rewards = db.query_eb_rewards_pokemon(query_pokemon)
    if not _eb_rewards:
        return await context.send_message(
            content=settings.message_eb_rewards_no_result.format(query_pokemon),
        )

    return await context.send_message(
        embed=embed_formatters.format_eb_rewards_embed(_eb_rewards),
    )
