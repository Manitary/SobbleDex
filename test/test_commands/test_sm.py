import discord
import pytest
from helper import check_payload_equal

from koduck import KoduckContext
from models import Payload
from shuffle_commands import sm_rewards


@pytest.mark.asyncio
async def test_sm(context: KoduckContext) -> None:
    real = await sm_rewards(context)
    embed = discord.Embed(title="Survival Mode Rewards", color=0xFF0000)
    embed.add_field(name="Level", value="10\n20\n25\n30\n35\n40\n45\n50\n55\n60")
    embed.add_field(
        name="First Clear",
        value=(
            "[EBM] x1\n[RML] x1\n[EBM] x1\n[RML] x1\n[EBL] x1\n"
            "[RML] x2\n[EBL] x1\n[RML] x5\n[SBL] x1\n[RML] x10"
        ),
    )
    embed.add_field(
        name="Repeat Clear",
        value=(
            "[EBS] x1\n[EBS] x2\n[EBS] x3\n[EBM] x1\n[EBM] x2"
            "\n[EBM] x2\n[EBM] x3\n[EBL] x1\n[EBL] x1\n[SBS] x1"
        ),
    )
    expected = Payload(embed=embed)
    check_payload_equal(real, expected)
