from typing import Any

import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import Payload, PokemonType

from .decorators import min_param


@min_param(num=1, error=settings.message_type_no_param)
async def type(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    query_type = args[0].capitalize()

    try:
        type_info = db.query_type(PokemonType(query_type))
    except ValueError:
        return Payload(content=settings.message_type_invalid_param)
    return Payload(embed=embed_formatters.format_type_embed(type_info))
