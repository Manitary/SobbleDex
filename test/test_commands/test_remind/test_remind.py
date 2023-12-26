from typing import Awaitable

import pytest
from helper.helper_functions import check_payload_equal

import db
from koduck import KoduckContext
from models import Payload
from shuffle_commands.remind import remind_me


@pytest.mark.asyncio
async def test_remind_no_arg_no_db_entry(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await remind_me(context_with_fake_message)
    expected_message = Payload(
        content="You are signed up to be reminded for:\nWeeks: \nPokémon: "
    )
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)


@pytest.mark.asyncio
async def test_remind_no_arg_with_db_entry(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        """INSERT INTO reminders (user_id, weeks, pokemon)
        VALUES (1, "2, 14, 3", "Dugtrio")
        """
    )
    real = await remind_me(context_with_fake_message)
    expected_message = Payload(
        content="You are signed up to be reminded for:\nWeeks: 2, 14, 3\nPokémon: Dugtrio"
    )
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 1
    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)


@pytest.mark.parametrize("week_num", (0, 25))
@pytest.mark.asyncio
async def test_remind_invalid_week_num(
    patch_shuffle_db_wipe_reminders: None,
    context_with_fake_message: KoduckContext,
    week_num: int,
) -> None:
    real = await remind_me(context_with_fake_message, str(week_num))
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
async def test_remind_week_num_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.add_reminder_week(1, 2)
    db.shuffle_connection.commit()

    real = await remind_me(context_with_fake_message, "2")
    expected = Payload(content="You already signed up for this rotation week")
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 1
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_week_new_record(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await remind_me(context_with_fake_message, "2")
    expected = Payload(
        content="Okay, you’re signed up to be reminded when rotation week 2 starts"
    )
    table_rows = db.shuffle_connection.execute(
        "SELECT id, user_id, weeks, pokemon FROM reminders"
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {"id": 1, "user_id": 1, "weeks": "2", "pokemon": None}
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_week_append_to_record(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    db.add_reminder_week(1, 2)
    db.shuffle_connection.commit()
    real = await remind_me(context_with_fake_message, "12")
    expected = Payload(
        content="Okay, you’re signed up to be reminded when rotation week 12 starts"
    )
    table_rows = db.shuffle_connection.execute(
        "SELECT id, user_id, weeks, pokemon FROM reminders"
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {"id": 1, "user_id": 1, "weeks": "2, 12", "pokemon": None}
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_invalid_pokemon(
    patch_shuffle_db_wipe_reminders: None,
    context_with_fake_message: KoduckContext,
    monkeypatch: pytest.MonkeyPatch,
    do_nothing: Awaitable[None],
) -> None:
    monkeypatch.setattr(context_with_fake_message, "send_message", do_nothing)
    real = await remind_me(context_with_fake_message, "test")
    expected_message = Payload()
    table_rows = db.shuffle_connection.execute("SELECT id FROM reminders").fetchall()

    assert len(table_rows) == 0
    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)


@pytest.mark.asyncio
async def test_remind_pokemon_in_db(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    await remind_me(context_with_fake_message, "Giratina-O")
    real = await remind_me(context_with_fake_message, "giratinao")
    expected = Payload(content="You already signed up for this Pokémon")
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": None,
        "pokemon": "Giratina (Origin Forme)",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_pokemon_new_record(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    real = await remind_me(context_with_fake_message, "giratinao")
    expected = Payload(
        content=(
            "Okay, you’re signed up to be reminded when Giratina (Origin Forme) "
            "appears in an event"
        )
    )
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": None,
        "pokemon": "Giratina (Origin Forme)",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_remind_pokemon_append_to_record(
    patch_shuffle_db_wipe_reminders: None, context_with_fake_message: KoduckContext
) -> None:
    await remind_me(context_with_fake_message, "meloetta")
    real = await remind_me(context_with_fake_message, "giratinao")
    expected = Payload(
        content=(
            "Okay, you’re signed up to be reminded when Giratina (Origin Forme) "
            "appears in an event"
        )
    )
    table_rows = db.shuffle_connection.execute(
        """SELECT id, user_id, weeks, pokemon FROM reminders"""
    ).fetchall()

    assert len(table_rows) == 1
    assert table_rows[0] == {
        "id": 1,
        "user_id": 1,
        "weeks": None,
        "pokemon": "Meloetta (Aria Forme), Giratina (Origin Forme)",
    }
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
