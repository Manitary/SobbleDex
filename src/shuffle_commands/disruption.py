from typing import Any

import discord

import settings
import utils
from koduck import KoduckContext
from models import Payload

from .decorators import min_param


@min_param(num=1, error=settings.message_dp_no_param)
async def disruption_pattern(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload:
    try:
        pattern_id = int(args[0])
        assert (
            pattern_id % 6 == 0
            and settings.disruption_patterns_min_index
            <= pattern_id
            <= settings.disruption_patterns_max_index
        )
    except (ValueError, AssertionError):
        return Payload(
            content=settings.message_dp_invalid_param.format(
                settings.disruption_patterns_min_index,
                settings.disruption_patterns_max_index,
            ),
        )

    embed = discord.Embed()
    embed.set_image(
        url=utils.url_encode(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption Patterns/"
            f"Pattern Index {pattern_id}.png",
        )
    )

    return Payload(embed=embed)
