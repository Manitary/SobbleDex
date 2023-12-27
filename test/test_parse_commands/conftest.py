import functools
from typing import Any, AsyncIterator

import discord
import pytest
from helper_models import MockAuthor, MockMessage

from koduck import ClientWithBackgroundTask, Koduck, KoduckContext
from main import refresh_commands
from models import Payload

type CtxData = tuple[str, str, list[str], list[str], dict[str, str]]


async def _store_message(*args: Any, archive: list[Payload], **kwargs: Any) -> None:
    archive.append(
        Payload(
            content=kwargs.get("content", ""),
            embed=kwargs.get("embed", discord.Embed()),
        )
    )


def _context_log(ctx: KoduckContext, archive: list[CtxData]) -> None:
    archive.append((ctx.command, ctx.param_line, ctx.params, ctx.args, ctx.kwargs))


def _make_fake_user(self: ClientWithBackgroundTask, user: MockAuthor) -> MockAuthor:
    return user


def no_log(*args: Any, **kwargs: Any) -> None:
    pass


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def context_archive(
    koduck_instance: Koduck, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[tuple[KoduckContext, list[Payload], list[CtxData]]]:
    context = KoduckContext()
    context.koduck = koduck_instance
    fake_author = MockAuthor()
    context.message = MockMessage(author=fake_author)

    message_archive: list[Payload] = []
    context_data: list[CtxData] = []
    store_message = functools.partial(_store_message, archive=message_archive)
    make_fake_user = functools.partial(_make_fake_user, user=fake_author)
    context_log = functools.partial(_context_log, archive=context_data)

    monkeypatch.setattr(ClientWithBackgroundTask, "user", property(make_fake_user))
    monkeypatch.setattr(koduck_instance, "log", no_log)
    monkeypatch.setattr(koduck_instance, "send_message", store_message)
    monkeypatch.setattr(KoduckContext, "log", context_log)

    await refresh_commands(context)

    yield context, message_archive, context_data
