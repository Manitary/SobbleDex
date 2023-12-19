import settings
from koduck import KoduckContext
from models import Payload


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


async def emojify_2(context: KoduckContext) -> Payload:
    if not context.param_line:
        return Payload()
    return Payload(content=context.param_line, check_aliases=True)
