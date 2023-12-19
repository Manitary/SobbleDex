from typing import Any

import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands
from koduck import KoduckContext
from models import Payload


async def do_nothing(*args: Any, **kwargs: Any) -> None:
    return


@pytest.mark.asyncio
async def test_invalid_pokemon(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await shuffle_commands.farming_cost(context, "1")
    expected = None
    assert real == expected


@pytest.mark.asyncio
async def test_pokemon_not_farmable(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "Flygon")
    expected = Payload(content="Flygon cannot be farmed")
    assert real == expected


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
            "Average: 123 runs ([Coin]x61,500)"
            "\nDRI (estimate): 76 runs ([Coin]x38,000)"
        ),
        inline=False,
    )
    expected = Payload(embed=embed)
    assert real == expected


@pytest.mark.asyncio
async def test_two_skill_diff_cost(context: KoduckContext) -> None:
    real = await shuffle_commands.farming_cost(context, "giratina-o")
    embed = discord.Embed(
        title="Giratina (Origin Forme)", description="**Stage**: Escalation Battle"
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Giratina%20%28Origin%20Forme%29.png"
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
    assert real
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
    assert real
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
    assert real
    check_payload_equal(real, expected)
