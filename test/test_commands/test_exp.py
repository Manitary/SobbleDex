import pytest
from helper import check_payload_equal

import shuffle_commands
from koduck import KoduckContext
from models import Payload


@pytest.mark.asyncio
async def test_exp_no_arg(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context)
    expected = Payload(content="I need a BP and either one target level or two levels")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_invalid_bp(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "10")
    expected = Payload(content="BP should be a multiple of 10 between 30 and 90")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_40(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "40")
    expected = Payload(
        content=(
            "EXP table for 40 BP (Total EXP)\n"
            "```\n      0     55    165    330    495    990   1815   2805   3960   5280"
            "\n   6765   7920   9570  11550  13860  16335  18975  21780  24750  28050"
            "\n  31515  35145  38940  42900  47025  51315  55770  60390  65175  70125\n```"
            "EXP table for 40 BP (EXP from previous level)\n"
            "```\n      0     55    110    165    165    495    825    990   1155   1320"
            "\n   1485   1155   1650   1980   2310   2475   2640   2805   2970   3300"
            "\n   3465   3630   3795   3960   4125   4290   4455   4620   4785   4950\n```"
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_40_pokemon(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "Bulbasaur")
    expected = Payload(
        content=(
            "EXP table for 40 BP (Total EXP)\n"
            "```\n      0     55    165    330    495    990   1815   2805   3960   5280"
            "\n   6765   7920   9570  11550  13860  16335  18975  21780  24750  28050"
            "\n  31515  35145  38940  42900  47025  51315  55770  60390  65175  70125\n```"
            "EXP table for 40 BP (EXP from previous level)\n"
            "```\n      0     55    110    165    165    495    825    990   1155   1320"
            "\n   1485   1155   1650   1980   2310   2475   2640   2805   2970   3300"
            "\n   3465   3630   3795   3960   4125   4290   4455   4620   4785   4950\n```"
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_invalid_level_out_of_bound(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "30 31")
    expected = Payload(content="Level should be an integer between 1 and 30")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_invalid_level_not_int(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "30 test")
    expected = Payload(content="Level should be an integer between 1 and 30")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_30_20(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "30 20")
    expected = Payload(
        content="A 30 BP Pokemon needs 25500 EXP to get from Level 1 (AP 30) to Level 20 (AP 100)"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_90_30_pokemon(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "pkyogre 30")
    expected = Payload(
        content=(
            "Primal Kyogre (90 BP) needs 102000 EXP to get "
            "from Level 1 (AP 90) to Level 30 (AP 150)"
        )
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_80_5_15(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "80 5 15")
    expected = Payload(
        content="A 80 BP Pokemon needs 18225 EXP to get from Level 5 (AP 90) to Level 15 (AP 115)"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_exp_70_5_15_pokemon(context: KoduckContext) -> None:
    real = await shuffle_commands.exp(context, "Gallade 5 15")
    expected = Payload(
        content="Gallade (70 BP) needs 17010 EXP to get from Level 5 (AP 80) to Level 15 (AP 110)"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
