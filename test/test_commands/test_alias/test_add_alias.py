import pytest
from helper.helper_functions import check_payload_equal

import db
from koduck import KoduckContext
from models import Payload
from shuffle_commands import add_alias


@pytest.mark.asyncio
async def test_fail_no_args(context: KoduckContext) -> None:
    real = await add_alias(context)
    expected = Payload(content="I need at least two parameters: original, alias(es)")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_fail_one_arg(context: KoduckContext) -> None:
    real = await add_alias(context, "test")
    expected = Payload(content="I need at least two parameters: original, alias(es)")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_fail_too_many_args(context: KoduckContext) -> None:
    real = await add_alias(context, *("test",) * 12)
    expected = Payload(content="Please only give me up to 10 aliases to add!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_empty_db_add_one_alias_success(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    real = await add_alias(context, "original", "alias")
    expected_message = Payload(
        content="Added an alias: 'original' is now also known as 'alias'"
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 1
    assert expected_rows[0] == {"id": 1, "alias": "alias", "original_name": "original"}


@pytest.mark.asyncio
async def test_empty_db_add_two_aliases_success(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    real = await add_alias(context, "original", "alias1", "alias2")
    expected_message = Payload(
        content=(
            "Added an alias: 'original' is now also known as 'alias1'"
            "\nAdded an alias: 'original' is now also known as 'alias2'"
        )
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases ORDER BY id"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 2
    assert expected_rows[0] == {"id": 1, "alias": "alias1", "original_name": "original"}
    assert expected_rows[1] == {"id": 2, "alias": "alias2", "original_name": "original"}


@pytest.mark.asyncio
async def test_empty_db_add_one_good_alias_one_bad_alias(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    real = await add_alias(context, "original", "alias1", "<@!1234>")
    expected_message = Payload(
        content=(
            "Added an alias: 'original' is now also known as 'alias1'"
            "\nFailed to add `<@!1234>` as an alias because it contains a ping"
        )
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 1
    assert expected_rows[0] == {"id": 1, "alias": "alias1", "original_name": "original"}


@pytest.mark.asyncio
async def test_empty_db_add_one_good_alias_one_duplicate_alias(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    real = await add_alias(context, "original", "alias1", "alias1")
    expected_message = Payload(
        content=("Added an alias: 'original' is now also known as 'alias1'")
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 1
    assert expected_rows[0] == {"id": 1, "alias": "alias1", "original_name": "original"}


@pytest.mark.asyncio
async def test_db_add_one_good_alias_one_duplicate_alias(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('old_alias', 'original')"
    )
    db.shuffle_connection.commit()
    real = await add_alias(context, "new", "old_alias", "alias")
    expected_message = Payload(
        content=(
            "Added an alias: 'new' is now also known as 'alias'"
            "\n'old_alias' is already used as an alias for 'original'"
        )
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases ORDER BY id"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 2
    assert expected_rows[0] == {
        "id": 1,
        "alias": "old_alias",
        "original_name": "original",
    }
    assert expected_rows[1] == {"id": 2, "alias": "alias", "original_name": "new"}


@pytest.mark.asyncio
async def test_empty_db_add_empty_aliases(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    real = await add_alias(context, "original", "", "", "", "")
    expected_message = Payload(content="No valid alias provided")
    expected_rows = db.shuffle_connection.execute("SELECT * FROM aliases").fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 0


@pytest.mark.asyncio
async def test_db_add_valid_duplicate_bad_empty_aliases_scrambled_order(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('alias', 'original')"
    )
    db.shuffle_connection.commit()
    real = await add_alias(
        context, "new", "<@123>", "", "alias", "valid_alias", "alias"
    )
    expected_message = Payload(
        content=(
            "Added an alias: 'new' is now also known as 'valid_alias'"
            "\n'alias' is already used as an alias for 'original'"
            "\nFailed to add `<@123>` as an alias because it contains a ping"
        )
    )
    expected_rows = db.shuffle_connection.execute(
        "SELECT id, alias, original_name FROM aliases ORDER BY id"
    ).fetchall()

    assert isinstance(real, dict)
    check_payload_equal(real, expected_message)
    assert len(expected_rows) == 2
    assert expected_rows[0] == {
        "id": 1,
        "alias": "alias",
        "original_name": "original",
    }
    assert expected_rows[1] == {"id": 2, "alias": "valid_alias", "original_name": "new"}
