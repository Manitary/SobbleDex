from typing import Awaitable

import discord
import pytest
from helper import check_payload_equal

import shuffle_commands
from koduck import KoduckContext
from models import Payload


@pytest.mark.asyncio
async def test_no_args(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context)
    expected = Payload(content="I need a Pokemon name to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_pokemon(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await shuffle_commands.farming_cost(context, "1")
    assert real is None


@pytest.mark.asyncio
async def test_pokemon_not_farmable(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "Flygon")
    expected = Payload(content="Flygon cannot be farmed")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_sp_single_skill(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "Arceus")
    embed = discord.Embed(title="Arceus", description="**Stage**: s693")
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Arceus.png"
    )
    embed.add_field(
        name="Double Normal",
        value=(
            "Average: 123 runs ([Coin]x57,980)"
            "\nDRI (estimate): 76 runs ([Coin]x35,890)"
        ),
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_two_skill_diff_cost(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "giratina-o")
    embed = discord.Embed(
        title="Giratina (Origin Forme)", description="**Stage**: Escalation Battle"
    )
    embed.set_thumbnail(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/"
            "Giratina%20%28Origin%20Forme%29.png"
        )
    )
    embed.add_field(
        name="Sinister Power",
        value="Average: 133 runs ([Heart]x133)\nDRI (estimate): 76 runs ([Heart]x76)",
        inline=False,
    )
    embed.add_field(
        name="Cross Attack+",
        value="Average: 160 runs ([Heart]x160)\nDRI (estimate): 91 runs ([Heart]x91)",
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_skills_same_cost(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "mew")
    embed = discord.Embed(title="Mew", description="**Stage**: s265")
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Mew.png"
    )
    embed.add_field(
        name="Barrier Bash+, Block Smash+, Eject+, Power of 4+, Power of 5",
        value="Average: 192 runs ([Heart]x192)\nDRI (estimate): 108 runs ([Heart]x108)",
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_stages(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "Blissey")
    embed = discord.Embed(title="Blissey", description="**Stages**: 493, 645")
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Blissey.png"
    )
    embed.add_field(
        name="Block Smash++, Power of 5",
        value=(
            "Stage: 493\n"
            "Average: 313 runs ([Heart]x313)"
            "\nDRI (estimate): 175 runs ([Heart]x175)"
            "\n\nStage: 645\n"
            "Average: 404 runs ([Heart]x404)"
            "\nDRI (estimate): 226 runs ([Heart]x226)"
        ),
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_stages_main_sp(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "Salamence")
    embed = discord.Embed(title="Salamence", description="**Stages**: 610, s258")
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Salamence.png"
    )
    embed.add_field(
        name="Hitting Streak, Mega Boost",
        value=(
            "Stage: 610\n"
            "Average: 229 runs ([Heart]x229)"
            "\nDRI (estimate): 126 runs ([Heart]x126)"
            "\n\nStage: s258\n"
            "Average: 200 runs ([Coin]x54,170)"
            "\nDRI (estimate): 114 runs ([Coin]x30,950)"
        ),
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
