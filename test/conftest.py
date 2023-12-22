import sqlite3
from typing import Any, Awaitable, Callable, Iterator

import pytest

import db
from koduck import Koduck, KoduckContext

pytest.register_assert_rewrite("helper")


@pytest.fixture(name="koduck_instance", scope="session")
def _koduck_instance() -> Iterator[Koduck]:
    _koduck = Koduck()
    yield _koduck


@pytest.fixture(scope="session")
def context(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    yield koduck_context


@pytest.fixture(scope="session")
def context_with_emoji(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.param_line = "[szard]"
    yield koduck_context


@pytest.fixture(scope="function")
def patch_shuffle_db(monkeypatch: pytest.MonkeyPatch) -> None:
    _db = sqlite3.Connection(":memory:")
    _db.row_factory = db.dict_factory
    with open("queries/create_shuffle_tables.sql", encoding="utf-8") as f:
        query = f.read()
    _db.executescript(query)
    monkeypatch.setattr(db, "shuffle_connection", _db)


@pytest.fixture(scope="session")
def do_nothing() -> Iterator[Callable[..., Awaitable[None]]]:
    async def _do_nothing(*args: Any, **kwargs: Any) -> None:
        return

    yield _do_nothing
