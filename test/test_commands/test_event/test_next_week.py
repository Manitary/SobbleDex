import datetime

import discord
import pytest
from conftest import WEEK_EMBEDS
from freezegun import freeze_time
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import next_week


@pytest.mark.asyncio
async def test_next_week_no_args(
    context: KoduckContext, week_embed: tuple[int, discord.Embed]
) -> None:
    i, embed = week_embed
    with freeze_time(datetime.datetime(2023, 8, 16) + datetime.timedelta(7 * (i - 1))):
        # 23/08/2023 is in week 1 of the cycle
        real = await next_week(context)
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time(datetime.datetime(2023, 8, 16))
@pytest.mark.asyncio
async def test_next_week_ignore_args(context: KoduckContext) -> None:
    real = await next_week(context, "test", "more", "args", "to", "ignore")
    expected = Payload(embed=WEEK_EMBEDS[0])
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
