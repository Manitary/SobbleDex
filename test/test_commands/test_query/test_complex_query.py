import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import query


@pytest.mark.asyncio
async def test_two_range_conditions_valid(context: KoduckContext) -> None:
    context.params = ["dex<=2", "bp>=40"]
    real = await query(context, **{"dex<": "2", "bp>": "40"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 3 Pokemon with dex<=2 and bp>=40 (sorted by Max AP)"
        )
        .add_field(name="90", value="Bulbasaur (Winking)", inline=False)
        .add_field(name="100", value="Ivysaur", inline=False)
        .add_field(name="125", value="Bulbasaur", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_fixed_conditions_valid(context: KoduckContext) -> None:
    context.params = [
        "type=grass",
        "bp=40",
        "rmls=20",
        "skill=power of 4",
        "ss=mega boost+",
    ]
    real = await query(
        context,
        **{
            "type": "grass",
            "bp": "40",
            "rmls": "20",
            "skill": "power of 4",
            "ss": "mega boost+",
        }
    )
    expected = Payload(
        embed=discord.Embed(
            description=(
                "Found 1 Pokemon with type=Grass and bp=40 and "
                "rmls=20 and skill=power of 4 (sorted by Max AP)"
            )
        ).add_field(name="125", value="Bulbasaur", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_test_mega_and_invalid_sort(context: KoduckContext) -> None:
    context.params = ["maxap>=105", "skill=shot out", "sortby <=bp", "mega"]
    real = await query(
        context, *["mega"], **{"maxap>": "105", "skill": "shot out", "sortby <": "bp"}
    )
    expected = Payload(
        embed=discord.Embed(
            description=(
                "Found 1 Pokemon with mega and maxap>=105 and "
                "skill=shot out (sorted by Max AP)"
            )
        ).add_field(name="110", value="**Mega Rayquaza**", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_parameters_overlapping(context: KoduckContext) -> None:
    context.params = [
        "mega",
        "farmable",
        "skill=eject",
        "!farmable",
        "sortby=bp",
        "maxap>115",
        "sortby=evospeed",
        "type=dark",
    ]
    real = await query(
        context,
        *["mega", "farmable", "!farmable", "maxap>115"],
        **{"skill": "eject", "sortby": "evospeed", "type": "dark"}
    )
    expected = Payload(
        embed=discord.Embed(
            description=(
                "Found 1 Pokemon with mega and not farmable and "
                "skill=eject and sortby=bp and maxap>115 and "
                "sortby=evospeed and type=Dark "
                "(sorted by Mega Evolution Speed)"
            )
        ).add_field(name="9", value="Mega Sharpedo", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_multiple_parameters_overlapping_different_order(
    context: KoduckContext,
) -> None:
    context.params = [
        "mega",
        "!farmable",
        "skill=eject",
        "sortby=bp",
        "farmable",
        "maxap>115",
        "sortby=evospeed",
        "type=dark",
    ]
    real = await query(
        context,
        *["mega", "farmable", "!farmable", "maxap>115"],
        **{"skill": "eject", "sortby": "evospeed", "type": "dark"}
    )
    expected = Payload(
        embed=discord.Embed(
            description=(
                "Found 1 Pokemon with mega and not farmable and "
                "skill=eject and sortby=bp and maxap>115 and "
                "sortby=evospeed and type=Dark "
                "(sorted by Mega Evolution Speed)"
            )
        ).add_field(name="9", value="Mega Sharpedo", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
