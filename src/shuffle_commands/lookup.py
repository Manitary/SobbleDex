import asyncio
import difflib
import functools

import discord

import constants
import db
import settings
from koduck import KoduckContext


async def choice_react(
    context: KoduckContext, num_choices: int, question_string: str
) -> int | None:
    assert context.koduck

    num_choices = min(
        num_choices, settings.choice_react_limit, len(constants.number_emojis) - 1
    )
    the_message = await context.send_message(content=question_string)
    choice_emojis = constants.number_emojis[: num_choices + 1]

    # add reactions
    assert the_message
    for emoji in choice_emojis:
        await the_message.add_reaction(emoji)

    # wait for reaction (with timeout)
    def check(reaction: discord.Reaction, user: discord.User) -> bool:
        return (
            reaction.message.id == the_message.id
            and isinstance(context.message, discord.Message)
            and user == context.message.author
            and str(reaction.emoji) in choice_emojis
        )

    try:
        reaction, _ = await context.koduck.client.wait_for(
            "reaction_add", timeout=settings.dym_timeout, check=check
        )
    except asyncio.TimeoutError:
        reaction = None

    # remove reactions
    for emoji in choice_emojis:
        try:
            assert context.koduck.client.user
            await the_message.remove_reaction(emoji, context.koduck.client.user)
        except discord.errors.NotFound:
            break

    # return the chosen answer if there was one
    if reaction is None:
        return
    choice = choice_emojis.index(reaction.emoji)
    if choice == 0:
        return
    return choice - 1


async def lookup(
    context: KoduckContext,
    table: str,
    column: str,
    name: str,
    *args: str,
    _query: str = "",
    enable_dym: bool = True,
) -> str:
    """Return a corrected query of the required entry.

    Check if it exists as an alias, and/or in an additionally provided list.
    Provide some suggestions to the user if it does not.

    Currently used for pokemon and skills.

    ``table`` and ``column`` must match the values in the database,
    ``name`` is the term appearing in the bot message.

    Recommended to pre-fill them with ``functools.partial`` for easy re-use.
    """
    name = name or table
    _query = _query or args[0]
    aliases = db.get_aliases()
    _query = aliases.get(_query.lower(), _query)

    names_dict = {k.lower(): k for k in db.get_db_table_column(table, column)}

    if _query.lower() in names_dict:
        return names_dict[_query.lower()]

    if not enable_dym:
        return ""

    close_matches = difflib.get_close_matches(
        _query,
        set(aliases.keys()) | set(names_dict.values()),
        n=settings.dym_limit,
        cutoff=settings.dym_threshold,
    )

    if not close_matches:
        await context.send_message(
            content=settings.message_pokemon_lookup_no_result.format(name, _query),
        )
        return ""

    choices: list[tuple[str, str]] = []
    no_duplicates: list[str] = []
    for close_match in close_matches:
        alias = aliases.get(close_match, close_match)
        if alias.lower() not in no_duplicates:
            choices.append((close_match, alias))
            no_duplicates.append(alias.lower())

    output_string = "\n".join(
        f"{emoji} {choice[0]}" + f" ({choice[1]})" * (choice[0] != choice[1])
        for choice, emoji in zip(choices, constants.number_emojis[1:])
    )

    result = await choice_react(
        context,
        len(choices),
        "\n".join(
            (
                settings.message_pokemon_lookup_no_result.format(name, _query),
                settings.message_pokemon_lookup_suggest,
                output_string,
            )
        ),
    )
    if result is None:
        return ""
    return choices[result][1]


lookup_pokemon = functools.partial(
    lookup, table="pokemon", column="pokemon", name="Pokemon"
)
lookup_skill = functools.partial(lookup, table="skills", column="skill", name="Skill")
