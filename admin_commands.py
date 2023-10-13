from typing import Any

import discord

import db
import settings
import user_commands
from koduck import KoduckContext


async def update_setting(
    context: KoduckContext, setting_name: str, new_value: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    result = context.koduck.update_setting(
        setting_name,
        new_value,
        context.koduck.get_user_level(context.message.author.id),
    )
    if result is None:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_update_setting_failed,
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_update_setting_success.format(
            setting_name, result, new_value
        ),
    )


async def add_setting(
    context: KoduckContext, setting_name: str, value: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    result = context.koduck.add_setting(
        setting_name, value, context.koduck.get_user_level(context.message.author.id)
    )
    if result is None:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_add_setting_failed
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_add_setting_success,
    )


async def remove_setting(
    context: KoduckContext, setting_name: str
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    result = context.koduck.remove_setting(
        setting_name, context.koduck.get_user_level(context.message.author.id)
    )
    if result is None:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_setting_failed,
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_remove_setting_success,
    )


async def restrict_user(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    assert context.message
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context.message.raw_mentions) != 1:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_no_mentioned_user
        )

    user_id = context.message.raw_mentions[0]
    user_level = context.koduck.get_user_level(user_id)

    # already restricted
    if user_level == 0:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_restrict_failed
        )
    # don't restrict high level users
    if user_level >= 2:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_restrict_failed_2.format(settings.bot_name),
        )
    context.koduck.update_user_level(user_id, 0)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_restrict_success.format(user_id, settings.bot_name),
    )


async def unrestrict_user(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    assert context.message
    # need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context.message.raw_mentions) != 1:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_no_mentioned_user
        )

    user_id = context.message.raw_mentions[0]
    user_level = context.koduck.get_user_level(user_id)

    if user_level != 0:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_unrestrict_failed
        )
    context.koduck.update_user_level(user_id, 1)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_unrestrict_success.format(user_id, settings.bot_name),
    )


async def add_response(
    context: KoduckContext, trigger: str, response: str
) -> discord.Message | None:
    assert context.koduck
    success = db.add_custom_response(trigger, response)
    if not success:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_add_response_failed,
        )
    context.koduck.add_command(trigger, user_commands.custom_response, "match", 1)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_add_response_success.format(trigger, response),
    )


async def remove_response(
    context: KoduckContext, trigger: str
) -> discord.Message | None:
    assert context.koduck
    success = db.remove_custom_response(trigger)
    if not success:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_response_failed.format(trigger),
        )
    context.koduck.remove_command(trigger)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_remove_response_success,
    )


async def change_nickname(
    context: KoduckContext, nickname: str = ""
) -> discord.Message | discord.Member | None:
    assert context.koduck
    assert context.message
    the_guild = context.message.guild
    if not the_guild:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_change_nickname_failed,
        )
    self_member = the_guild.me
    return await self_member.edit(nick=nickname)


async def add_requestable_roles(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    assert context.message
    if not context.message.role_mentions:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_add_requestable_roles_no_role,
        )
    assert context.message.guild
    guild_id = context.message.guild.id
    role_ids = (r.id for r in context.message.role_mentions)
    db.add_requestable_roles(guild_id, *role_ids)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_add_requestable_roles_success,
    )


async def remove_requestable_roles(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    assert context.message
    if not context.message.role_mentions:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_requestable_roles_no_role,
        )
    assert context.message.guild
    guild_id = context.message.guild.id
    role_ids = (r.id for r in context.message.role_mentions)
    db.remove_requestable_roles(guild_id, *role_ids)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_remove_requestable_roles_success,
    )
