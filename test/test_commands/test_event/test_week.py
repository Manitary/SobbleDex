import datetime
from typing import Awaitable

import discord
import pytest
from conftest import WEEK_EMBEDS
from freezegun import freeze_time
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import week


@pytest.mark.asyncio
async def test_pokemon_no_event(context: KoduckContext) -> None:
    real = await week(context, "Aerodactyl")  # Not an event pokemon
    expected = Payload(content="Could not find an event with the Pokemon 'Aerodactyl'")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_pokemon_with_event(context: KoduckContext) -> None:
    real = await week(context, "Salazzle")  # Week 7 event
    expected = Payload(embed=WEEK_EMBEDS[6])
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_pokemon_invalid(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await week(context, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.parametrize("week_num", range(1, 25))
@pytest.mark.asyncio
async def test_pokemon_with_multiple_events(
    context: KoduckContext, week_num: int
) -> None:
    with freeze_time(
        datetime.datetime(2023, 8, 23) + datetime.timedelta(7 * (week_num - 1))
    ):
        # 23/08/2023 is in week 1 of the cycle
        real = await week(context, "tornadus-i")
    # Tornadus-I appears in weeks 2, 10, 18
    expected_week = 10 if 2 < week_num <= 10 else 18 if 9 < week_num <= 18 else 2
    expected = Payload(embed=WEEK_EMBEDS[expected_week - 1])
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_week_by_number(
    context: KoduckContext, week_embed: tuple[int, discord.Embed]
) -> None:
    i, embed = week_embed
    real = await week(context, str(i))
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.parametrize("week_num", (0, 25))
@pytest.mark.asyncio
async def test_week_out_of_bound(context: KoduckContext, week_num: int) -> None:
    real = await week(context, str(week_num))
    expected = Payload(
        content="There are 24 weeks of events in the event rotation, so I need a number from 1 to 24"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_week_no_args(
    context: KoduckContext, week_embed: tuple[int, discord.Embed]
) -> None:
    i, embed = week_embed
    with freeze_time(datetime.datetime(2023, 8, 23) + datetime.timedelta(7 * (i - 1))):
        # 23/08/2023 is in week 1 of the cycle
        real = await week(context)
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
