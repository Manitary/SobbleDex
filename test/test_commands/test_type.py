import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands
from koduck import KoduckContext
from models import Payload


@pytest.mark.asyncio
async def test_type_no_arg(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context)
    expected = Payload(content="I need a Type to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_invalid_type(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "fre")
    expected = Payload(content="That's not a valid type")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_normal(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "normal")
    embed = discord.Embed(title="Normal", color=11053176)
    embed.add_field(name="Super Effective Against", value="None")
    embed.add_field(name="Not Very Effective Against", value="Rock, Ghost, Steel")
    embed.add_field(name="Weaknesses", value="Fighting")
    embed.add_field(name="Resistances", value="Ghost")
    embed.add_field(name="Status Effect Immunities", value="None")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_fire(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "fire")
    embed = discord.Embed(title="Fire", color=15761456)
    embed.add_field(name="Super Effective Against", value="Grass, Ice, Bug, Steel")
    embed.add_field(
        name="Not Very Effective Against", value="Fire, Water, Rock, Dragon"
    )
    embed.add_field(name="Weaknesses", value="Water, Ground, Rock")
    embed.add_field(name="Resistances", value="Fire, Grass, Ice, Bug, Steel, Fairy")
    embed.add_field(name="Status Effect Immunities", value="Burned, Frozen")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_water(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "water")
    embed = discord.Embed(title="Water", color=6852848)
    embed.add_field(name="Super Effective Against", value="Fire, Ground, Rock")
    embed.add_field(name="Not Very Effective Against", value="Water, Grass, Dragon")
    embed.add_field(name="Weaknesses", value="Grass, Electric")
    embed.add_field(name="Resistances", value="Fire, Water, Ice, Steel")
    embed.add_field(name="Status Effect Immunities", value="Burned")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_grass(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "grass")
    embed = discord.Embed(title="Grass", color=7915600)
    embed.add_field(name="Super Effective Against", value="Water, Ground, Rock")
    embed.add_field(
        name="Not Very Effective Against",
        value="Fire, Grass, Poison, Flying, Bug, Dragon, Steel",
    )
    embed.add_field(name="Weaknesses", value="Fire, Ice, Poison, Flying, Bug")
    embed.add_field(name="Resistances", value="Water, Grass, Electric, Ground")
    embed.add_field(name="Status Effect Immunities", value="Spooked, Asleep")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_electric(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "electric")
    embed = discord.Embed(title="Electric", color=16306224)
    embed.add_field(name="Super Effective Against", value="Water, Flying")
    embed.add_field(
        name="Not Very Effective Against", value="Grass, Electric, Ground, Dragon"
    )
    embed.add_field(name="Weaknesses", value="Ground")
    embed.add_field(name="Resistances", value="Electric, Flying, Steel")
    embed.add_field(name="Status Effect Immunities", value="Frozen, Paralyzed")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_ice(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "ice")
    embed = discord.Embed(title="Ice", color=10016984)
    embed.add_field(
        name="Super Effective Against", value="Grass, Ground, Flying, Dragon"
    )
    embed.add_field(name="Not Very Effective Against", value="Fire, Water, Ice, Steel")
    embed.add_field(name="Weaknesses", value="Fire, Fighting, Rock, Steel")
    embed.add_field(name="Resistances", value="Ice")
    embed.add_field(name="Status Effect Immunities", value="Frozen, Spooked, Asleep")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_fighting(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "fighting")
    embed = discord.Embed(title="Fighting", color=12595240)
    embed.add_field(
        name="Super Effective Against", value="Normal, Ice, Rock, Dark, Steel"
    )
    embed.add_field(
        name="Not Very Effective Against",
        value="Poison, Flying, Psychic, Bug, Ghost, Fairy",
    )
    embed.add_field(name="Weaknesses", value="Flying, Psychic, Fairy")
    embed.add_field(name="Resistances", value="Bug, Rock, Dark")
    embed.add_field(name="Status Effect Immunities", value="Frozen, Spooked, Asleep")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_poison(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "poison")
    embed = discord.Embed(title="Poison", color=10502304)
    embed.add_field(name="Super Effective Against", value="Grass, Fairy")
    embed.add_field(
        name="Not Very Effective Against", value="Poison, Ground, Rock, Ghost, Steel"
    )
    embed.add_field(name="Weaknesses", value="Ground, Psychic")
    embed.add_field(name="Resistances", value="Grass, Fighting, Poison, Bug, Fairy")
    embed.add_field(
        name="Status Effect Immunities",
        value="Burned, Frozen, Spooked, Poisoned, Paralyzed",
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_ground(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "ground")
    embed = discord.Embed(title="Ground", color=14729320)
    embed.add_field(
        name="Super Effective Against", value="Fire, Electric, Poison, Rock, Steel"
    )
    embed.add_field(name="Not Very Effective Against", value="Grass, Flying, Bug")
    embed.add_field(name="Weaknesses", value="Water, Grass, Ice")
    embed.add_field(name="Resistances", value="Electric, Poison, Rock")
    embed.add_field(name="Status Effect Immunities", value="Burned, Spooked, Poisoned")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_flying(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "flying")
    embed = discord.Embed(title="Flying", color=11047152)
    embed.add_field(name="Super Effective Against", value="Grass, Fighting, Bug")
    embed.add_field(name="Not Very Effective Against", value="Electric, Rock, Steel")
    embed.add_field(name="Weaknesses", value="Electric, Ice, Rock")
    embed.add_field(name="Resistances", value="Grass, Fighting, Ground, Bug")
    embed.add_field(name="Status Effect Immunities", value="Paralyzed")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_psychic(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "psychic")
    embed = discord.Embed(title="Psychic", color=16275592)
    embed.add_field(name="Super Effective Against", value="Fighting, Poison")
    embed.add_field(name="Not Very Effective Against", value="Psychic, Dark, Steel")
    embed.add_field(name="Weaknesses", value="Bug, Ghost, Dark")
    embed.add_field(name="Resistances", value="Fighting, Psychic")
    embed.add_field(name="Status Effect Immunities", value="Frozen, Paralyzed")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_bug(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "bug")
    embed = discord.Embed(title="Bug", color=11057184)
    embed.add_field(name="Super Effective Against", value="Grass, Psychic, Dark")
    embed.add_field(
        name="Not Very Effective Against",
        value="Fire, Fighting, Poison, Flying, Ghost, Steel, Fairy",
    )
    embed.add_field(name="Weaknesses", value="Fire, Flying, Rock")
    embed.add_field(name="Resistances", value="Grass, Fighting, Ground")
    embed.add_field(name="Status Effect Immunities", value="Spooked")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_rock(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "rock")
    embed = discord.Embed(title="Rock", color=12099640)
    embed.add_field(name="Super Effective Against", value="Fire, Ice, Flying, Bug")
    embed.add_field(name="Not Very Effective Against", value="Fighting, Ground, Steel")
    embed.add_field(name="Weaknesses", value="Water, Grass, Fighting, Ground, Steel")
    embed.add_field(name="Resistances", value="Normal, Fire, Poison, Flying")
    embed.add_field(
        name="Status Effect Immunities", value="Burned, Spooked, Poisoned, Asleep"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_ghost(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "ghost")
    embed = discord.Embed(title="Ghost", color=7362712)
    embed.add_field(name="Super Effective Against", value="Psychic, Ghost")
    embed.add_field(name="Not Very Effective Against", value="Normal, Dark")
    embed.add_field(name="Weaknesses", value="Ghost, Dark")
    embed.add_field(name="Resistances", value="Normal, Fighting, Poison, Bug")
    embed.add_field(
        name="Status Effect Immunities",
        value="Burned, Frozen, Poisoned, Asleep, Paralyzed",
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_dragon(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "dragon")
    embed = discord.Embed(title="Dragon", color=7354616)
    embed.add_field(name="Super Effective Against", value="Dragon")
    embed.add_field(name="Not Very Effective Against", value="Steel, Fairy")
    embed.add_field(name="Weaknesses", value="Ice, Fairy, Dragon")
    embed.add_field(name="Resistances", value="Fire, Water, Grass, Electric")
    embed.add_field(
        name="Status Effect Immunities", value="Burned, Spooked, Asleep, Paralyzed"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_dark(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "dark")
    embed = discord.Embed(title="Dark", color=7362632)
    embed.add_field(name="Super Effective Against", value="Psychic, Ghost")
    embed.add_field(name="Not Very Effective Against", value="Fighting, Dark, Fairy")
    embed.add_field(name="Weaknesses", value="Fighting, Bug, Fairy")
    embed.add_field(name="Resistances", value="Psychic, Ghost, Dark")
    embed.add_field(name="Status Effect Immunities", value="Asleep, Spooked")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_steel(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "steel")
    embed = discord.Embed(title="Steel", color=12105936)
    embed.add_field(name="Super Effective Against", value="Ice, Rock, Fairy")
    embed.add_field(
        name="Not Very Effective Against", value="Fire, Water, Electric, Steel"
    )
    embed.add_field(name="Weaknesses", value="Fire, Fighting, Ground")
    embed.add_field(
        name="Resistances",
        value="Normal, Grass, Ice, Poison, Flying, Psychic, Bug, Rock, Dragon, Steel, Fairy",
    )
    embed.add_field(
        name="Status Effect Immunities",
        value="Frozen, Spooked, Poisoned, Asleep, Paralyzed",
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_fairy(context: KoduckContext) -> None:
    real = await shuffle_commands.type(context, "fairy")
    embed = discord.Embed(title="Fairy", color=15636908)
    embed.add_field(name="Super Effective Against", value="Fighting, Dragon, Dark")
    embed.add_field(name="Not Very Effective Against", value="Fire, Poison, Steel")
    embed.add_field(name="Weaknesses", value="Poison, Steel")
    embed.add_field(name="Resistances", value="Fighting, Bug, Dragon, Dark")
    embed.add_field(name="Status Effect Immunities", value="Frozen, Paralyzed")
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
