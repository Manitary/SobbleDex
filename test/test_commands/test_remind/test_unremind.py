from typing import Awaitable

import pytest
from helper.helper_functions import check_payload_equal

import db
from koduck import KoduckContext
from models import Payload
from shuffle_commands.remind import unremind_me


@pytest.mark.asyncio
async def test_unremind_no_arg(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await unremind_me(context_with_fake_message)
    expected_message = Payload(content="I need a week number or a Pokémon name")
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)


@pytest.mark.parametrize("week_num", (0, 25))
@pytest.mark.asyncio
async def test_unremind_invalid_week_num(
    patch_shuffle_db_wipe_reminders: None,
    context_with_fake_message: KoduckContext,
    week_num: int,
) -> None:
    real = await unremind_me(context_with_fake_message, str(week_num))
    expected = Payload(
        content=(
            "There are 24 weeks of events in the event rotation, "
            "so I need a number from 1 to 24"
        )
    )
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_week_user_not_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await unremind_me(context_with_fake_message, "2")
    expected = Payload(content="You aren’t signed up for this rotation week")
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_week_not_in_user_list(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        """INSERT INTO reminders (user_id, weeks, pokemon)
        VALUES (1, "1, 3, 22", "Dugtrio, Kabutops")
        """
    )
    real = await unremind_me(context_with_fake_message, "2")
    expected = Payload(content="You aren’t signed up for this rotation week")
    table_rows = db.shuffle_connection.execute(
        "SELECT id, user_id, weeks, pokemon FROM reminders"
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": "1, 3, 22",
        "pokemon": "Dugtrio, Kabutops",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_unremind_week_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        """INSERT INTO reminders (user_id, weeks, pokemon)
        VALUES (1, "12, 2, 3, 22", "Dugtrio")"""
    )
    db.shuffle_connection.commit()

    real = await unremind_me(context_with_fake_message, "2")
    expected = Payload(
        content="Okay, you’re no longer signed up to be reminded when rotation week 2 starts"
    )
    table_rows = db.shuffle_connection.execute(
        "SELECT id, user_id, weeks, pokemon FROM reminders"
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": "12, 3, 22",
        "pokemon": "Dugtrio",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_unremind_invalid_pokemon(
    patch_shuffle_db_wipe_reminders: None,
    context_with_fake_message: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    monkeypatch.setattr(context_with_fake_message, "send_message", do_nothing)
    real = await unremind_me(context_with_fake_message, "test")
    expected_message = Payload()
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)


@pytest.mark.asyncio
async def test_unremind_pokemon_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        """INSERT INTO reminders (user_id, weeks, pokemon)
        VALUES (1, "1, 3, 4", "Giratina (Origin Forme), Latios")"""
    )
    real = await unremind_me(context_with_fake_message, "giratinao")
    expected = Payload(
        content=(
            "Okay, you’re no longer signed up to be reminded when "
            "Giratina (Origin Forme) appears in an event"
        )
    )
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": "1, 3, 4",
        "pokemon": "Latios",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_unremind_pokemon_user_not_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await unremind_me(context_with_fake_message, "giratinao")
    expected = Payload(content="You aren’t signed up for this Pokémon")
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_unremind_pokemon_not_in_user_list(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        """INSERT INTO reminders (user_id, weeks, pokemon)
        VALUES (1, "2, 3", "Dugtrio, Kabutops")
        """
    )
    real = await unremind_me(context_with_fake_message, "giratinao")
    expected = Payload(content="You aren’t signed up for this Pokémon")
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": "2, 3",
        "pokemon": "Dugtrio, Kabutops",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
