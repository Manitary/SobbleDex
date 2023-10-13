import asyncio
import random
from collections import defaultdict
from typing import Iterable

import discord

import db
import settings
from koduck import KoduckContext
from models import RealCommand

DISCORD_ACTIVITIES = {
    discord.ActivityType.playing: "Playing",
    discord.ActivityType.streaming: "Streaming",
    discord.ActivityType.listening: "Listening",
    discord.ActivityType.watching: "Watching",
    discord.ActivityType.unknown: "unknown",
}


# When someone says a trigger message, respond with a custom response!
async def custom_response(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    response = db.query_custom_response(context.command)
    if response:
        return await context.koduck.send_message(
            receive_message=context.message, content=response[0]
        )


async def oops(context: KoduckContext) -> str:
    """Delete the last bot output triggered by the user.

    This information is tracked starting from bot startup,
    and only when koduck.send_message is used.
    """
    assert context.koduck
    assert context.message
    try:
        the_message = context.koduck.output_history[context.message.author.id].pop()
    except (KeyError, IndexError):
        return settings.message_oops_failed
    try:
        await the_message.delete()
        return settings.message_oops_success
    except discord.errors.NotFound:
        return await oops(context)


async def list_commands(context: KoduckContext) -> discord.Message | None:
    """List all commands that the user has permission to run.

    Group the commands by function. Multiple aliases are shown in parentheses.
    """
    assert context.koduck
    assert context.message
    current_level = context.koduck.get_user_level(context.message.author.id)

    available_commands: dict[RealCommand, list[str]] = defaultdict(list)

    for command_name, command in context.koduck.commands.items():
        if command.tier <= current_level and command.type == "prefix":
            available_commands[command].append(command_name)

    output = ", ".join(
        f"({', '.join(command_names)})" if len(command_names) > 1 else command_names[0]
        for command_names in available_commands.values()
    )
    return await context.koduck.send_message(
        receive_message=context.message, content=output
    )


async def help(context: KoduckContext, query: str = "") -> discord.Message | None:
    assert context.koduck
    help_message = get_help_message(query)
    if not help_message:
        help_message = get_help_message("unknown_command")
    return await context.koduck.send_message(
        receive_message=context.message, content=help_message
    )


def get_help_message(message_name: str) -> str:
    help_message = db.query_help_message(message_name)
    # Use {cp} for command prefix and {pd} for parameter delimiter
    return (
        help_message.replace("{cp}", settings.command_prefix)
        .replace("{pd}", settings.param_delim)
        .replace("\\n", "\n")
        .replace("\\t", "\t")
    )


async def user_info(context: KoduckContext) -> discord.Message | None:
    # if there is no mentioned user, use the message sender instead
    assert context.koduck
    assert context.message
    user = None
    if not context.message.raw_mentions:
        if context.message.guild is None:
            user = context.message.author
        else:
            user = context.message.guild.get_member(context.message.author.id)
            if user is None:
                user = context.message.author
    elif len(context.message.raw_mentions) == 1:
        if context.message.guild is None:
            user = context.koduck.client.get_user(context.message.raw_mentions[0])
        else:
            user = context.message.guild.get_member(context.message.raw_mentions[0])
            if user is None:
                user = context.koduck.client.get_user(context.message.raw_mentions[0])
    if not user or len(context.message.raw_mentions) > 1:
        return await context.koduck.send_message(
            context.message, content=settings.message_no_mentioned_user_2
        )

    username = user.name
    discriminator = user.discriminator
    avatar = user.display_avatar
    creation_date = user.created_at

    # if user is not in a server (i.e. User but not Member)
    if not isinstance(user, discord.Member):
        embed = discord.Embed(
            title=f"{username}#{discriminator}",
            description=f"Account creation date: {creation_date.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        )
        embed.set_thumbnail(url=avatar.url)
        return await context.koduck.send_message(
            receive_message=context.message, embed=embed
        )

    activities = user.activities
    join_date = user.joined_at
    color = user.color

    embed = discord.Embed(
        title=f"{username}#{discriminator}",
        description=str(user.status)
        if not activities
        else "\n".join(
            f"{activity}"
            if isinstance(activity, discord.CustomActivity)
            else f"{DISCORD_ACTIVITIES[activity.type]} {activity.name}"
            for activity in activities
        ),
        color=color,
    )
    embed.add_field(
        name="Account creation date",
        value=creation_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
        inline=False,
    )
    embed.add_field(
        name="Server join date",
        value=join_date.strftime("%Y-%m-%d %H:%M:%S UTC") if join_date else "Unknown",
        inline=False,
    )
    embed.set_thumbnail(url=avatar.url)
    return await context.koduck.send_message(
        receive_message=context.message, embed=embed
    )


async def roll(
    context: KoduckContext, max_value: int | str = ""
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    try:
        max_value = int(max_value)
    except ValueError:
        max_value = settings.roll_default_max

    if max_value >= 0:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_roll_result.format(
                context.message.author.mention, random.randint(0, max_value)
            ),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_roll_result.format(
            context.message.author.mention, random.randint(max_value, 0)
        ),
    )


async def request_roles(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    assert context.message

    if context.message.guild is None:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_request_roles_no_guild,
        )

    role_ids = set(db.query_requestable_roles(context.message.guild.id))

    if not role_ids:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_request_roles_no_roles,
        )

    requestable_roles = list(
        filter(None, map(context.message.guild.get_role, role_ids))
    )

    async def add_role(member: discord.Member, role_id: int) -> bool:
        assert context.message
        assert context.message.guild
        role = context.message.guild.get_role(role_id)
        if not role:
            return False
        try:
            await member.add_roles(role)
            return True
        except discord.errors.Forbidden:
            return False

    async def remove_role(member: discord.Member, role_id: int) -> bool:
        assert context.message
        assert context.message.guild
        role = context.message.guild.get_role(role_id)
        if not role:
            return False
        try:
            await member.remove_roles(role)
            return True
        except discord.errors.Forbidden:
            return False

    class RoleButton(discord.ui.Button[discord.ui.View]):
        role: discord.Role
        roles: list[discord.Role]

        async def callback(self, interaction: discord.Interaction) -> None:
            assert context.message
            assert interaction.message
            assert isinstance(context.message.author, discord.Member)
            assert isinstance(interaction.user, discord.Member)

            response_string = ""
            new_roles = context.message.author.roles

            # check user
            if interaction.user.id != context.message.author.id:
                response_string = (
                    interaction.user.mention
                    + " "
                    + settings.message_request_roles_wrong_user
                )
            else:
                # toggle role and update view
                if self.style == discord.ButtonStyle.success:
                    succeeded = await add_role(interaction.user, self.role.id)
                    if succeeded:
                        response_string = (
                            interaction.user.mention
                            + " "
                            + settings.message_request_roles_add_role_success.format(
                                self.label
                            )
                        )
                        new_roles.append(self.role)
                    else:
                        response_string = (
                            interaction.user.mention
                            + " "
                            + settings.message_request_roles_add_role_failed.format(
                                self.label
                            )
                        )
                elif self.style == discord.ButtonStyle.danger:
                    succeeded = await remove_role(interaction.user, self.role.id)
                    if succeeded:
                        response_string = (
                            interaction.user.mention
                            + " "
                            + settings.message_request_roles_remove_role_success.format(
                                self.label
                            )
                        )
                        new_roles.remove(self.role)
                    else:
                        response_string = (
                            interaction.user.mention
                            + " "
                            + settings.message_request_roles_remove_role_failed.format(
                                self.label
                            )
                        )

            new_message_content = interaction.message.content + "\n" + response_string
            new_view = create_view(self.roles, new_roles)
            await interaction.response.edit_message(
                content=new_message_content, view=new_view
            )

    def create_view(
        requestable_roles: Iterable[discord.Role], user_roles: Iterable[discord.Role]
    ) -> discord.ui.View:
        the_view = discord.ui.View(timeout=60)
        for role in requestable_roles:
            has_role = role in user_roles
            style = (
                discord.ButtonStyle.danger if has_role else discord.ButtonStyle.success
            )
            # button labels have 80 character limit, while role names have 100 character limit
            the_button = RoleButton(style=style, label=role.name[:80])
            the_button.roles = list(requestable_roles)
            the_button.role = role
            the_view.add_item(the_button)
        return the_view

    # set up initial view and send it
    assert isinstance(context.message.author, discord.Member)
    the_view = create_view(requestable_roles, context.message.author.roles)
    message_content = (
        context.message.author.mention + " " + settings.message_request_roles_start
    )
    the_message = await context.koduck.send_message(
        receive_message=context.message, content=message_content, view=the_view
    )
    timed_out = await the_view.wait()
    if timed_out:
        # re-fetch the message to get the latest message content
        assert the_message
        latest_message = await the_message.channel.fetch_message(the_message.id)
        message_content = (
            latest_message.content + "\n" + settings.message_request_roles_finished
        )
        await the_message.edit(content=message_content, view=None)


async def ping(interaction: discord.Interaction, delay: int) -> None:
    await interaction.response.defer(thinking=True)
    await asyncio.sleep(delay)
    await interaction.command.koduck.send_message(interaction, content="pong")
