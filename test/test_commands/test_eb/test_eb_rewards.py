import datetime
from typing import Awaitable

import discord
import pytest
from freezegun import freeze_time
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands.eb import eb_rewards


@pytest.mark.asyncio
async def test_eb_rewards_pokemon_no_eb(context: KoduckContext) -> None:
    real = await eb_rewards(context, "kabuto")
    expected = Payload(
        content="Could not find an Escalation Battles with the Pokemon 'Kabuto'"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_rewards_invalid_pokemon(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await eb_rewards(context, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_rewards_no_args(
    context: KoduckContext, eb_rewards_embed: tuple[int, discord.Embed]
) -> None:
    i, embed = eb_rewards_embed
    with freeze_time(datetime.datetime(2023, 8, 23) + datetime.timedelta(7 * (i - 1))):
        # 23/08/2023 is in week 1 of the cycle
        real = await eb_rewards(context)
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_rewards_by_name(
    context: KoduckContext, eb_rewards_embed: tuple[int, discord.Embed]
) -> None:
    _, embed = eb_rewards_embed
    assert embed.title
    pokemon_name = embed.title.split(" Escalation")[0]
    real = await eb_rewards(context, pokemon_name)
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
