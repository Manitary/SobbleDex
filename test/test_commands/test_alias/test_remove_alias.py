import pytest
from helper.helper_functions import check_payload_equal

import db
from koduck import KoduckContext
from models import Payload
from shuffle_commands import remove_alias


@pytest.mark.asyncio
async def test_no_arg(context: KoduckContext) -> None:
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    real = await remove_alias(context)
    expected_message = Payload(content="I need an alias to remove!")
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == len(expected_new_aliases) == 0


@pytest.mark.asyncio
async def test_too_many_args(context: KoduckContext) -> None:
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    real = await remove_alias(context, *("test",) * 11)
    expected_message = Payload(
        content="Please only give me up to 10 aliases to remove!"
    )
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == len(expected_new_aliases) == 0


@pytest.mark.asyncio
async def test_remove_one_alias(context: KoduckContext) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('alias', 'original')"
    )
    db.shuffle_connection.commit()
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    real = await remove_alias(context, "alias")
    expected_message = Payload(
        content="Removed an alias: 'original' is no longer known as 'alias'"
    )
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == 1
    assert len(expected_new_aliases) == 0


@pytest.mark.asyncio
async def test_remove_one_alias_not_exist(context: KoduckContext) -> None:
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()
    real = await remove_alias(context, "alias1")
    expected_message = Payload(
        content="'alias1' is not currently assigned as an alias to anything"
    )
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == len(expected_new_aliases) == 0


@pytest.mark.asyncio
async def test_remove_one_alias_success_one_not_exist(context: KoduckContext) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('alias', 'original')"
    )
    db.shuffle_connection.commit()
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    real = await remove_alias(context, "alias1", "alias")
    expected_message = Payload(
        content=(
            "Removed an alias: 'original' is no longer known as 'alias'"
            "\n'alias1' is not currently assigned as an alias to anything"
        )
    )
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == 1
    assert len(expected_new_aliases) == 0


@pytest.mark.asyncio
async def test_remove_one_alias_success_one_not_exist_with_duplicates(
    context: KoduckContext,
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('alias', 'original')"
    )
    db.shuffle_connection.commit()
    all_aliases = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    real = await remove_alias(context, "alias1", "alias", "alias", "alias1")
    expected_message = Payload(
        content=(
            "Removed an alias: 'original' is no longer known as 'alias'"
            "\n'alias1' is not currently assigned as an alias to anything"
        )
    )
    expected_new_aliases = db.shuffle_connection.execute(
        "SELECT * FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(all_aliases) == 1
    assert len(expected_new_aliases) == 0
