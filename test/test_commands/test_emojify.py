import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import emojify_2, update_emojis


@pytest.mark.asyncio
async def test_no_msg(context: KoduckContext) -> None:
    real = await emojify_2(context)
    expected = Payload()
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_msg(context_with_emoji: KoduckContext) -> None:
    real = await emojify_2(context_with_emoji)
    expected = Payload(content="[szard]", check_aliases=True)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_update_no_emoji(context: KoduckContext) -> None:
    await update_emojis(context)
    assert context.koduck
    assert context.koduck.emojis == {}
