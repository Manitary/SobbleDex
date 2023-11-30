from typing import Any

import discord

import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import StageType

from .lookup import lookup_pokemon
from .stage import latest_stage_query


async def pokemon(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    if not args:
        return await last_stage_pokemon(context)
    # parse params
    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # retrieve data
    pokemon_ = db.query_pokemon(query_pokemon)
    if not pokemon_:
        return await context.send_message(
            content=settings.message_pokemon_no_result.format(query_pokemon),
        )

    return await context.send_message(
        embed=embed_formatters.format_pokemon_embed(pokemon_),
    )


async def last_stage_pokemon(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    query_ = await latest_stage_query(context)
    if not query_:
        return await context.send_message(
            content=settings.message_no_previous_stage,
        )

    if not query_.args:
        return await context.send_message(content=settings.message_last_query_error)

    last_stage_id = query_.args[0]
    assert isinstance(last_stage_id, str)

    if last_stage_id.startswith("ex"):
        pokemon_ = db.query_stage_by_index(
            int(last_stage_id[2:]), StageType.EXPERT
        ).pokemon
    elif last_stage_id.startswith("s"):
        pokemon_ = db.query_stage_by_index(
            int(last_stage_id[1:]), StageType.EVENT
        ).pokemon
    elif last_stage_id.isdigit():
        pokemon_ = db.query_stage_by_index(int(last_stage_id), StageType.MAIN).pokemon
    else:
        return await context.send_message(content=settings.message_last_query_error)

    return await pokemon(context, pokemon_)
