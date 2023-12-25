import datetime
from typing import Awaitable

import discord
import pytest
from freezegun import freeze_time
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload, QueryType, UserQuery
from shuffle_commands.eb import eb_details, eb_details_shorthand


@pytest.mark.asyncio
async def test_eb_invalid_arg(
    context_with_fake_message: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    monkeypatch.setattr(context_with_fake_message, "send_message", do_nothing)
    real = await eb_details(context_with_fake_message, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_pokemon_no_eb(context_with_fake_message: KoduckContext) -> None:
    real = await eb_details(context_with_fake_message, "kabuto")
    expected = Payload(
        content="Could not find an Escalation Battles with the Pokemon 'Kabuto'"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_no_pokemon_invalid_level(
    context_with_fake_message: KoduckContext,
) -> None:
    real = await eb_details(context_with_fake_message, "0")
    expected = Payload(content="EB level should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_pokemon_invalid_level_with_space(
    context_with_fake_message: KoduckContext,
) -> None:
    real = await eb_details(context_with_fake_message, "primarina 0")
    expected = Payload(content="EB level should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_pokemon_invalid_level(
    context_with_fake_message: KoduckContext,
) -> None:
    real = await eb_details(context_with_fake_message, "primarina", "-1")
    expected = Payload(content="EB level should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_pokemon_level_not_int(
    context_with_fake_message: KoduckContext,
) -> None:
    real = await eb_details(context_with_fake_message, "primarina", "test")
    expected = Payload(content="EB level should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_no_args(
    context_with_fake_message: KoduckContext,
    eb_details_embed: tuple[int, discord.Embed],
) -> None:
    i, embed = eb_details_embed
    with freeze_time(datetime.datetime(2023, 8, 23) + datetime.timedelta(7 * (i - 1))):
        # 23/08/2023 is in week 1 of the cycle
        real = await eb_details(context_with_fake_message)
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_with_level_in_leg(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.ANY, tuple())]},
    )
    real = await eb_details(context_with_fake_message, "primarina 1")
    embed = (
        discord.Embed(
            title="Event Stage 669: Primarina [Primarina] (Levels 1 to 15 (1))",
            colour=6852848,
            description=(
                "**HP**: 1211 + 242 (1211)\n**Moves**: 8\n"
                "**Damage/move**: 152 ([M+5] 94)\n**Experience**: 5\n**Catchability**: 1%\n"
                "**Default Supports**: [Buneary][Happiny][Minccino][Meowth]\n"
                "**Rank Requirements**: 0 / 0 / 0\n"
                "**Attempt Cost**: [Heart] x1\n**Drop Items**: [PSB] / [PSB] / [PSB]\n"
                "**Drop Rates**: 25.0% / 25.0% / 25.0%\n**Items**: [M+5][EXP][MS][C-1][DD][APU]\n"
                "**EB stage clear reward**: [EBS] x1"
            ),
        )
        .add_field(
            name="**Countdown 1**",
            value=(
                "Start counter at 0. Switch to cd2 after 2 disrupts. "
                "Choose one of these every 3 moves:\n- 6x2 area at A3 ([Primarina] x4)"
            ),
            inline=False,
        )
        .add_field(
            name="**Countdown 2**",
            value="Choose one of these every 3 moves:\n- Random 6x2 area ([Primarina] x3)",
            inline=False,
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_with_level_boss_stage(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.ANY, tuple())]},
    )
    real = await eb_details(context_with_fake_message, "primarina 50")
    embed = (
        discord.Embed(
            title="Event Stage 673: Primarina [Primarina] (Level 50)",
            colour=6852848,
            description=(
                "**HP**: 23022\n**Moves**: 16\n"
                "**Damage/move**: 1439 ([M+5] 1097)\n**Experience**: 5\n**Catchability**: 50%\n"
                "**Default Supports**: [Buneary][Happiny][Minccino][Meowth]\n"
                "**Rank Requirements**: 0 / 0 / 0\n"
                "**Attempt Cost**: [Heart] x1\n**Drop Items**: [PSB] / [PSB] / [PSB]\n"
                "**Drop Rates**: 25.0% / 25.0% / 25.0%\n**Items**: [M+5][EXP][MS][C-1][DD][APU]\n"
                "**EB stage clear reward**: [RML] x1"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%202419.png"
            ),
        )
        .add_field(
            name="**Countdown 1**",
            value=(
                "Switch to cd2 after 6 moves. Choose one of these every 3 moves:"
                "\n- 4x3 area at B2 ([Barrier] x4)"
            ),
            inline=False,
        )
        .add_field(
            name="**Countdown 2**",
            value=(
                "Do these in order every 4 moves:"
                "\n- 2x6 area at C1 ([Barrier] x6)"
                "\n- 6x2 area at A3 ([Barrier] x6)"
            ),
            inline=False,
        )
        .set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%202419.png"
            ),
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_with_level_boss_stage_shorthand(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.ANY, tuple())]},
    )
    real = await eb_details_shorthand(context_with_fake_message, "primarina 50")
    embed = discord.Embed(
        title="Event Stage 673: Primarina [Primarina] (Level 50)",
        colour=6852848,
        description=(
            "**HP**: 23022\n**Moves**: 16\n"
            "**Damage/move**: 1439 ([M+5] 1097)\n**Experience**: 5\n**Catchability**: 50%\n"
            "**Default Supports**: [Buneary][Happiny][Minccino][Meowth]\n"
            "**Rank Requirements**: 0 / 0 / 0\n"
            "**Attempt Cost**: [Heart] x1\n**Drop Items**: [PSB] / [PSB] / [PSB]\n"
            "**Drop Rates**: 25.0% / 25.0% / 25.0%\n**Items**: [M+5][EXP][MS][C-1][DD][APU]\n"
            "**EB stage clear reward**: [RML] x1"
        ),
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_eb_with_level_infinite(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.ANY, tuple())]},
    )
    real = await eb_details(context_with_fake_message, "primarina 200")
    embed = (
        discord.Embed(
            title="Event Stage 688: Primarina [Primarina] (Levels 151+ (200))",
            colour=6852848,
            description=(
                "**HP**: 85612\n**Moves**: 10\n"
                "**Damage/move**: 8562 ([M+5] 5708)\n**Experience**: 5\n**Catchability**: 100%\n"
                "**Default Supports**: [Primarina] | [Rock][Gulpin][Litwick][Amaura]\n"
                "**Rank Requirements**: 0 / 0 / 0\n"
                "**Attempt Cost**: [Heart] x1\n**Drop Items**: [PSB] / [PSB] / [PSB]\n"
                "**Drop Rates**: 25.0% / 25.0% / 25.0%\n**Items**: [M+5][EXP][MS][C-1][DD][APU]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%202515.png"
            ),
        )
        .add_field(
            name="**Countdown 1**",
            value=(
                "Switch to cd2 after 2 disrupts. Do these in order every 2 moves:"
                "\n- Disruption Pattern 3336 ([Block] x6, [Barrier] x6)"
                "\n- Disruption Pattern 3342 ([Block] x12, [Barrier] x8)"
            ),
            inline=False,
        )
        .add_field(
            name="**Countdown 2**",
            value=(
                "Switch to cd3 after 1 disrupt. Choose one of these every 3 moves:"
                "\n- Random 6x6 area ([Block] x4, [Barrier] x1)"
            ),
            inline=False,
        )
        .add_field(
            name="**Countdown 3**",
            value=(
                "Choose one of these every 4 moves:"
                "\n- Disruption Pattern 3348 ([Barrier] x14, [Block] x6)"
            ),
            inline=False,
        )
        .set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%202515.png"
            ),
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
