from typing import Any, Awaitable

import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands.lookup
from koduck import KoduckContext
from models import Payload
from shuffle_commands import stage
from shuffle_commands.eb import eb_details


@pytest.mark.asyncio
async def test_stage_no_args(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history)
    expected = Payload(content="I need a stage index/pokemon to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.parametrize("stage_id", (0, 701))
@pytest.mark.asyncio
async def test_stage_main_out_of_bound(
    context_with_fake_message_and_history: KoduckContext, stage_id: int
) -> None:
    real = await stage(context_with_fake_message_and_history, str(stage_id))
    expected = Payload(content="Main Stages range from 1 to 700")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.parametrize("stage_id", ("ex0", "ex54"))
@pytest.mark.asyncio
async def test_stage_expert_out_of_bound(
    context_with_fake_message_and_history: KoduckContext, stage_id: str
) -> None:
    real = await stage(context_with_fake_message_and_history, stage_id)
    expected = Payload(content="Expert Stages range from 1 to 53")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_event_out_of_bound(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "s800")
    expected = Payload(content="Event Stages range from 0 to 715")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_invalid_pokemon(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    monkeypatch.setattr(
        context_with_fake_message_and_history, "send_message", do_nothing
    )
    real = await stage(context_with_fake_message_and_history, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_invalid_pokemon_2(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def choose_zero(*args: Any, **kwargs: Any) -> int:
        return 0

    monkeypatch.setattr(shuffle_commands.lookup, "choice_react", choose_zero)
    real = await stage(context_with_fake_message_and_history, "ejectt")
    expected = Payload(content="Could not find a stage with the Pokemon 'Eliminate'")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_2nd_arg_not_int(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "blissey", "test")
    expected = Payload(content="Result number should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_2nd_arg_invalid_int(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "blissey", "-1")
    expected = Payload(content="Result number should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_main_by_id(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "1")
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 1: Espurr [Espurr]",
            colour=16275592,
            description=(
                "**3DS HP**: 200 (UX: 600)\n**Mobile HP**: 600 (UX: 1800)\n"
                "**Moves**: 8\n**Damage/move**: 25 ([M+5] 16)\n"
                "**Experience**: 8\n**Catchability**: 75% + 5%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 4 / 3 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Items**: [M+5][EXP][MS][C-1]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%201.png"
            ),
        ).set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%201.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_expert_by_id(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "ex2")
    expected = Payload(
        embed=discord.Embed(
            title="Expert Stage 2: Rotom [Rotom]",
            colour=16306224,
            description=(
                "**HP**: 3456\n**Seconds**: 60\n**Damage/second**: 58 ([T+10] 50)\n"
                "**Experience**: 10\n**Catchability**: 1% + 5%/3sec (Mobile: 1% + 3%/3sec)\n"
                "**Default Supports**: [Jolteon] | [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 30 / 10 / 1\n**S-Ranks to unlock**: 12\n"
                "**Attempt Cost**: [Heart] x1\n**Items**: [T+10][EXP][MS][C-1]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Expert%20Stages%20Layouts/Layout%20Index%201.png"
            ),
        ).set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Expert%20Stages%20Layouts/Layout%20Index%201.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_event_by_id(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "s3")
    expected = Payload(
        embed=discord.Embed(
            title="Event Stage 3: Charmander [Charmander]",
            colour=15761456,
            description=(
                "**HP**: 700\n**Moves**: 5\n**Damage/move**: 140 ([M+5] 70)\n"
                "**Experience**: 5\n**Catchability**: 0% + 100%/move (Mobile: 100% + 100%/move)\n"
                "**Default Supports**: [Buneary][Happiny][Minccino][Meowth]\n"
                "**Rank Requirements**: 3 / 2 / 1\n**Attempt Cost**: [Heart] x0\n"
                "**Drop Items**: [MSU] / [MSU] / [Nothing]\n"
                "**Drop Rates**: 100.0% / 100.0% / 0.0%\n"
                "**Items**: [M+5][EXP][MS][C-1][APU]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%203049.png"
            ),
        )
        .add_field(
            name="**Countdown 1**",
            value="Switch to cd2 when Moves <= 1. ",
            inline=False,
        )
        .add_field(
            name="**Countdown 2**",
            value=(
                "Choose one of these every 0 move:"
                "\n- Disruption Pattern 4152 ([Charmander] x36)"
            ),
            inline=False,
        )
        .set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Event%20Stages%20Layouts/Layout%20Index%203049.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_multiple_choices_pre_select_with_space(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "blissey 2")
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 493: Blissey [Blissey]",
            colour=11053176,
            description=(
                "**HP**: 18900 (UX: 56700)\n**Moves**: 15\n**Damage/move**: 1260 ([M+5] 945)\n"
                "**Experience**: 15\n**Catchability**: 8% + 8%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 7 / 3 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Drop Items**: [PSB] / [PSB] / [PSB]\n"
                "**Drop Rates**: 25.0% / 12.5% / 0.78125%\n"
                "**Items**: [M+5][EXP][MS][C-1][DD]"
            ),
        ).add_field(
            name="**Countdown 1**",
            value=(
                "Start counter at 0. Do these in order every 5 moves:"
                "\n- 6x2 area at A3 ([Barrier] x4, [Blissey] x2)"
                "\n- Random 4x4 area ([Blissey] x3, [Barrier] x1)"
                "\n- 2x6 area at C1 ([Barrier] x4, [Blissey] x2)"
            ),
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_multiple_choices_pre_select_out_of_bound(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "blissey 4")
    expected = Payload(content="Result number wasn't in the range of results (3)")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_multiple_choices(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    async def choose_zero(*args: Any, **kwargs: Any) -> int:
        return 0

    monkeypatch.setattr(
        context_with_fake_message_and_history, "send_message", do_nothing
    )
    real = await stage(
        context_with_fake_message_and_history, "blissey", choice_selector=choose_zero
    )
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 115: Blissey [Blissey]",
            colour=11053176,
            description=(
                "**HP**: 4322 (UX: 12966)\n**Moves**: 16\n**Damage/move**: 271 ([M+5] 206)\n"
                "**Experience**: 16\n**Catchability**: 5% + 6%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 8 / 4 / 1\n"
                "**Attempt Cost**: [Heart] x1\n**Items**: [M+5][EXP][MS][C-1]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%20295.png"
            ),
        ).set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%20295.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_multiple_choices_no_selection(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    async def choose_none(*args: Any, **kwargs: Any) -> None:
        return None

    monkeypatch.setattr(
        context_with_fake_message_and_history, "send_message", do_nothing
    )
    real = await stage(
        context_with_fake_message_and_history, "blissey", choice_selector=choose_none
    )
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_eb_pokemon(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "giratinao")
    expected = Payload(
        embed=discord.Embed(
            title="Giratina (Origin Forme) Escalation Battles Details",
            colour=5144142,
            description=(
                "**Levels 1 to 9**: 4200 + 375 / 50\n**Level 10**: 24000 / 50\n"
                "**Levels 11 to 39**: 4950 + 117 / 50\n**Level 40**: 29172 / 50\n"
                "**Levels 41 to 69**: 8820 + 64 / 50\n**Level 70**: 33976 / 50\n"
                "**Levels 71 to 99**: 7912 + 188 / 50\n**Level 100**: 34288 / 50\n"
                "**Levels 101 to 129**: 10173 + 121 / 50\n**Level 130**: 41328 / 50\n"
                "**Levels 131 to 149**: 8778 + 320 / 50\n**Level 150**: 39270 / 50\n"
                "**Levels 151 to 199**: 7623 + 120 / 50\n"
                "**Level 200**: 49410 / 50 **(5th support: [Block])**\n"
                "**Levels 201 to 239**: 7560 + 119 / 40\n**Levels 240 to 249**: 7812 + 252 / 30\n"
                "**Level 250**: 32340 / 30 **(5th support: [Block])**\n"
                "**Levels 251 to 269**: 12474 + 128 / 50\n**Levels 270 to 279**: 7770 + 460 / 30\n"
                "**Level 280**: 58968 / 50 **(5th support: [Block])**\n"
                "**Levels 281 to 289**: 10080 + 315 / 40\n**Levels 290 to 299**: 27200 + 280 / 50\n"
                "**Level 300**: 64092 / 50 **(5th support: [Block])**\n"
                "**Levels 301+**: 12600 / 50\n"
            ),
        )
    )
    assert isinstance(real, dict)
    assert isinstance(expected, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_eb_pokemon_with_args(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await stage(context_with_fake_message_and_history, "giratinao", "100")
    expected = Payload(
        embed=discord.Embed(
            title="Giratina (Origin Forme) Escalation Battles Details",
            colour=5144142,
            description=(
                "**Levels 1 to 9**: 4200 + 375 / 50\n**Level 10**: 24000 / 50\n"
                "**Levels 11 to 39**: 4950 + 117 / 50\n**Level 40**: 29172 / 50\n"
                "**Levels 41 to 69**: 8820 + 64 / 50\n**Level 70**: 33976 / 50\n"
                "**Levels 71 to 99**: 7912 + 188 / 50\n**Level 100**: 34288 / 50\n"
                "**Levels 101 to 129**: 10173 + 121 / 50\n**Level 130**: 41328 / 50\n"
                "**Levels 131 to 149**: 8778 + 320 / 50\n**Level 150**: 39270 / 50\n"
                "**Levels 151 to 199**: 7623 + 120 / 50\n"
                "**Level 200**: 49410 / 50 **(5th support: [Block])**\n"
                "**Levels 201 to 239**: 7560 + 119 / 40\n**Levels 240 to 249**: 7812 + 252 / 30\n"
                "**Level 250**: 32340 / 30 **(5th support: [Block])**\n"
                "**Levels 251 to 269**: 12474 + 128 / 50\n**Levels 270 to 279**: 7770 + 460 / 30\n"
                "**Level 280**: 58968 / 50 **(5th support: [Block])**\n"
                "**Levels 281 to 289**: 10080 + 315 / 40\n**Levels 290 to 299**: 27200 + 280 / 50\n"
                "**Level 300**: 64092 / 50 **(5th support: [Block])**\n"
                "**Levels 301+**: 12600 / 50\n"
            ),
        )
    )
    assert isinstance(real, dict)
    assert isinstance(expected, dict)
    check_payload_equal(real, expected)
