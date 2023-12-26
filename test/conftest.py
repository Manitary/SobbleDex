import json
import shutil
import sqlite3
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterator, NotRequired, TypedDict

import discord
import pytest
from helper_models import MockAuthor, MockMessage

import db
from koduck import Koduck, KoduckContext
from models import QueryType, UserQuery

pytest.register_assert_rewrite("helper")

ASSETS_PATH = Path() / "test" / "assets"


def import_json_asset(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(name="koduck_instance", scope="function")
def _koduck_instance() -> Iterator[Koduck]:
    _koduck = Koduck()
    yield _koduck


@pytest.fixture(scope="function")
def context(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    yield koduck_context


@pytest.fixture(scope="function")
def context_with_fake_message(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.message = MockMessage(MockAuthor(1))
    yield koduck_context


@pytest.fixture(scope="function")
def context_with_fake_message_and_history(
    koduck_instance: Koduck,
) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.message = MockMessage(MockAuthor(1))
    koduck_context.koduck.query_history = {1: [UserQuery(QueryType.ANY, tuple())]}
    yield koduck_context


@pytest.fixture(scope="function")
def context_with_emoji(koduck_instance: Koduck) -> Iterator[KoduckContext]:
    koduck_context = KoduckContext()
    koduck_context.koduck = koduck_instance
    koduck_context.param_line = "[szard]"
    yield koduck_context


@pytest.fixture(scope="function")
def patch_shuffle_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    _db = sqlite3.Connection(":memory:")
    _db.row_factory = db.dict_factory
    with open("queries/create_shuffle_tables.sql", encoding="utf-8") as f:
        query = f.read()
    _db.executescript(query)
    monkeypatch.setattr(db, "shuffle_connection", _db)
    yield
    _db.close()


@pytest.fixture(name="db_copy", scope="session")
def _db_copy(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    tmp_dir = tmp_path_factory.mktemp("db_copy")
    original = db.DB_SHUFFLE_PATH
    new_path = tmp_dir / "shuffle_copy.sqlite"
    shutil.copy(original, new_path)
    yield new_path


@pytest.fixture(scope="function")
def patch_shuffle_db_wipe_reminders(
    monkeypatch: pytest.MonkeyPatch, db_copy: Path
) -> Iterator[None]:
    _db = sqlite3.Connection(db_copy)
    _db.row_factory = db.dict_factory
    _db.execute("DELETE FROM reminders")
    _db.execute("UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'reminders'")
    _db.commit()
    monkeypatch.setattr(db, "shuffle_connection", _db)
    yield
    _db.close()


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
    color: str | int
    description: NotRequired[str]
    fields: NotRequired[list[EmbedField]]


def parse_embed(embed_dict: EmbedDict) -> discord.Embed:
    colour = embed_dict["color"]
    if isinstance(colour, str):
        colour = int(colour[2:], 16)
    embed = discord.Embed(
        title=embed_dict["title"],
        color=colour,
        description=embed_dict.get("description", None),
    )
    for field in embed_dict.get("fields", []):
        embed.add_field(**field)
    return embed


WEEK_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "week_embeds.json"))
)


@pytest.fixture(params=enumerate(WEEK_EMBEDS, 1))
def week_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param


EB_REWARDS_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "eb_rewards_embeds.json"))
)


@pytest.fixture(params=enumerate(EB_REWARDS_EMBEDS, 1))
def eb_rewards_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param


EB_DETAILS_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "eb_details_embeds.json"))
)


@pytest.fixture(params=enumerate(EB_DETAILS_EMBEDS, 1))
def eb_details_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param
