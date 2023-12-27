import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import query


@pytest.mark.asyncio
async def test_no_args(context: KoduckContext) -> None:
    real = await query(context)
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg(context: KoduckContext) -> None:
    real = await query(context, "test")
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_gt(context: KoduckContext) -> None:
    context.params = ["type>dragon"]
    real = await query(context, "type>dragon")
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_le(context: KoduckContext) -> None:
    context.params = ["type<=dragon"]
    real = await query(context, **{"type<": "dragon"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_type_eq_invalid(context: KoduckContext) -> None:
    context.params = ["type=test"]
    real = await query(context, **{"type": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_se_gt(context: KoduckContext) -> None:
    context.params = ["se>dragon"]
    real = await query(context, "se>dragon")
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_se_le(context: KoduckContext) -> None:
    context.params = ["se<=dragon"]
    real = await query(context, **{"se<": "dragon"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_bp_eq_invalid(context: KoduckContext) -> None:
    context.params = ["bp=test"]
    real = await query(context, **{"bp": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_rmls_gt_invalid(context: KoduckContext) -> None:
    context.params = ["rmls>test"]
    real = await query(context, **{"rmls>": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_maxap_eq_invalid(context: KoduckContext) -> None:
    context.params = ["maxap=test"]
    real = await query(context, **{"maxap": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_skill_le(context: KoduckContext) -> None:
    context.params = ["skill<=test"]
    real = await query(context, **{"skill<": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_evospeed_eq_invalid(context: KoduckContext) -> None:
    context.params = ["evospeed=test"]
    real = await query(context, **{"evospeed": "test"})
    expected = Payload(content="Sorry, I didn't recognize any of those filters")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
