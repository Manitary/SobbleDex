import sqlite3
from typing import Iterator

import pytest

import db


@pytest.fixture(scope="function", autouse=True)
def patch_shuffle_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    _db = sqlite3.Connection(":memory:")
    _db.row_factory = db.dict_factory
    with open("queries/create_shuffle_tables.sql", encoding="utf-8") as f:
        query = f.read()
    _db.executescript(query)
    monkeypatch.setattr(db, "shuffle_connection", _db)
    yield
    _db.close()
