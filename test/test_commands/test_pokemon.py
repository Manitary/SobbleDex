from typing import Any, Awaitable

import discord
import pytest
from helper.helper_functions import check_payload_equal

import shuffle_commands.lookup
from koduck import KoduckContext
from models import Payload, QueryType, UserQuery
from shuffle_commands import pokemon


@pytest.mark.asyncio
async def test_invalid_pokemon(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await pokemon(context, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_pokemon(context: KoduckContext) -> None:
    real = await pokemon(context, "bulbasaur")
    embed = discord.Embed(
        title="Bulbasaur",
        description=(
            "**Dex**: 001\n**Type**: Grass\n**BP**: 40\n**RMLs**: 20"
            "\n**Max AP**: 125\n**Skill**: Power of 4 (Mega Boost+)"
        ),
        colour=7915600,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Bulbasaur.png"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_pokemon_with_space(context: KoduckContext) -> None:
    real = await pokemon(context, "zygarde 10")
    embed = discord.Embed(
        title="Zygarde (10% Forme)",
        description=(
            "**Dex**: 503\n**Type**: Dragon\n**BP**: 50\n**RMLs**: 5"
            "\n**Max AP**: 100\n**Skill**: Mega Boost+"
        ),
        colour=7354616,
    )
    embed.set_thumbnail(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/"
            "Zygarde%20%2810%25%20Forme%29.png"
        )
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_lookup(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def choose_zero(*args: Any, **kwargs: Any) -> int:
        return 0

    monkeypatch.setattr(shuffle_commands.lookup, "choice_react", choose_zero)
    real = await pokemon(context, "spookofy+")
    expected = Payload(
        content="Could not find a Pokemon entry with the name 'Spookify+'"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_no_stage(context_with_fake_message: KoduckContext) -> None:
    real = await pokemon(context_with_fake_message)
    expected = Payload(content="No stage in your recent query history")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_with_one_stage_history(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE, ("1",))]},
    )
    real = await pokemon(context_with_fake_message)
    embed = discord.Embed(
        title="Espurr",
        description=(
            "**Dex**: 013\n**Type**: Psychic\n**BP**: 40\n**RMLs**: 5"
            "\n**Max AP**: 90\n**Skill**: Opportunist (Sleep Charm)"
        ),
        colour=16275592,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Espurr.png"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_with_two_stage_history(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {
            1: [
                UserQuery(QueryType.STAGE, ("2",)),
                UserQuery(QueryType.STAGE, ("1",)),
                UserQuery(QueryType.ANY, ("test",)),
            ]
        },
    )
    real = await pokemon(context_with_fake_message)
    embed = discord.Embed(
        title="Espurr",
        description=(
            "**Dex**: 013\n**Type**: Psychic\n**BP**: 40\n**RMLs**: 5"
            "\n**Max AP**: 90\n**Skill**: Opportunist (Sleep Charm)"
        ),
        colour=16275592,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Espurr.png"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_with_sp_stage_history(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE, ("s521",))]},
    )
    real = await pokemon(context_with_fake_message)
    embed = discord.Embed(
        title="Darkrai",
        description=(
            "**Dex**: 303\n**Type**: Dark\n**BP**: 80\n**RMLs**: 20"
            "\n**Max AP**: 145\n**Skill**: Sleep Charm (Spookify+)"
        ),
        colour=7362632,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Darkrai.png"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_with_ex_stage_history(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE, ("ex1",))]},
    )
    real = await pokemon(context_with_fake_message)
    embed = discord.Embed(
        title="Absol",
        description=(
            "**Dex**: 033\n**Type**: Dark\n**BP**: 60\n**RMLs**: 20"
            "\n**Max AP**: 135\n**Skill**: Mind Zap"
        ),
        colour=7362632,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/Absol.png"
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_invalid_history_no_args(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE)]},
    )
    real = await pokemon(context_with_fake_message)
    content = "Unexpected error, contact my owner to investigate"
    expected = Payload(content=content)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_arg_invalid_history_invalid_stage_id(
    context_with_fake_message: KoduckContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        context_with_fake_message.koduck,
        "query_history",
        {1: [UserQuery(QueryType.STAGE, ("ss1",))]},
    )
    real = await pokemon(context_with_fake_message)
    content = "Unexpected error, contact my owner to investigate"
    expected = Payload(content=content)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
