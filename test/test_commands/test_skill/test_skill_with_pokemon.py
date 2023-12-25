from typing import Any, Awaitable

import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands.lookup
from koduck import KoduckContext
from models import Payload
from shuffle_commands import skill_with_pokemon
from shuffle_commands.skill import skill_with_pokemon_with_emojis

EMBED_BASE = {
    "title": "Mind Zap",
    "colour": 16711680,
    "description": (
        "**Description**: Delays your opponent's disruptions."
        "\n**Notes**: Resets disruption counter to max;"
        " Can't trigger if a status effect is already present"
        "\n**Activation Rates**: 10% / 40% / 100%"
        "\n**Damage Multiplier**: x1.00"
        "\n**SL2 Bonus**: +5% (15% / 45% / 100%)"
        "\n**SL3 Bonus**: +10% (20% / 50% / 100%)"
        "\n**SL4 Bonus**: +20% (30% / 60% / 100%)"
        "\n**SL5 Bonus**: +25% (35% / 65% / 100%)"
        "\n**SP Requirements**: 5 => 15 => 20 => 60 (Total: 100)"
    ),
}


@pytest.mark.asyncio
async def test_skill_no_args(context: KoduckContext) -> None:
    real = await skill_with_pokemon(context)
    expected = Payload(content="I need a Skill name to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_invalid_arg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await skill_with_pokemon(context, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_invalid_skill_name(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def choose_zero(*args: Any, **kwargs: Any) -> int:
        return 0

    monkeypatch.setattr(shuffle_commands.lookup, "choice_react", choose_zero)
    real = await skill_with_pokemon(context, "Dugtrio")
    expected = Payload(
        content="Could not find a Skill entry with the name 'Dugtrio (Alola Form)'"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill(context: KoduckContext, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: **Abomasnow**\\*, Kecleon, Musharna"
                "\n**110**: Bellossom\\*, **Entei**, **Gardevoir**\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_with_emoji(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon_with_emojis(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill sorted by Max AP",
            value=(
                "\n**85**: [Burmy (Plant Cloak)][Weedle]"
                "\n**90**: [Foongus][Shuppet]\\*[Slakoth]"
                "\n**100**: [Lileep][Staravia]([Trubbish])[Unown (Question)]"
                "\n**105**: ([Abomasnow])\\*[Kecleon][Musharna]"
                "\n**110**: [Bellossom]\\*([Entei])([Gardevoir])\\*[Gorebyss]"
                "\n**115**: [Pikachu (Enamored)]"
                "\n**120**: [Audino (Winking)]\\*[Jellicent (Female)]"
                "\n**125**: [Greninja][Uxie]\\*"
                "\n**130**: [Ludicolo]"
                "\n**135**: [Absol]"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_farmable(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "farmable")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (farmable) sorted by Max AP",
            value=(
                "\n**90**: Shuppet\\*"
                "\n**105**: **Abomasnow**\\*"
                "\n**110**: Bellossom\\*, **Gardevoir**\\*"
                "\n**120**: Audino (Winking)\\*"
                "\n**125**: Uxie\\*"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_not_farmable(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "!farmable")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (not farmable) sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: Kecleon, Musharna"
                "\n**110**: **Entei**, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Jellicent (Female)"
                "\n**125**: Greninja"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_farmable_using_kwarg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    monkeypatch.setattr(context, "kwargs", {"farmable": "yes"})
    real = await skill_with_pokemon(context, "mindzap", **context.kwargs)
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (farmable) sorted by Max AP",
            value=(
                "\n**90**: Shuppet\\*"
                "\n**105**: **Abomasnow**\\*"
                "\n**110**: Bellossom\\*, **Gardevoir**\\*"
                "\n**120**: Audino (Winking)\\*"
                "\n**125**: Uxie\\*"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_not_farmable_using_kwarg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    monkeypatch.setattr(context, "kwargs", {"farmable": "no"})
    real = await skill_with_pokemon(context, "mindzap", **context.kwargs)
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (not farmable) sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: Kecleon, Musharna"
                "\n**110**: **Entei**, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Jellicent (Female)"
                "\n**125**: Greninja"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_farmable_both(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "?farmable")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: **Abomasnow**\\*, Kecleon, Musharna"
                "\n**110**: Bellossom\\*, **Entei**, **Gardevoir**\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_farmable_both_using_kwarg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    monkeypatch.setattr(context, "kwargs", {"farmable": "both"})
    real = await skill_with_pokemon(context, "mindzap", **context.kwargs)
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: **Abomasnow**\\*, Kecleon, Musharna"
                "\n**110**: Bellossom\\*, **Entei**, **Gardevoir**\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_ss(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "ss")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (only-SS) sorted by Max AP",
            value=(
                "\n**100**: **Trubbish**"
                "\n**105**: **Abomasnow**\\*"
                "\n**110**: **Entei**, **Gardevoir**\\*"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_ss_using_kwarg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    monkeypatch.setattr(context, "kwargs", {"ss": "yes"})
    real = await skill_with_pokemon(context, "mindzap", **context.kwargs)
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (only-SS) sorted by Max AP",
            value=(
                "\n**100**: **Trubbish**"
                "\n**105**: **Abomasnow**\\*"
                "\n**110**: **Entei**, **Gardevoir**\\*"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_no_ss(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "!ss")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (no-SS) sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, Unown (Question)"
                "\n**105**: Kecleon, Musharna"
                "\n**110**: Bellossom\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_no_ss_using_kwarg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    monkeypatch.setattr(context, "kwargs", {"ss": "no"})
    real = await skill_with_pokemon(context, "mindzap", **context.kwargs)
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (no-SS) sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, Unown (Question)"
                "\n**105**: Kecleon, Musharna"
                "\n**110**: Bellossom\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_sort_by_evospeed(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "sortby=evospeed"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name=(
                "Pokemon with this skill (mega and sortby=evospeed)"
                " sorted by Mega Evolution Speed"
            ),
            value=(
                "\n**6**: **Mega Abomasnow**, **Mega Gardevoir**"
                "\n**7**: Mega Audino (Winking)"
                "\n**10**: Mega Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_filter_by_evospeed(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "evospeed<=8"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name=("Pokemon with this skill (mega and evospeed<=8) sorted by Max AP"),
            value=(
                "\n**105**: **Mega Abomasnow**"
                "\n**110**: **Mega Gardevoir**"
                "\n**120**: Mega Audino (Winking)"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_has_mega(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap"])
    real = await skill_with_pokemon(context, "mindzap", "hasmega")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (hasmega) sorted by Max AP",
            value=(
                "\n**105**: **Abomasnow**\\*"
                "\n**110**: **Gardevoir**\\*"
                "\n**120**: Audino (Winking)\\*"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_ignore_incomplete_query_param(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "maxap<="])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill sorted by Max AP",
            value=(
                "\n**85**: Burmy (Plant Cloak), Weedle"
                "\n**90**: Foongus, Shuppet\\*, Slakoth"
                "\n**100**: Lileep, Staravia, **Trubbish**, Unown (Question)"
                "\n**105**: **Abomasnow**\\*, Kecleon, Musharna"
                "\n**110**: Bellossom\\*, **Entei**, **Gardevoir**\\*, Gorebyss"
                "\n**115**: Pikachu (Enamored)"
                "\n**120**: Audino (Winking)\\*, Jellicent (Female)"
                "\n**125**: Greninja, Uxie\\*"
                "\n**130**: Ludicolo"
                "\n**135**: Absol"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_query_no_hits(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "maxap<80"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (maxap<80)",
            value="None",
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_sortby_bp(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "sortby=bp"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (sortby=bp) sorted by BP",
            value=(
                "\n**30**: Burmy (Plant Cloak), Weedle"
                "\n**40**: Foongus, Shuppet\\*, Slakoth"
                "\n**50**: Audino (Winking)\\*, Lileep, Pikachu (Enamored),"
                " Staravia, **Trubbish**, Unown (Question)"
                "\n**60**: **Abomasnow**\\*, Absol, Jellicent (Female), Kecleon, Musharna"
                "\n**70**: Bellossom\\*, **Entei**, **Gardevoir**\\*, Gorebyss,"
                " Greninja, Ludicolo, Uxie\\*"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_sortby_type(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(context, "params", ["mindzap", "sortby=type"])
    real = await skill_with_pokemon(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(**EMBED_BASE).add_field(
            name="Pokemon with this skill (sortby=type) sorted by Type",
            value=(
                "\n**Bug**: Burmy (Plant Cloak)"
                "\n**Dark**: Absol"
                "\n**Electric**: Pikachu (Enamored)"
                "\n**Fairy**: **Gardevoir**\\*"
                "\n**Fire**: **Entei**"
                "\n**Flying**: Staravia"
                "\n**Ghost**: Jellicent (Female), Shuppet\\*"
                "\n**Grass**: Bellossom\\*, Foongus, Ludicolo"
                "\n**Ice**: **Abomasnow**\\*"
                "\n**Normal**: Audino (Winking)\\*, Kecleon, Slakoth"
                "\n**Poison**: **Trubbish**, Weedle"
                "\n**Psychic**: Musharna, Unown (Question), Uxie\\*"
                "\n**Rock**: Lileep"
                "\n**Water**: Gorebyss, Greninja"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
