from typing import Any

import discord

import settings
import utils
from koduck import KoduckContext

from .decorators import min_param


@min_param(num=1, error=settings.message_dp_no_param)
async def disruption_pattern(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    # parse params
    try:
        query_index = int(args[0])
        assert (
            query_index % 6 == 0
            and settings.disruption_patterns_min_index
            <= query_index
            <= settings.disruption_patterns_max_index
        )
    except (ValueError, AssertionError):
        return await context.send_message(
            content=settings.message_dp_invalid_param.format(
                settings.disruption_patterns_min_index,
                settings.disruption_patterns_max_index,
            ),
        )

    embed = discord.Embed()
    embed.set_image(
        url=utils.url_encode(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption Patterns/"
            f"Pattern Index {query_index}.png",
        )
    )
    return await context.send_message(embed=embed)
