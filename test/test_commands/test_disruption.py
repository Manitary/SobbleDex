import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands.disruption import disruption_pattern


@pytest.mark.asyncio
async def test_no_arg(context: KoduckContext) -> None:
    real = await disruption_pattern(context)
    expected = Payload(content="I need a Disruption Pattern index to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_not_int(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "test")
    expected = Payload(
        content="Disruption Pattern index should be a multiple of 6 from 0 to 7260"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_not_mod_6(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "5")
    expected = Payload(
        content="Disruption Pattern index should be a multiple of 6 from 0 to 7260"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_too_low(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "-1")
    expected = Payload(
        content="Disruption Pattern index should be a multiple of 6 from 0 to 7260"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_too_high(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "7266")
    expected = Payload(
        content="Disruption Pattern index should be a multiple of 6 from 0 to 7260"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_arg(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "6")
    embed = discord.Embed()
    embed.set_image(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption%20Patterns/"
            "Pattern%20Index%206.png"
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_arg_min(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "0")
    embed = discord.Embed()
    embed.set_image(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption%20Patterns/"
            "Pattern%20Index%200.png"
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_arg_max(context: KoduckContext) -> None:
    real = await disruption_pattern(context, "7260")
    embed = discord.Embed()
    embed.set_image(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption%20Patterns/"
            "Pattern%20Index%207260.png"
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
