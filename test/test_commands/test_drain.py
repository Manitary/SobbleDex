import pytest
from helper.helper_functions import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands.drain import drain_list


@pytest.mark.asyncio
async def test_no_args(context: KoduckContext) -> None:
    real = await drain_list(context)
    expected = Payload(content="I need HP and moves to calculate drain values!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_missing_arg_2(context: KoduckContext) -> None:
    real = await drain_list(context, "1000")
    expected = Payload(content="I need HP and moves to calculate drain values!")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_1(context: KoduckContext) -> None:
    real = await drain_list(context, "test", "10")
    expected = Payload(content="One of the arguments wasn't an integer greater than 0")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_2(context: KoduckContext) -> None:
    real = await drain_list(context, "1000", "-12")
    expected = Payload(content="One of the arguments wasn't an integer greater than 0")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_arg_2_too_high(context: KoduckContext) -> None:
    real = await drain_list(context, "1000", "56")
    expected = Payload(content="Moves has a limit of 55")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_args(context: KoduckContext) -> None:
    real = await drain_list(context, "10000", "3")
    content = (
        "```\n"
        "hp:    10000\n"
        "moves: 3\n\n"
        " 3:  1000 ( 10000 =>   9000)\n"
        " 2:   900 (  9000 =>   8100)\n"
        " 1:   810 (  8100 =>   7290)\n"
        "```"
    )
    expected = Payload(content=content)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_valid_args_with_space(context: KoduckContext) -> None:
    real = await drain_list(context, "9876543 10")
    content = (
        "```\n"
        "hp:    9876543\n"
        "moves: 10\n\n"
        "10: 987654 (9876543 => 8888889)\n"
        " 9: 888888 (8888889 => 8000001)\n"
        " 8: 800000 (8000001 => 7200001)\n"
        " 7: 720000 (7200001 => 6480001)\n"
        " 6: 648000 (6480001 => 5832001)\n"
        " 5: 583200 (5832001 => 5248801)\n"
        " 4: 524880 (5248801 => 4723921)\n"
        " 3: 472392 (4723921 => 4251529)\n"
        " 2: 425152 (4251529 => 3826377)\n"
        " 1: 382637 (3826377 => 3443740)\n"
        "```"
    )
    expected = Payload(content=content)
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
