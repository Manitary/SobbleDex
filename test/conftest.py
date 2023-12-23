import json
import sqlite3
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterator, TypedDict

import discord
import pytest
from helper_models import MockAuthor, MockMessage

import db
from koduck import Koduck, KoduckContext

pytest.register_assert_rewrite("helper")

ASSETS_PATH = Path() / "test" / "assets"


def import_json_asset(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data


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
def context_with_fake_message(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.message = MockMessage(MockAuthor(1))
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


class EmbedField(TypedDict):
    name: str
    value: str
    inline: bool


class EmbedDict(TypedDict):
    title: str
    color: str
    fields: list[EmbedField]


def parse_embed(embed_dict: EmbedDict) -> discord.Embed:
    embed = discord.Embed(
        title=embed_dict["title"], color=int(embed_dict["color"][2:], 16)
    )
    for field in embed_dict["fields"]:
        embed.add_field(**field)
    return embed


WEEK_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "week_embeds.json"))
)


@pytest.fixture(params=enumerate(WEEK_EMBEDS, 1))
def week_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param
