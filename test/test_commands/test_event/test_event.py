from typing import Awaitable

import discord
import pytest
from freezegun import freeze_time
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import event


@pytest.mark.asyncio
async def test_event_no_args(context: KoduckContext) -> None:
    real = await event(context)
    expected = Payload(content="I need a Pokemon name to look up events for!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_two_args_invalid_int(context: KoduckContext) -> None:
    real = await event(context, "Pinsir", "0")
    expected = Payload(content="Result number should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_two_args_not_int(context: KoduckContext) -> None:
    real = await event(context, "Pinsir", "test")
    expected = Payload(content="Result number should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_two_args_invalid_int_with_space(context: KoduckContext) -> None:
    real = await event(context, "Pinsir 0")
    expected = Payload(content="Result number should be 1 or higher")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_not_pokemon(
    context: KoduckContext, monkeypatch: pytest.MonkeyPatch, do_nothing: Awaitable[None]
) -> None:
    monkeypatch.setattr(context, "send_message", do_nothing)
    real = await event(context, "test")
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_pokemon_no_event(context: KoduckContext) -> None:
    real = await event(context, "Aerodactyl")
    expected = Payload(content="Could not find an event with the Pokemon 'Aerodactyl'")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_event_multiple_results_out_of_bound(context: KoduckContext) -> None:
    real = await event(context, "Pinsir", "4")
    expected = Payload(content="Result number wasn't in the range of results (3)")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time("2023-12-24")
@pytest.mark.asyncio
async def test_event_one_choice_rotation(context: KoduckContext) -> None:
    real = await event(context, "Salazzle")
    embed = discord.Embed(title="Salazzle [Salazzle]", colour=43775).add_field(
        name="Rotation Event: Week 7/24",
        value=(
            "Event duration: 2024/03/19 06:00 UTC to 2024/03/26 06:00 UTC (7 days)"
            " (starts in 86 days 6 hours)"
        ),
        inline=False,
    )
    expected = Payload(embed=embed)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time("2023-12-24")
@pytest.mark.asyncio
async def test_event_one_choice_safari(context: KoduckContext) -> None:
    real = await event(context, "Camerupt")
    expected = Payload(
        embed=discord.Embed(title="Pokémon Safari", colour=1082930)
        .add_field(
            name="Event Pokémon",
            value=(
                "[Numel] Numel (16.67%)\n[Camerupt] Camerupt (3.33%)\n"
                "[Hippopotas (Female)] Hippopotas (Female) (16.67%)\n"
                "[Hippowdon (Female)] Hippowdon (Female) (3.33%)\n"
                "[Pidove] Pidove (20.0%)\n[Tranquill] Tranquill (10.0%)\n"
                "[Unfezant (Male)] Unfezant (Male) (6.67%)\n"
                "[Unfezant (Female)] Unfezant (Female) (3.33%)\n"
                "[Jangmo-o] Jangmo-o (13.33%)\n[Hakamo-o] Hakamo-o (6.67%)\n"
            ),
            inline=False,
        )
        .add_field(
            name="Rotation Event: Week 15/24",
            value=(
                "Event duration: 2024/05/14 06:00 UTC to 2024/05/28 06:00 UTC (14 days)"
                " (starts in 142 days 6 hours)"
            ),
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time("2023-12-24")
@pytest.mark.asyncio
async def test_event_one_choice_competition(context: KoduckContext) -> None:
    real = await event(context, "megabanette")
    expected = Payload(
        embed=discord.Embed(
            title="Mega Banette [Mega Banette]", colour=14959622
        ).add_field(
            name="Rotation Event: Week 1/24",
            value=(
                "Event duration: 2024/02/06 06:00 UTC to 2024/02/13 05:00 UTC (6 days, 23 hours)"
                " (starts in 44 days 6 hours)"
            ),
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time("2023-12-24")
@pytest.mark.asyncio
async def test_event_one_choice_eb(context: KoduckContext) -> None:
    real = await event(context, "giratinao")
    expected = Payload(
        embed=discord.Embed(
            title="Escalation Battles: Giratina (Origin Forme) [Giratina (Origin Forme)]",
            colour=5144142,
        ).add_field(
            name="Rotation Event: Week 20/24",
            value=(
                "Event duration: 2024/01/02 06:00 UTC to 2024/01/16 06:00 UTC (14 days)"
                " (starts in 9 days 6 hours)"
            ),
            inline=False,
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@freeze_time("2023-12-24")
@pytest.mark.asyncio
async def test_event_one_choice_yearly(context: KoduckContext) -> None:
    real = await event(context, "shaymin")
    expected = Payload(
        embed=discord.Embed(
            title="Daily Pokémon",
            colour=16749568,
        )
        .add_field(
            name="Event Pokémon",
            value=(
                "Monday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Tuesday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Wednesday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Thursday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Friday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Saturday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
                "Sunday: Shaymin (Land Forme) [Shaymin (Land Forme)]\n"
            ),
            inline=False,
        )
        .add_field(
            name="Yearly Event",
            value=(
                "Event duration: 20XX/02/18 06:00 UTC to 20XX/02/21 06:00 UTC (3 days)"
                " (starts in 56 days 6 hours)"
            ),
            inline=False,
        )
        .add_field(
            name="Misc. Details",
            value="Stage is available to attempt 1 time before it disappears",
            inline=False
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
