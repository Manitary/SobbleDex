from typing import Any, Awaitable

import discord
import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import starting_board


@pytest.mark.asyncio
async def test_board_main_by_id(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await starting_board(context_with_fake_message_and_history, "1")
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage Index 1: Espurr [Espurr]",
            colour=16275592,
        ).set_image(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%201.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_board_multiple_choices_pre_select_with_space(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await starting_board(context_with_fake_message_and_history, "blissey 3")
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage Index 645: Blissey [Blissey]",
            colour=11053176,
        ).set_image(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%203421.png"
            )
        )
    )
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
    real = await starting_board(
        context_with_fake_message_and_history, "blissey", choice_selector=choose_zero
    )
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage Index 115: Blissey [Blissey]",
            colour=11053176,
        ).set_image(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                "Main%20Stages%20Layouts/Layout%20Index%20295.png"
            )
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_stage_no_starting_board(
    context_with_fake_message_and_history: KoduckContext,
) -> None:
    real = await starting_board(context_with_fake_message_and_history, "blissey", "2")
    expected = Payload(
        embed=discord.Embed(
            title="Main Stage Index 493: Blissey [Blissey]",
            colour=11053176,
            description="No initial board layout",
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
