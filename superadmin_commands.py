from typing import Any

import discord

import settings
from koduck import KoduckContext


async def shutdown(context: KoduckContext, *args: str, **kwargs: Any) -> None:
    assert context.koduck
    return await context.koduck.client.close()


async def send_message(
    context: KoduckContext,
    channel_id: int,
    message_content: str,
    *args: str,
    **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    try:
        channel_id = int(channel_id)
    except ValueError:
        channel_id = -1
    the_channel = context.koduck.client.get_channel(channel_id)
    return await context.koduck.send_message(
        receive_message=context.message,
        channel=the_channel,
        content=message_content,
        ignore_cd=True,
    )


# note: discord server prevents any user, including bots, from changing usernames more than twice per hour
async def change_name(
    context: KoduckContext, username: str, *args: str, **kwargs: Any
) -> discord.ClientUser:
    assert context.koduck
    assert context.koduck.client.user
    return await context.koduck.client.user.edit(username=username)


async def change_status(context: KoduckContext, *args: str, **kwargs: Any) -> None:
    assert context.koduck
    if not context.param_line:
        return await context.koduck.client.change_presence(
            activity=discord.Game(name="")
        )
    return await context.koduck.client.change_presence(
        activity=discord.Game(name=context.param_line)
    )


# Updates any manual changes to the settings table
async def refresh_settings(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    context.koduck.refresh_settings()
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_refresh_settings_success,
    )


# Syncs the slash commands to Discord. This is not done automatically and should be done by running this command if changes were made to the slash commands.
async def refresh_app_commands(
    context: KoduckContext, *args: str, **kwargs: Any
) -> None:
    assert context.koduck
    await context.koduck.refresh_app_commands()
    await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_refresh_app_commands_success,
    )


async def add_admin(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context.message.raw_mentions) != 1:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_no_mentioned_user
        )

    user_id = context.message.raw_mentions[0]
    user_level = context.koduck.get_user_level(user_id)

    # already an admin
    if user_level == 2:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_add_admin_failed
        )

    context.koduck.update_user_level(user_id, 2)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_add_admin_success.format(user_id),
    )


async def remove_admin(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context.message.raw_mentions) != 1:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_no_mentioned_user
        )

    user_id = context.message.raw_mentions[0]
    user_level = context.koduck.get_user_level(user_id)

    # not an admin
    if user_level < 2:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_admin_failed,
        )

    context.koduck.update_user_level(user_id, 1)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_remove_admin_success.format(user_id),
    )


async def purge(
    context: KoduckContext, message_count: int, *args: str, **kwargs: Any
) -> discord.Message | None:
    """Search through the past settings.purge_search_limit number of messages in this channel
    and delete given number of bot messages"""
    assert context.koduck
    assert context.message
    try:
        limit = int(message_count)
    except (IndexError, ValueError):
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_purge_invalid_param,
        )
    counter = 0
    assert context.koduck.client.user
    async for message in context.message.channel.history(
        limit=settings.purge_search_limit
    ):
        if counter >= limit:
            break
        if message.author.id == context.koduck.client.user.id:
            await message.delete()
            counter += 1
