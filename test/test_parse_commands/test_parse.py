import json
from pathlib import Path
from typing import AsyncIterator

import pytest

from koduck import KoduckContext, on_message
from models import Payload

type CtxData = tuple[str, str, list[str], list[str], dict[str, str]]
type Context_Payloads = tuple[KoduckContext, list[Payload], list[CtxData]]

SAMPLES_PATH = Path(__file__).resolve().parent.parent / "assets" / "user_queries.json"

with SAMPLES_PATH.open(encoding="utf-8") as f:
    QUERIES_SAMPLES: list[tuple[str, CtxData]] = json.load(f)


@pytest.mark.parametrize("user_msg, expected", QUERIES_SAMPLES)
@pytest.mark.asyncio
async def test_on_message(
    context_archive: AsyncIterator[Context_Payloads], user_msg: str, expected: CtxData
) -> None:
    context, _, context_data = await anext(context_archive)
    assert context.message
    context.message.content = user_msg
    await on_message(context.message)

    assert context_data[-1] == tuple(expected)


@pytest.mark.parametrize("user_msg", ("?test", '?"q" mega', '"?q mega"', " ?stage 1"))
@pytest.mark.asyncio
async def test_on_message_invalid(
    context_archive: AsyncIterator[Context_Payloads], user_msg: str
) -> None:
    context, _, context_data = await anext(context_archive)
    assert context.message
    context.message.content = user_msg
    await on_message(context.message)

    assert not context_data
