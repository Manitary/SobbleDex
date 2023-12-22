import pytest
from helper.helper_functions import check_payload_equal

import db
from koduck import KoduckContext
from models import Payload
from shuffle_commands import list_aliases


@pytest.mark.asyncio
async def test_no_args(context: KoduckContext) -> None:
    real = await list_aliases(context)
    expected = Payload(content="I need a name to look for aliases for!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_no_alias(patch_shuffle_db: None, context: KoduckContext) -> None:
    real = await list_aliases(context, "flabebe")
    expected = Payload(content="There are currently no aliases assigned to this name")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_alias_search_by_original_exists_one(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('alias', 'original')"
    )
    db.shuffle_connection.commit()
    real = await list_aliases(context, "original")
    expected = Payload(content="'original' is also known as: alias")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_alias_search_by_original_exist_multiple(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.executemany(
        "INSERT INTO aliases (alias, original_name) VALUES (:alias, 'original')",
        ({"alias": f"alias{i}"} for i in range(4, -1, -1)),
    )
    db.shuffle_connection.commit()
    real = await list_aliases(context, "original")
    expected = Payload(
        content="'original' is also known as: alias0, alias1, alias2, alias3, alias4"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_alias_search_by_original_non_ascii(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('flabebe', 'Flabébé')"
    )
    db.shuffle_connection.commit()
    real = await list_aliases(context, "Flabébé")
    expected = Payload(content="'Flabébé' is also known as: flabebe")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_alias_search_by_alias(
    patch_shuffle_db: None, context: KoduckContext
) -> None:
    db.shuffle_connection.execute(
        "INSERT INTO aliases (alias, original_name) VALUES ('flabebe', 'Flabébé')"
    )
    db.shuffle_connection.commit()
    real = await list_aliases(context, "flabebe")
    expected = Payload(content="'Flabébé' is also known as: flabebe")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
