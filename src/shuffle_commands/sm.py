import discord

import db
from koduck import KoduckContext


async def sm_rewards(context: KoduckContext) -> discord.Message | None:
    reward_list = db.get_sm_rewards()
    level = "\n".join(str(r.level) for r in reward_list)
    first_clear = "\n".join(f"[{r.reward}] x{r.amount}" for r in reward_list)
    repeat_clear = "\n".join(
        f"[{r.reward_repeat}] x{r.amount_repeat}" for r in reward_list
    )

    embed = discord.Embed(title="Survival Mode Rewards", color=0xFF0000)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="First Clear", value=first_clear, inline=True)
    embed.add_field(name="Repeat Clear", value=repeat_clear, inline=True)
    return await context.send_message(embed=embed)
