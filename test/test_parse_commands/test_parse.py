from typing import AsyncIterator

import pytest

from koduck import KoduckContext, on_message
from models import Payload

type CtxData = tuple[str, str, list[str], list[str], dict[str, str]]
type Context_Payloads = tuple[KoduckContext, list[Payload], list[CtxData]]


@pytest.mark.parametrize(
    "user_msg, expected",
    [("?query rmls=7", ("query", "rmls=7", ["rmls=7"], list[str](), {"rmls": "7"}))],
)
@pytest.mark.asyncio
async def test_on_message(
    context_archive: AsyncIterator[Context_Payloads], user_msg: str, expected: CtxData
) -> None:
    context, _, context_data = await anext(context_archive)
    assert context.message
    context.message.content = user_msg
    await on_message(context.message)

    assert context_data[-1] == expected
