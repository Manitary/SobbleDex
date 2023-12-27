from typing import Any, Awaitable, Callable, Iterator

import discord
import pytest
from assets import EB_DETAILS_EMBEDS, EB_REWARDS_EMBEDS, WEEK_EMBEDS
from helper_models import MockAuthor, MockMessage

from koduck import Koduck, KoduckContext
from models import QueryType, UserQuery

pytest.register_assert_rewrite("helper")


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


@pytest.fixture(scope="session")
def do_nothing() -> Iterator[Callable[..., Awaitable[None]]]:
    async def _do_nothing(*args: Any, **kwargs: Any) -> None:
        return

    yield _do_nothing


@pytest.fixture(params=enumerate(WEEK_EMBEDS, 1))
def week_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param


@pytest.fixture(params=enumerate(EB_REWARDS_EMBEDS, 1))
def eb_rewards_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param


@pytest.fixture(params=enumerate(EB_DETAILS_EMBEDS, 1))
def eb_details_embed(request: pytest.FixtureRequest) -> tuple[int, discord.Embed]:
    return request.param
