from typing import Any

import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import Payload, StageType

from .lookup import lookup_pokemon
from .stage import latest_stage_query


async def pokemon(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    if not args:
        return await _last_stage_pokemon(context)
    # parse params
    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return Payload()

    # retrieve data
    pokemon_ = db.query_pokemon(query_pokemon)
    if not pokemon_:
        # ? This happens when looking up a name that is used as an alias
        # ? If the original name is not a valid pokemon, this is the path taken
        # ? e.g. `?p spookify+` -> prompt `spook+ (Spookify+)` alias choice -> no such pokemon
        return Payload(content=settings.message_pokemon_no_result.format(query_pokemon))

    return Payload(embed=embed_formatters.format_pokemon_embed(pokemon_))


async def _last_stage_pokemon(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload:
    query_ = await latest_stage_query(context)
    if not query_:
        return Payload(content=settings.message_no_previous_stage)

    if not query_.args:
        return Payload(content=settings.message_last_query_error)

    last_stage_id = query_.args[0]
    assert isinstance(last_stage_id, str)

    if last_stage_id.startswith("ex") and last_stage_id[2:].isdigit():
        pokemon_ = db.query_stage_by_index(
            int(last_stage_id[2:]), StageType.EXPERT
        ).pokemon
    elif last_stage_id.startswith("s") and last_stage_id[1:].isdigit():
        pokemon_ = db.query_stage_by_index(
            int(last_stage_id[1:]), StageType.EVENT
        ).pokemon
    elif last_stage_id.isdigit():
        pokemon_ = db.query_stage_by_index(int(last_stage_id), StageType.MAIN).pokemon
    else:
        return Payload(content=settings.message_last_query_error)

    return await pokemon(context, pokemon_)
