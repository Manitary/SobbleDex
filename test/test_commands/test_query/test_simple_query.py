import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import query


@pytest.mark.asyncio
async def test_dex_le_2(context: KoduckContext) -> None:
    context.params = ["dex<=2"]
    real = await query(context, **{"dex<": "2"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 3 Pokemon with dex<=2 (sorted by Max AP)"
        )
        .add_field(name="90", value="Bulbasaur (Winking)", inline=False)
        .add_field(name="100", value="Ivysaur", inline=False)
        .add_field(name="125", value="Bulbasaur", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_dex_out_of_bound(context: KoduckContext) -> None:
    context.params = ["dex>999"]
    real = await query(context, "dex>999")
    expected = Payload(
        embed=discord.Embed(
            description="Found 0 Pokemon with dex>999 (sorted by Max AP)"
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_eq_dragon(context: KoduckContext) -> None:
    context.params = ["type=dragon"]
    real = await query(context, **{"type": "dragon"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 25 Pokemon with type=Dragon (sorted by Max AP)"
        )
        .add_field(
            name="100",
            value="Axew, Bagon, Dratini, Goomy, Jangmo-o, Zygarde (10% Forme)",
            inline=False,
        )
        .add_field(
            name="105",
            value="Dragonair, Drampa, Fraxure, Hakamo-o, Shelgon, Sliggoo",
            inline=False,
        )
        .add_field(name="110", value="Haxorus, Rayquaza", inline=False)
        .add_field(name="115", value="Goodra, Latias, Latios", inline=False)
        .add_field(
            name="120",
            value="Altaria, Druddigon, Zygarde (Complete Forme)",
            inline=False,
        )
        .add_field(name="130", value="Dragonite, Zygarde (50% Forme)", inline=False)
        .add_field(name="145", value="Kommo-o", inline=False)
        .add_field(
            name="150",
            value="Kyurem (Black Kyurem), Kyurem (White Kyurem)",
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_se_normal(context: KoduckContext) -> None:
    context.params = ["se=normal"]
    real = await query(context, **{"se": "normal"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 35 Pokemon with se=Normal (sorted by Max AP)"
        )
        .add_field(name="85", value="Makuhita", inline=False)
        .add_field(name="90", value="Meditite", inline=False)
        .add_field(
            name="100",
            value="Crabrawler, Hawlucha, Mankey, Mienfoo, Pancham, Stufful, Timburr, Tyrogue",
            inline=False,
        )
        .add_field(
            name="105",
            value=(
                "Crabominable, Gurdurr, Hariyama, Hitmonchan, Hitmonlee, Hitmontop, "
                "Machoke, Mienshao, Pangoro, Passimian, Primeape"
            ),
            inline=False,
        )
        .add_field(name="110", value="Bewear, Conkeldurr", inline=False)
        .add_field(name="115", value="Hawlucha (Shiny), Machop", inline=False)
        .add_field(name="116", value="Buzzwole", inline=False)
        .add_field(name="120", value="Sawk, Throh", inline=False)
        .add_field(name="125", value="Machamp, Riolu", inline=False)
        .add_field(
            name="130", value="Gallade, Meloetta (Pirouette Forme)", inline=False
        )
        .add_field(name="135", value="Keldeo (Resolute Form), Medicham", inline=False)
        .add_field(name="140", value="Lucario", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_bp_gt_89(context: KoduckContext) -> None:
    context.params = ["bp>89"]
    real = await query(context, "bp>89")
    expected = Payload(
        embed=discord.Embed(description="Found 8 Pokemon with bp>89 (sorted by Max AP)")
        .add_field(
            name="120",
            value="Hoopa (Hoopa Unbound), Zygarde (Complete Forme)",
            inline=False,
        )
        .add_field(
            name="150",
            value="Arceus, Kyurem (Black Kyurem), Kyurem (White Kyurem), Primal Groudon, Primal Kyogre, Regigigas",
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_rml_eq_7(context: KoduckContext) -> None:
    context.params = ["rml=7"]
    real = await query(context, **{"rml": "7"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 12 Pokemon with rml=7 (sorted by Max AP)"
        )
        .add_field(
            name="111", value="Lunatone, Sandslash, Solrock, Turtonator", inline=False
        )
        .add_field(
            name="116",
            value="Buzzwole, Celesteela, Flygon, Guzzlord, Kartana, Nihilego, Pheromosa, Xurkitree",
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_rmls_eq_7(context: KoduckContext) -> None:
    context.params = ["rmls=7"]
    real = await query(context, **{"rmls": "7"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 12 Pokemon with rmls=7 (sorted by Max AP)"
        )
        .add_field(
            name="111", value="Lunatone, Sandslash, Solrock, Turtonator", inline=False
        )
        .add_field(
            name="116",
            value="Buzzwole, Celesteela, Flygon, Guzzlord, Kartana, Nihilego, Pheromosa, Xurkitree",
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_maxap_gt_149(context: KoduckContext) -> None:
    context.params = ["maxap>149"]
    real = await query(context, "maxap>149")
    expected = Payload(
        embed=discord.Embed(
            description="Found 6 Pokemon with maxap>149 (sorted by Max AP)"
        ).add_field(
            name="150",
            value=(
                "Arceus, Kyurem (Black Kyurem), Kyurem (White Kyurem), "
                "Primal Groudon, Primal Kyogre, Regigigas"
            ),
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_eq_cheer_plus(context: KoduckContext) -> None:
    context.params = ["skill=cheer+"]
    real = await query(context, **{"skill": "cheer+"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 10 Pokemon with skill=Super Cheer (sorted by Max AP)"
        )
        .add_field(name="85", value="Wimpod", inline=False)
        .add_field(name="100", value="**Tyrunt**", inline=False)
        .add_field(
            name="105", value="**Chansey**, **Misdreavus**, **Shiftry**", inline=False
        )
        .add_field(name="115", value="**Vulpix**, **Zorua**", inline=False)
        .add_field(
            name="120", value="**Cleffa**, **Diglett**, **Smeargle**", inline=False
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_with_spaces(context: KoduckContext) -> None:
    context.params = ["skill=power of 5"]
    real = await query(context, **{"skill": "power of 5"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 17 Pokemon with skill=power of 5 (sorted by Max AP)"
        )
        .add_field(
            name="105",
            value="Frogadier, Gastrodon (West Sea), Klang, Noctowl, Slowking",
            inline=False,
        )
        .add_field(
            name="110",
            value="Entei, Gengar, Nidoking, Raikou, Starmie, Suicune",
            inline=False,
        )
        .add_field(name="115", value="Ariados", inline=False)
        .add_field(name="120", value="Throh", inline=False)
        .add_field(name="125", value="Blissey, Excadrill", inline=False)
        .add_field(name="130", value="Mew", inline=False)
        .add_field(name="145", value="Yveltal", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_shorthand(context: KoduckContext) -> None:
    context.params = ["sk=b+"]
    real = await query(context, **{"sk": "b+"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 2 Pokemon with sk=burn+ (sorted by Max AP)"
        )
        .add_field(name="105", value="Castform (Sunny Form)", inline=False)
        .add_field(name="110", value="**Ninetales**", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_eq_not_a_skill(context: KoduckContext) -> None:
    context.params = ["skill=test"]
    real = await query(context, **{"skill": "test"})
    expected = Payload(
        embed=discord.Embed(
            description="Found 0 Pokemon with skill=test (sorted by Max AP)"
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_evospeed_gt_13(context: KoduckContext) -> None:
    context.params = ["evospeed>13"]
    real = await query(context, "evospeed>13")
    expected = Payload(
        embed=discord.Embed(
            description="Found 1 Pokemon with mega and evospeed>13 (sorted by Max AP)"
        ).add_field(name="115", value="Mega Tyranitar", inline=False)
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_mega(context: KoduckContext) -> None:
    context.params = ["mega"]
    real = await query(context, "mega")
    assert isinstance(real, dict)
    assert "embed" in real
    assert real["embed"].description == "Found 63 Pokemon with mega (sorted by Max AP)"


@pytest.mark.asyncio
async def test_farmable(context: KoduckContext) -> None:
    context.params = ["farmable"]
    real = await query(context, "farmable")
    assert isinstance(real, dict)
    assert "embed" in real
    assert (
        real["embed"].description
        == "Found 358 Pokemon with farmable (sorted by Max AP)"
    )


@pytest.mark.asyncio
async def test_farmable_as_param(context: KoduckContext) -> None:
    context.params = ["farmable=yes"]
    real = await query(context, **{"farmable": "yes"})
    assert isinstance(real, dict)
    assert "embed" in real
    assert (
        real["embed"].description
        == "Found 358 Pokemon with farmable (sorted by Max AP)"
    )


@pytest.mark.asyncio
async def test_sortby(context: KoduckContext) -> None:
    context.params = ["sortby=bp"]
    real = await query(context, **{"sortby": "bp"})
    assert isinstance(real, dict)
    assert "embed" in real
    assert (
        real["embed"].description == "Found 1022 Pokemon with sortby=bp (sorted by BP)"
    )


@pytest.mark.asyncio
async def test_ss_not(context: KoduckContext) -> None:
    context.params = ["!ss"]
    real = await query(context, "!ss")
    assert isinstance(real, dict)
    assert "embed" in real
    assert (
        real["embed"].description == "Found 1022 Pokemon with no-SS (sorted by Max AP)"
    )  # ! should it be all of them? seems wrong


@pytest.mark.asyncio
async def test_ss_as_param(context: KoduckContext) -> None:
    context.params = ["ss=yes"]
    real = await query(context, **{"ss": "yes"})
    assert isinstance(real, dict)
    assert "embed" in real
    assert (
        real["embed"].description
        == "Found 1022 Pokemon with only-SS (sorted by Max AP)"
    )  # ! should it be all of them? seems wrong
