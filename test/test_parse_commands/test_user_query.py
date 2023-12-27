from typing import AsyncIterator

import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext, on_message
from models import Payload

type CtxData = tuple[str, str, list[str], list[str], dict[str, str]]
type Context_Payloads = tuple[KoduckContext, list[Payload], list[CtxData]]


@pytest.mark.asyncio
async def test_on_message(context_archive: AsyncIterator[Context_Payloads]) -> None:
    context, archive, context_data = await anext(context_archive)
    assert context.message
    context.message.content = "?query rmls=7"
    await on_message(context.message)

    real = archive[-1]
    command, params, parsed_params, args, kwargs = context_data[-1]

    expected = Payload(
        content="",
        embed=discord.Embed(
            description="Found 12 Pokemon with rmls=7 (sorted by Max AP)"
        )
        .add_field(
            name="111", value="Lunatone, Sandslash, Solrock, Turtonator", inline=False
        )
        .add_field(
            name="116",
            value="Buzzwole, Celesteela, Flygon, Guzzlord, Kartana, Nihilego, Pheromosa, Xurkitree",
            inline=False,
        ),
    )

    check_payload_equal(real, expected)
    assert command == "query"
    assert params == "rmls=7"
    assert parsed_params == ["rmls=7"]
    assert args == []
    assert kwargs == {"rmls": "7"}
