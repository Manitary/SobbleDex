import discord

import settings
from koduck import KoduckContext


async def update_emojis(context: KoduckContext) -> None:
    assert context.koduck
    context.koduck.emojis = {}
    for server in context.koduck.client.guilds:
        if not (
            server.name.startswith("Pokemon Shuffle Icons")
            or server.id == settings.main_server_id
        ):
            continue
        for emoji in server.emojis:
            context.koduck.emojis[emoji.name.lower()] = f"<:{emoji.name}:{emoji.id}>"


async def emojify_2(context: KoduckContext) -> discord.Message | None:
    if not context.param_line:
        return
    return await context.send_message(content=context.param_line, check_aliases=True)
