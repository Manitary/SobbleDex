from typing import Any

import discord

import db
from embed_formatters import format_farming_cost
from koduck import KoduckContext
from models import Payload

from .lookup import lookup_pokemon


async def farming_cost(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload | None:
    pokemon_name = await lookup_pokemon(context, _query=args[0])
    if not pokemon_name:
        return

    farming_stages = db.farming_stages(pokemon_name)
    if not farming_stages:
        return Payload(content=f"{pokemon_name} cannot be farmed")
    farming_stages.sort(key=lambda s: s.string_id)

    pokemon = db.query_pokemon(pokemon_name)
    assert pokemon
    skills = (s for skill in pokemon.all_skills if (s := db.query_skill(skill)))

    return Payload(embed=format_farming_cost(pokemon, farming_stages, skills))
