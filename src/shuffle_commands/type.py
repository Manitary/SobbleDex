from typing import Any

import discord

import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import PokemonType

from .decorators import min_param


@min_param(num=1, error=settings.message_type_no_param)
async def type(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    query_type = args[0].capitalize()

    try:
        type_info = db.query_type(PokemonType(query_type))
    except ValueError:
        return await context.send_message(content=settings.message_type_invalid_param)
    return await context.send_message(
        embed=embed_formatters.format_type_embed(type_info),
    )
