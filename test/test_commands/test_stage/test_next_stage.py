import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload, QueryType, UserQuery
from shuffle_commands import next_stage, next_stage_shorthand, stage, stage_shorthand


@pytest.mark.asyncio
async def test_next_stage(context_with_fake_message_and_history: KoduckContext) -> None:
    await stage(context_with_fake_message_and_history, "1")
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 2: Bulbasaur [Bulbasaur]",
            colour=7915600,
            description=(
                "**3DS HP**: 360 (UX: 1080)\n**Mobile HP**: 90 (UX: 270)\n"
                "**Moves**: 7 (Mobile: 10)\n**Damage/move**: 52 ([M+5] 30)\n"
                "**Experience**: 7 (Mobile: 10)\n**Catchability**: 75% + 4%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 4 / 2 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Items**: [M+5][EXP][MS][C-1]"
            ),
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%2019.png"
            ),
        ).set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%2019.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_roll_around_main(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage(context_with_fake_message_and_history, "700")
    real = await next_stage(context_with_fake_message_and_history)
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
async def test_next_stage_no_roll_around_expert(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage(context_with_fake_message_and_history, "ex53")
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(content="Expert Stages range from 1 to 53")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_no_next_for_events(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage(context_with_fake_message_and_history, "s5")
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(content="The command only works with a main or EX stage")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_no_history(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(content="No stage in your recent query history")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_broken_history_no_args(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        context_with_fake_message_and_history.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE)]},
    )
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(content="Unexpected error, contact my owner to investigate")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_broken_history_invalid_stage_id(
    context_with_fake_message_and_history: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        context_with_fake_message_and_history.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE, ("exx12",))]},
    )
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(content="Unexpected error, contact my owner to investigate")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_keep_shorthand(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage_shorthand(context_with_fake_message_and_history, "1")
    real = await next_stage(context_with_fake_message_and_history)
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 2: Bulbasaur [Bulbasaur]",
            colour=7915600,
            description=(
                "**3DS HP**: 360 (UX: 1080)\n**Mobile HP**: 90 (UX: 270)\n"
                "**Moves**: 7 (Mobile: 10)\n**Damage/move**: 52 ([M+5] 30)\n"
                "**Experience**: 7 (Mobile: 10)\n**Catchability**: 75% + 4%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 4 / 2 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Items**: [M+5][EXP][MS][C-1]"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_shorthand_overwrite_no_shorthand(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage(context_with_fake_message_and_history, "1")
    real = await next_stage_shorthand(context_with_fake_message_and_history)
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 2: Bulbasaur [Bulbasaur]",
            colour=7915600,
            description=(
                "**3DS HP**: 360 (UX: 1080)\n**Mobile HP**: 90 (UX: 270)\n"
                "**Moves**: 7 (Mobile: 10)\n**Damage/move**: 52 ([M+5] 30)\n"
                "**Experience**: 7 (Mobile: 10)\n**Catchability**: 75% + 4%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 4 / 2 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Items**: [M+5][EXP][MS][C-1]"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_next_stage_shorthand_keeps_shorthand(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    await stage_shorthand(context_with_fake_message_and_history, "1")
    real = await next_stage_shorthand(context_with_fake_message_and_history)
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage 2: Bulbasaur [Bulbasaur]",
            colour=7915600,
            description=(
                "**3DS HP**: 360 (UX: 1080)\n**Mobile HP**: 90 (UX: 270)\n"
                "**Moves**: 7 (Mobile: 10)\n**Damage/move**: 52 ([M+5] 30)\n"
                "**Experience**: 7 (Mobile: 10)\n**Catchability**: 75% + 4%/move\n"
                "**Default Supports**: [Pidgey][Happiny][Azurill][Pichu]\n"
                "**Rank Requirements**: 4 / 2 / 1\n**Attempt Cost**: [Heart] x1\n"
                "**Items**: [M+5][EXP][MS][C-1]"
            ),
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
