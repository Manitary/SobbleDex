import pytest
from helper import check_payload_equal

import shuffle_commands
from koduck import KoduckContext
from models import Payload


@pytest.mark.asyncio
async def test_no_arg(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context)
    expected = Payload(content="I need a BP and (optionally) a level")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_bp(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "14")
    expected = Payload(content="BP should be a multiple of 10 between 30 and 90")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_bp_multiple_args(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "14", "10")
    expected = Payload(content="BP should be a multiple of 10 between 30 and 90")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_invalid_level(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "30", "50")
    expected = Payload(content="Level should be an integer between 1 and 30")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_level_valid(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "30", "10")
    expected = Payload(content="55")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_level_with_spaces_valid(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "30 10")
    expected = Payload(content="55")
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_30(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "30")
    expected = Payload(
        content="``` 30  35  39  42  45  47  49  51  53  55\n"
        " 61  67  73  79  85  88  91  94  97 100\n"
        "102 104 106 108 110 112 114 116 118 120```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_40(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "40")
    expected = Payload(
        content="``` 40  43  46  48  50  52  54  56  58  60\n"
        " 66  72  78  84  90  93  96  99 102 105\n"
        "107 109 111 113 115 117 119 121 123 125```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_50(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "50")
    expected = Payload(
        content="``` 50  53  56  58  60  62  64  66  68  70\n"
        " 75  80  85  90 100 103 106 109 112 115\n"
        "116 117 118 119 120 122 124 126 128 130```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_60(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "60")
    expected = Payload(
        content="``` 60  63  66  68  70  72  74  76  78  80\n"
        " 84  88  92  96 105 108 111 114 117 120\n"
        "121 122 123 124 125 127 129 131 133 135```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_70(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "70")
    expected = Payload(
        content="``` 70  73  76  78  80  82  84  86  88  90\n"
        " 93  96  99 102 110 113 116 119 122 125\n"
        "126 127 128 129 130 132 134 136 138 140```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_80(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "80")
    expected = Payload(
        content="``` 80  83  86  88  90  92  94  96  98 100\n"
        "102 104 106 108 115 118 121 124 127 130\n"
        "131 132 133 134 135 137 139 141 143 145```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)


@pytest.mark.asyncio
async def test_ap_90(context: KoduckContext) -> None:
    real = await shuffle_commands.ap(context, "90")
    expected = Payload(
        content="``` 90  93  96  98 100 102 104 106 108 110\n"
        "112 114 116 118 120 123 126 129 132 135\n"
        "136 137 138 139 140 142 144 146 148 150```"
    )
    assert isinstance(real, dict)
    check_payload_equal(real, expected)
