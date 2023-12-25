from typing import Any, Awaitable

import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands.lookup
from koduck import KoduckContext
from models import Payload
from shuffle_commands import skill


@pytest.mark.asyncio
async def test_skill_no_args(context: KoduckContext) -> None:
    real = await skill(context)
    expected = Payload(content="I need a Skill name to look up!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_invalid_arg(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await skill(context, "test")
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
    real = await skill(context, "Dugtrio")
    expected = Payload(
        content="Could not find a Skill entry with the name 'Dugtrio (Alola Form)'"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill(context: KoduckContext) -> None:
    real = await skill(context, "mindzap")
    expected = Payload(
        embed=discord.Embed(
            title="Mind Zap",
            colour=16711680,
            description=(
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
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
