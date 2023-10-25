import asyncio
import datetime
import difflib
import itertools
import re
from collections import defaultdict
from math import floor
from typing import Any, Sequence

import discord
import pytz

import constants
import db
import embed_formatters
import settings
import utils
from koduck import Koduck, KoduckContext
from models import Param, PokemonType, Reminder, Stage, StageType

RE_PING = re.compile(r"<@!?[0-9]*>")


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
    assert context.koduck
    if not context.param_line:
        return
    return await context.koduck.send_message(
        receive_message=context.message, content=context.param_line, check_aliases=True
    )


async def add_alias(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if len(args) < 2:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_add_alias_no_param
        )
    if len(args) > settings.manage_alias_limit + 1:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_add_alias_too_many_params.format(
                settings.manage_alias_limit
            ),
        )

    aliases = db.get_aliases()
    original = aliases.get(args[0].lower(), args[0])
    new_aliases = args[1:]

    bad_alias = list(filter(lambda x: bool(RE_PING.findall(x)), new_aliases))
    success, duplicate, failure = db.add_aliases(
        original, *(a for a in new_aliases if a not in bad_alias)
    )
    return_message = "\n".join(
        itertools.chain(
            (settings.message_add_alias_success.format(original, s) for s in success),
            (
                settings.message_add_alias_failed.format(d, aliases[d.lower()])
                for d in duplicate
            ),
            (settings.message_add_alias_failed_2.format(f) for f in failure),
            (settings.message_add_alias_failed_3.format(b) for b in bad_alias),
        )
    )

    return await context.koduck.send_message(
        receive_message=context.message, content=return_message
    )


async def remove_alias(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_alias_no_param,
        )
    if len(args) > settings.manage_alias_limit:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remove_alias_too_many_params.format(
                settings.manage_alias_limit
            ),
        )

    success, not_exist, failure = db.remove_aliases(*args)
    return_message = "\n".join(
        itertools.chain(
            (settings.message_remove_alias_success.format(*s) for s in success),
            (settings.message_remove_alias_failed.format(n) for n in not_exist),
            (settings.message_remove_alias_failed_2.format(f) for f in failure),
        )
    )

    return await context.koduck.send_message(
        receive_message=context.message, content=return_message
    )


async def list_aliases(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if len(args) < 1:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_list_aliases_no_param,
        )

    # parse params
    aliases = db.get_aliases()
    original = aliases.get(args[0].lower(), args[0])

    # action
    results = [k for k, v in aliases.items() if v.lower() == original.lower()]
    if not results:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_list_aliases_no_result,
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_list_aliases_result.format(
            original, ", ".join(results)
        ),
    )


async def pokemon(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_pokemon_no_param
        )

    # parse params
    query_pokemon = await pokemon_lookup(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # retrieve data
    pokemon_ = db.query_pokemon(query_pokemon)
    if not pokemon_:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_pokemon_no_result.format(query_pokemon),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_pokemon_embed(pokemon_),
    )


async def skill(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_skill_no_param
        )

    # parse params
    query_skill = await pokemon_lookup(context, _query=args[0], skill_lookup=True)
    if not query_skill:
        print("Unrecognized Skill")
        return

    # retrieve data
    skill_ = db.query_skill(query_skill)
    if not skill_:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_skill_no_result.format(query_skill),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_skill_embed(skill_),
    )


async def ap(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_ap_no_param
        )

    query_bp = args[0]
    if not query_bp.isdigit() or query_bp not in map(str, range(30, 91, 10)):
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_ap_invalid_param
        )

    ap_list = db.query_ap(int(query_bp))

    if len(args) >= 2:
        try:
            query_level = int(args[1])
            assert 1 <= query_level <= 30
        except (ValueError, AssertionError):
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_ap_invalid_param_2,
            )
        return await context.koduck.send_message(
            receive_message=context.message, content=ap_list[query_level - 1]
        )
    else:
        desc = "```"
        for i, ap_ in enumerate(ap_list):
            if i % 10 == 0:
                desc += "\n"
            desc += f"{ap_} " if ap_ >= 100 else f" {ap_} "
        desc += "\n```"
        return await context.koduck.send_message(
            receive_message=context.message, content=desc
        )


async def exp(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_exp_no_param
        )

    # allow space delimited parameters
    if len(args) == 1:
        args = tuple(args[0].split())

    # parse params
    _query = args[0]
    query_pokemon = ""
    # ? split into two functions for digit and string?
    try:
        query_bp = int(_query)
        assert query_bp in range(30, 91, 10)
    except ValueError:
        query_pokemon = await pokemon_lookup(context, _query=_query)
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return
        pokemon_ = db.query_pokemon(query_pokemon)
        assert pokemon_
        query_bp = pokemon_.bp
    except AssertionError:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_exp_invalid_param,
        )

    exp_table = db.query_exp(query_bp)

    if len(args) == 1:
        desc = settings.message_exp_result_3.format(query_bp)
        desc += "\n```"
        for i, xp in enumerate(exp_table):
            if i % 10 == 0:
                desc += "\n"
            desc += str(xp).rjust(7)
        desc += "\n```"
        desc += settings.message_exp_result_4.format(query_bp)
        desc += "\n```"
        for i, (xp1, xp2) in enumerate(zip(exp_table, [0] + exp_table)):
            if i % 10 == 0:
                desc += "\n"
            desc += str(xp1 - xp2).rjust(7)
        desc += "\n```"
        return await context.koduck.send_message(
            receive_message=context.message, content=desc
        )

    try:
        query_level_1, query_level_2 = (
            (1, int(args[1])) if len(args) == 2 else (int(args[1]), int(args[2]))
        )
    except ValueError:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_exp_invalid_param_2,
        )

    if query_level_1 not in range(1, 31) or query_level_2 not in range(1, 31):
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_exp_invalid_param_2,
        )

    # retrieve data
    ap_table = db.query_ap(query_bp)
    start_exp = exp_table[query_level_1 - 1]
    end_exp = exp_table[query_level_2 - 1]
    start_ap = ap_table[query_level_1 - 1]
    end_ap = ap_table[query_level_2 - 1]

    if _query.isdigit():
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_exp_result.format(
                query_bp,
                end_exp - start_exp,
                query_level_1,
                start_ap,
                query_level_2,
                end_ap,
            ),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_exp_result_2.format(
            query_pokemon,
            query_bp,
            end_exp - start_exp,
            query_level_1,
            start_ap,
            query_level_2,
            end_ap,
        ),
    )


async def type(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_type_no_param
        )
    query_type = args[0].lower().capitalize()

    try:
        type_info = db.query_type(PokemonType(query_type))
    except ValueError:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_type_invalid_param
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_type_embed(type_info),
    )


async def stage(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_stage_no_param
        )

    # allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = ("".join(temp[:-1]), temp[-1])

    result_number = 0
    shorthand = kwargs.get("shorthand", False)
    stage_starting_board = kwargs.get("startingboard", False)

    # parse params
    stage_index = 0
    query_pokemon = args[0]
    if query_pokemon.isdigit():
        stage_type = StageType.MAIN
        stage_index = int(query_pokemon)
    elif query_pokemon.lower().startswith("ex") and query_pokemon[2:].isdigit():
        stage_type = StageType.EXPERT
        stage_index = int(query_pokemon[2:])
    elif query_pokemon.lower().startswith("s") and query_pokemon[1:].isdigit():
        stage_type = StageType.EVENT
        stage_index = int(query_pokemon[1:])
    else:
        stage_type = StageType.ALL

    if len(args) >= 2:
        try:
            result_number = int(args[1])
            if result_number <= 0:
                return await context.koduck.send_message(
                    receive_message=context.message,
                    content=settings.message_stage_invalid_param,
                )
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_stage_invalid_param,
            )

    results: list[Stage] = []
    # retrieve data
    if stage_type == StageType.MAIN:
        try:
            candidate_stage = db.query_stage_by_index(stage_index, stage_type)
            results.append(candidate_stage)
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_stage_main_invalid_param.format(
                    settings.main_stages_min_index, settings.main_stages_max_index
                ),
            )
    elif stage_type == StageType.EXPERT:
        try:
            candidate_stage = db.query_stage_by_index(stage_index, stage_type)
            results.append(candidate_stage)
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_stage_expert_invalid_param.format(
                    settings.expert_stages_min_index + 1,
                    settings.expert_stages_max_index + 1,
                ),
            )
    elif stage_type == StageType.EVENT:
        try:
            candidate_stage = db.query_stage_by_index(stage_index, stage_type)
            results.append(candidate_stage)
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_stage_event_invalid_param.format(
                    settings.event_stages_min_index, settings.event_stages_max_index
                ),
            )
    elif stage_type == StageType.ALL:
        query_pokemon = await pokemon_lookup(context, _query=query_pokemon)
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return

        # redirect to EB if queried pokemon is in EB table
        if db.query_eb_pokemon(query_pokemon):
            return await eb_details(context, *[query_pokemon], **kwargs)
        results = (
            list(db.query_stage_by_pokemon(query_pokemon, StageType.MAIN))
            + list(db.query_stage_by_pokemon(query_pokemon, StageType.EXPERT))
            + list(db.query_stage_by_pokemon(query_pokemon, StageType.EVENT))
        )

    if not results:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_stage_no_result.format(query_pokemon),
        )

    # if a result number is given
    if result_number:
        try:
            if stage_starting_board:
                return await context.koduck.send_message(
                    receive_message=context.message,
                    embed=embed_formatters.format_starting_board_embed(
                        results[result_number - 1]
                    ),
                )
            return await context.koduck.send_message(
                receive_message=context.message,
                embed=embed_formatters.format_stage_embed(
                    results[result_number - 1], shorthand=shorthand
                ),
            )
        except IndexError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_stage_result_error.format(len(results)),
            )

    if len(results) == 1:
        if stage_starting_board:
            return await context.koduck.send_message(
                receive_message=context.message,
                embed=embed_formatters.format_starting_board_embed(results[0]),
            )
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_stage_embed(results[0], shorthand=shorthand),
        )

    indices: list[str] = []
    output_string = ""
    for i, candidate_stage in enumerate(results):
        indices.append(candidate_stage.string_id)
        if i < settings.choice_react_limit:
            output_string += f"\n{constants.number_emojis[i + 1]} {indices[i]}"

    choice = await choice_react(
        context,
        min(len(indices), settings.choice_react_limit),
        settings.message_stage_multiple_results + output_string,
    )
    if choice is None:
        return
    if stage_starting_board:
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_starting_board_embed(results[choice]),
        )
    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_stage_embed(results[choice], shorthand=shorthand),
    )


async def stage_shorthand(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["shorthand"] = True
    return await stage(context, *args, **kwargs)


async def starting_board(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["startingboard"] = True
    return await stage(context, *args, **kwargs)


async def disruption_pattern(
    context: KoduckContext, *args: str
) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_dp_no_param
        )

    # parse params
    try:
        query_index = int(args[0])
        assert (
            query_index % 6 == 0
            and settings.disruption_patterns_min_index
            <= query_index
            <= settings.disruption_patterns_max_index
        )
    except (ValueError, AssertionError):
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_dp_invalid_param.format(
                settings.disruption_patterns_min_index,
                settings.disruption_patterns_max_index,
            ),
        )

    embed = discord.Embed()
    embed.set_image(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption Patterns/"
            f"Pattern Index {query_index}.png"
        ).replace(" ", "%20")
    )
    return await context.koduck.send_message(
        receive_message=context.message, embed=embed
    )


async def event(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_event_no_param
        )

    # allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = ("".join(temp[:-1]), temp[-1])

    result_number = 1

    # parse params
    if len(args) >= 2:
        try:
            result_number = int(args[1])
            if result_number <= 0:
                return await context.koduck.send_message(
                    receive_message=context.message,
                    content=settings.message_event_invalid_param,
                )
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_event_invalid_param,
            )
    query_pokemon = await pokemon_lookup(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # retrieve data
    events = list(db.query_event_by_pokemon(query_pokemon))

    if not events:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_event_result_error.format(len(events)),
        )

    try:
        selected_event = events[result_number - 1]
    except IndexError:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_event_no_result.format(query_pokemon),
        )

    if len(events) > 1:
        return await paginate_embeds(
            context,
            [embed_formatters.format_event_embed(e) for e in events],
            result_number,
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_event_embed(selected_event),
    )


async def paginate_embeds(
    context: KoduckContext, pages: Sequence[discord.Embed], initial_page: int = 1
) -> discord.Message | None:
    assert context.koduck
    current_page = initial_page
    the_message = await context.koduck.send_message(
        receive_message=context.message,
        content=f"Showing result {current_page} of {len(pages)}",
        embed=pages[current_page - 1],
    )
    assert the_message
    await the_message.add_reaction("⬅️")
    await the_message.add_reaction("➡️")

    while True:
        # wait for reaction (with timeout)
        def check(reaction: discord.Reaction, user: discord.User) -> bool:
            return (
                reaction.message.id == the_message.id
                and isinstance(context.message, discord.Message)
                and user == context.message.author
                and str(reaction.emoji) in ["⬅️", "➡️"]
            )

        try:
            reaction, _ = await context.koduck.client.wait_for(
                "reaction_add", timeout=settings.dym_timeout, check=check
            )
        except asyncio.TimeoutError:
            reaction = None

        # timeout
        if reaction is None:
            break

        # adjust page
        if reaction.emoji == "⬅️":
            current_page -= 1
        elif reaction.emoji == "➡️":
            current_page += 1

        # wrap
        if current_page < 1:
            current_page = len(pages)
        elif current_page > len(pages):
            current_page = 1

        await the_message.edit(
            content=f"Showing result {current_page} of {len(pages)}",
            embed=pages[current_page - 1],
        )

    # remove reactions
    try:
        assert context.koduck.client.user
        await the_message.remove_reaction("⬅️", context.koduck.client.user)
        await the_message.remove_reaction("➡️", context.koduck.client.user)
    except discord.errors.NotFound:
        pass

    return the_message


def validate_query(subqueries: list[str]) -> list[tuple[str, str, str]]:
    # allow space delimited parameters
    if len(subqueries) == 1 and len(subqueries[0].split("=")) > 2:
        subqueries = subqueries[0].split(" ")
        new_subqueries: list[str] = []
        for subquery in subqueries:
            operation = ""
            for op in [">=", "<=", "=>", "=<", ">", "<", "!=", "="]:
                if len(subquery.split(op)) == 2:
                    operation = op
                    break
            if operation == "" and len(new_subqueries) > 0:
                new_subqueries[-1] = new_subqueries[-1] + " " + subquery
            else:
                new_subqueries.append(subquery)
        subqueries = new_subqueries

    validated_queries: list[tuple[str, str, str]] = []
    for subquery in subqueries:
        subquery = subquery.strip()
        # accept five (seven) different operations
        operation = ""
        for op in [">=", "<=", "=>", "=<", ">", "<", "!=", "="]:
            if len(subquery.split(op)) == 2:
                operation = op
                break
        if operation == "":
            continue

        # split
        left = subquery.split(operation)[0].strip().lower()
        if left not in [
            "dex",
            "type",
            "bp",
            "rml",
            "rmls",
            "maxap",
            "skill",
            "sk",
            "sortby",
            "se",
            "evospeed",
            "megaspeed",
            "name",
        ]:
            continue
        if left in [
            "type",
            "skill",
            "sk",
            "sortby",
            "se",
            "name",
        ] and operation not in ["=", "!="]:
            continue

        right = subquery.split(operation)[1].strip()
        if right == "":
            continue

        # skills maybe used an alias
        if left in ["skill", "sk"]:
            right = utils.alias(right.lower())
        # make sure these are integers...
        elif left in ["dex", "bp", "rml", "rmls", "maxap", "evospeed", "megaspeed"]:
            try:
                _ = int(right)
            except ValueError:
                continue
        # make sure type and se are valid types
        elif left in ["type", "se"]:
            right = right.lower().capitalize()
            try:
                _ = PokemonType(right)
            except ValueError:
                continue

        validated_queries.append((left, operation, right))

    return validated_queries


def pokemon_filter_results_to_string(
    buckets: dict[Any, list[str]], use_emojis: bool = False
) -> str:
    farmable_pokemon = db.get_farmable_pokemon()
    output_string = ""
    for bucket_key, items in buckets.items():
        output_string += f"\n**{bucket_key}**: "
        for item in items:
            farmable = item.replace("**", "") in farmable_pokemon
            if use_emojis:
                try:
                    # surround ss pokemon with parentheses
                    # (instead of boldifying it, because, y'know... can't boldify emojis)
                    if item.find("**") != -1:
                        output_string += f"([{item.replace("**", "")}])"  # fmt: skip
                    else:
                        output_string += f"[{item}]"
                    if farmable:
                        output_string += "\\*"
                except KeyError:
                    output_string += "{}{} ".format(
                        "**" + item if item.find("**") != -1 else item,
                        "\\*" if farmable else "",
                    )
            else:
                output_string += "{}{}, ".format(
                    "**" + item if item.find("**") != -1 else item,
                    "\\*" if farmable else "",
                )
        if not use_emojis:
            output_string = output_string[:-2]
    return output_string


async def query(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    use_emojis = kwargs.get("useemojis", False)
    queries = validate_query(context["params"])

    farmable = Param.IGNORE
    if "farmable" in args:
        farmable = Param.INCLUDE
    if "!farmable" in args:
        farmable = Param.EXCLUDE
    if "?farmable" in args:
        #! double check this
        farmable = Param.IGNORE
    if "farmable" in kwargs:
        if kwargs["farmable"] == "yes":
            farmable = Param.INCLUDE
        elif kwargs["farmable"] == "no":
            farmable = Param.EXCLUDE
        elif kwargs["farmable"] == "both":
            farmable = Param.IGNORE

    ss_filter = Param.IGNORE
    if "ss" in args:
        ss_filter = Param.INCLUDE
    if "!ss" in args:
        ss_filter = Param.EXCLUDE
    if "ss" in kwargs:
        if kwargs["ss"] == "yes":
            ss_filter = Param.INCLUDE
        elif kwargs["ss"] == "no":
            ss_filter = Param.EXCLUDE

    # force mega if evospeed is used
    if (
        "evospeed" in (x[0] for x in queries)
        or "evospeed" in (x[2] for x in queries if x[0] == "sortby")
        or "megaspeed" in (x[0] for x in queries)
        or "megaspeed" in (x[2] for x in queries if x[0] == "sortby")
    ):
        kwargs["mega"] = True

    # generate a string to show which filters were recognized
    query_string = ""
    if "mega" in args or "mega" in kwargs:
        query_string += "mega and "

    if "hasmega" in args or "hasmega" in kwargs:
        query_string += "hasmega and "

    if farmable == Param.INCLUDE:
        query_string += "farmable and "
    elif farmable == Param.EXCLUDE:
        query_string += "not farmable and "

    if ss_filter == Param.INCLUDE:
        query_string += "only-SS and "
    elif ss_filter == Param.EXCLUDE:
        query_string += "no-SS and "

    sortby = ""
    for left, operation, right in queries:
        if not right:
            continue
        query_string += f"{left}{operation}{right} and "
        if left == "sortby":
            sortby = right

    if not query_string:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_query_invalid_param,
        )

    query_string = query_string[:-5]

    hits, hits_bp, hits_max_ap, hits_type, hits_evo_speed = pokemon_filter(
        queries,
        "mega" in args or "mega" in kwargs,
        "fake" in args or "fake" in kwargs,
        farmable,
        ss_filter,
        "hasmega" in args or "hasmega" in kwargs,
    )

    # format output depending on which property to sort by
    if sortby == "bp":
        buckets = {k: sorted(v) for k, v in sorted(hits_bp.items())}
        sortby_string = "BP"
    elif sortby == "type":
        buckets = {k: sorted(v) for k, v in sorted(hits_type.items())}
        sortby_string = "Type"
    elif sortby in ["evospeed", "megaspeed"] and ("mega" in args or "mega" in kwargs):
        buckets = {k: sorted(v) for k, v in sorted(hits_evo_speed.items())}
        sortby_string = "Mega Evolution Speed"
    else:
        buckets = {k: sorted(v) for k, v in sorted(hits_max_ap.items())}
        sortby_string = "Max AP"

    # sort results and create a string to send
    header = settings.message_query_result.format(
        len(hits), query_string, sortby_string
    )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_query_results_embed(header, buckets, use_emojis),
    )


async def query_with_emojis(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["useemojis"] = True
    return await query(context, *args, **kwargs)


async def skill_with_pokemon(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    use_emojis = kwargs.get("useemojis", False)

    if not args:
        return await context.koduck.send_message(
            receive_message=context.message, content=settings.message_skill_no_param
        )

    query_skill = args[0]

    # lookup and validate skill
    query_skill = await pokemon_lookup(context, _query=query_skill, skill_lookup=True)
    if not query_skill:
        print("Unrecognized Skill")
        return

    # retrieve skill data
    skill_ = db.query_skill(query_skill)
    if not skill_:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_skill_no_result.format(query_skill),
        )

    copy_of_params = context["params"].copy()
    copy_of_params.remove(args[0])
    queries = validate_query(copy_of_params)

    farmable = Param.IGNORE
    if "farmable" in args:
        farmable = Param.INCLUDE
    if "!farmable" in args:
        farmable = Param.EXCLUDE
    if "?farmable" in args:
        #! double check again the meaning of this
        farmable = Param.IGNORE
    if "farmable" in kwargs:
        if kwargs["farmable"] == "yes":
            farmable = Param.INCLUDE
        elif kwargs["farmable"] == "no":
            farmable = Param.EXCLUDE
        elif kwargs["farmable"] == "both":
            farmable = Param.IGNORE

    ss_filter = Param.IGNORE
    if "ss" in args:
        ss_filter = Param.INCLUDE
    if "!ss" in args:
        ss_filter = Param.EXCLUDE
    if "ss" in kwargs:
        if kwargs["ss"] == "yes":
            ss_filter = Param.INCLUDE
        elif kwargs["ss"] == "no":
            ss_filter = Param.EXCLUDE

    # force mega if evospeed is used
    if (
        "evospeed" in (x[0] for x in queries)
        or "evospeed" in (x[2] for x in queries if x[0] == "sortby")
        or "megaspeed" in (x[0] for x in queries)
        or "megaspeed" in (x[2] for x in queries if x[0] == "sortby")
    ):
        kwargs["mega"] = True

    # generate a string to show which filters were recognized
    query_string = ""
    if "mega" in args or "mega" in kwargs:
        query_string += "mega and "
    if "hasmega" in args or "hasmega" in kwargs:
        query_string += "hasmega and "
    if farmable == Param.INCLUDE:
        query_string += "farmable and "
    elif farmable == Param.EXCLUDE:
        query_string += "not farmable and "

    if ss_filter == Param.INCLUDE:
        query_string += "only-SS and "
    elif ss_filter == Param.EXCLUDE:
        query_string += "no-SS and "

    sortby = ""
    for left, operation, right in queries:
        if not right:
            continue
        query_string += f"{left}{operation}{right} and "
        if left == "sortby":
            sortby = right

    if query_string:
        query_string = query_string[:-5]

    # query for pokemon with this skill
    queries.append(("skill", "=", skill_.skill))
    hits, hits_bp, hits_max_ap, hits_type, hits_evo_speed = pokemon_filter(
        queries,
        "mega" in args or "mega" in kwargs,
        "fake" in args or "fake" in kwargs,
        farmable,
        ss_filter,
        "hasmega" in args or "hasmega" in kwargs,
    )

    # format output
    if not hits:
        field_value = "None"
        sortby_string = ""
    else:
        # format output depending on which property to sort by (default maxap)
        if sortby == "bp":
            buckets = {k: sorted(v) for k, v in sorted(hits_bp.items())}
            sortby_string = "BP"
        elif sortby == "type":
            buckets = {k: sorted(v) for k, v in sorted(hits_type.items())}
            sortby_string = "Type"
        elif sortby in ["evospeed", "megaspeed"] and (
            "mega" in args or "mega" in kwargs
        ):
            buckets = {k: sorted(v) for k, v in sorted(hits_evo_speed.items())}
            sortby_string = "Mega Evolution Speed"
        else:
            buckets = {k: sorted(v) for k, v in sorted(hits_max_ap.items())}
            sortby_string = "Max AP"
        field_value = pokemon_filter_results_to_string(buckets, use_emojis)

    field_name = "Pokemon with this skill{}{}".format(
        f" ({query_string})" if query_string else "",
        f" sorted by {sortby_string}" if sortby_string else "",
    )

    embed = embed_formatters.format_skill_embed(skill_)
    embed.add_field(name=field_name, value=field_value)

    return await context.koduck.send_message(
        receive_message=context.message, embed=embed
    )


async def skill_with_pokemon_with_emojis(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["useemojis"] = True
    return await skill_with_pokemon(context, *args, **kwargs)


# Helper function for query command
# farmable/ss_filter: 0 = ignore, 1 = include, 2 = exclude
def pokemon_filter(
    queries: list[tuple[str, str, str]],
    mega: bool = False,
    include_fake: bool = False,
    farmable: Param = Param.IGNORE,
    ss_filter: Param = Param.IGNORE,
    has_mega: bool = False,
) -> tuple[
    list[str],
    dict[int, list[str]],
    dict[int, list[str]],
    dict[PokemonType, list[str]],
    dict[int, list[str]],
]:
    hits: list[str] = []
    hits_bp: dict[int, list[str]] = defaultdict(list)
    hits_max_ap: dict[int, list[str]] = defaultdict(list)
    hits_type: dict[PokemonType, list[str]] = defaultdict(list)
    hits_evo_speed: dict[int, list[str]] = defaultdict(list)

    se_types = set(
        itertools.chain(
            *(
                db.query_weak_against(PokemonType(right))
                for left, _, right in queries
                if left == "se"
            )
        )
    )

    farmable_pokemon: set[str] = (
        db.get_farmable_pokemon() if farmable != Param.IGNORE else set()
    )

    all_pokemon_names = db.get_pokemon_names()

    # check each pokemon
    for pokemon_ in db.get_all_pokemon():
        if mega ^ bool(pokemon_.mega_power):
            continue
        # ? add a has_mega field in the pokemon table?
        # ? or another table to map pokemon -> mega pokemon
        if has_mega and pokemon_.pokemon in [
            "Charizard",
            "Mewtwo",
            "Charizard (Shiny)",
        ]:
            pass
        elif has_mega and f"Mega {pokemon_.pokemon}" not in all_pokemon_names:
            continue

        if not include_fake and pokemon_.fake:
            continue

        if farmable == Param.INCLUDE and pokemon_.pokemon not in farmable_pokemon:
            continue
        if farmable == Param.EXCLUDE and pokemon_.pokemon in farmable_pokemon:
            continue

        temp_ss = list(map(str.lower, pokemon_.ss_skills))

        result = True
        is_ss = False
        # TODO do this less painfully
        for subquery in queries:
            left, operation, right = subquery

            if (left == "dex") and (
                (operation in [">=", "=>"] and pokemon_.dex < int(right))
                or (operation in ["<=", "=<"] and pokemon_.dex > int(right))
                or (operation == ">" and pokemon_.dex <= int(right))
                or (operation == "<" and pokemon_.dex >= int(right))
                or (operation == "=" and pokemon_.dex != int(right))
                or (operation == "!=" and pokemon_.dex == int(right))
            ):
                result = False
                break
            if (left == "bp") and (
                (operation in [">=", "=>"] and pokemon_.bp < int(right))
                or (operation in ["<=", "=<"] and pokemon_.bp > int(right))
                or (operation == ">" and pokemon_.bp <= int(right))
                or (operation == "<" and pokemon_.bp >= int(right))
                or (operation == "=" and pokemon_.bp != int(right))
                or (operation == "!=" and pokemon_.bp == int(right))
            ):
                result = False
                break
            if (left in ["rml", "rmls"]) and (
                (operation in [">=", "=>"] and pokemon_.rml < int(right))
                or (operation in ["<=", "=<"] and pokemon_.rml > int(right))
                or (operation == ">" and pokemon_.rml <= int(right))
                or (operation == "<" and pokemon_.rml >= int(right))
                or (operation == "=" and pokemon_.rml != int(right))
                or (operation == "!=" and pokemon_.rml == int(right))
            ):
                result = False
                break
            if (left == "maxap") and (
                (operation in [">=", "=>"] and pokemon_.max_ap < int(right))
                or (operation in ["<=", "=<"] and pokemon_.max_ap > int(right))
                or (operation == ">" and pokemon_.max_ap <= int(right))
                or (operation == "<" and pokemon_.max_ap >= int(right))
                or (operation == "=" and pokemon_.max_ap != int(right))
                or (operation == "!=" and pokemon_.max_ap == int(right))
            ):
                result = False
                break
            if (left == "type") and (
                (operation == "=" and right.lower() != pokemon_.type.lower())
                or (operation == "!=" and right.lower() == pokemon_.type.lower())
            ):
                result = False
                break
            if (left == "se") and (
                (operation == "=" and pokemon_.type not in se_types)
                or (operation == "!=" and pokemon_.type in se_types)
            ):
                result = False
                break
            if (left in ["skill", "sk"]) and (
                (
                    operation == "="
                    and right.lower() != pokemon_.skill.lower()
                    and right.lower() not in temp_ss
                )
                or (
                    operation == "!="
                    and (
                        right.lower() == pokemon_.skill.lower()
                        or right.lower() in temp_ss
                    )
                )
            ):
                result = False
                break
            if (
                left in ["skill", "sk"]
                and operation == "="
                and right.lower() in temp_ss
            ):
                is_ss = True
                if ss_filter == Param.EXCLUDE:
                    result = False
            else:
                if ss_filter == Param.INCLUDE:
                    result = False
            if (left in ["evospeed", "megaspeed"]) and (
                (operation in [">=", "=>"] and pokemon_.evo_speed < int(right))
                or (operation in ["<=", "=<"] and pokemon_.evo_speed > int(right))
                or (operation == ">" and pokemon_.evo_speed <= int(right))
                or (operation == "<" and pokemon_.evo_speed >= int(right))
                or (operation == "=" and pokemon_.evo_speed != int(right))
                or (operation == "!=" and pokemon_.evo_speed == int(right))
            ):
                result = False
                break
            if (left == "name") and (
                (operation == "=" and right.lower() not in pokemon_.pokemon.lower())
                or (operation == "!=" and (right.lower() in pokemon_.pokemon.lower()))
            ):
                result = False
                break
        if not result:
            continue

        # if skill is used, boldify pokemon with ss
        # it can't start with ** because it needs to be sorted by name
        hit_name = f"{pokemon_.pokemon}**" if is_ss else pokemon_.pokemon

        #! farmable == 3 is not an option described in the previous documentation
        #! the goal is to tag farmable with *, but apparently it's done by default anyway?
        if farmable == 3 and pokemon_.pokemon in farmable_pokemon:
            hit_name += "\\*"

        hits_bp[pokemon_.bp].append(hit_name)
        hits_max_ap[pokemon_.max_ap].append(hit_name)
        hits_type[pokemon_.type].append(hit_name)
        hits_evo_speed[pokemon_.evo_speed].append(hit_name)
        hits.append(hit_name)

    return (hits, hits_bp, hits_max_ap, hits_type, hits_evo_speed)


async def eb_rewards(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        query_pokemon = utils.current_eb_pokemon()
    else:
        # parse params
        query_pokemon = await pokemon_lookup(context, _query=args[0])
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return

    # retrieve data
    _eb_rewards = db.query_eb_rewards_pokemon(query_pokemon)
    if not _eb_rewards:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_eb_rewards_no_result.format(query_pokemon),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_eb_rewards_embed(_eb_rewards),
    )


async def eb_details(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    if not args or args[0].isdigit():
        eb_pokemon = utils.current_eb_pokemon()
        args = (eb_pokemon,) + args

    # allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = (" ".join(temp[:-1]), temp[-1])

    query_level = 0
    if len(args) >= 2:
        query_level = args[1]
        try:
            if int(query_level) <= 0:
                return await context.koduck.send_message(
                    receive_message=context.message,
                    content=settings.message_eb_invalid_param,
                )
            query_level = int(query_level)
        except ValueError:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_eb_invalid_param,
            )

    # parse params
    query_pokemon = await pokemon_lookup(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # verify that queried pokemon is in EB table
    eb_details_2 = db.query_eb_pokemon(query_pokemon)
    if not eb_details_2:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_eb_no_result.format(query_pokemon),
        )

    # optional level param which will return a stage embed instead
    if query_level <= 0:
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_eb_details_embed(eb_details_2),
        )

    leg = next(x for x in eb_details_2 if x.end_level < 0 or x.end_level > query_level)
    # extra string to show level range of this eb stage
    if leg.start_level == leg.end_level - 1:
        level_range = f" (Level {leg.start_level})"
    elif leg.end_level < 0:
        level_range = f" (Levels {leg.start_level}+ ({query_level}))"
    else:
        level_range = (
            f" (Levels {leg.start_level} to {leg.end_level-1} ({query_level}))"
        )

    delta = query_level - leg.start_level

    shorthand = kwargs.get("shorthand", False)
    eb_starting_board = kwargs.get("startingboard", False)

    eb_stage = db.query_stage_by_index(leg.stage_index, StageType.EVENT)
    _eb_rewards = db.query_eb_rewards_pokemon(query_pokemon)
    eb_reward = ""
    for entry in _eb_rewards:
        if entry.level == query_level:
            eb_reward = f"[{entry.reward}] x{entry.amount} {entry.alternative}"
            break

    if eb_starting_board:
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_starting_board_embed(eb_stage),
        )
    else:
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_stage_embed(
                eb_stage,
                eb_data=(level_range, delta, eb_reward, query_level),
                shorthand=shorthand,
            ),
        )


async def eb_details_shorthand(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["shorthand"] = True
    return await eb_details(context, *args, **kwargs)


async def week(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    curr_week = utils.get_current_week()
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message,
            embed=embed_formatters.format_week_embed(curr_week),
        )

    if args[0].isdigit():
        query_week = int(args[0])
    else:
        query_pokemon = await pokemon_lookup(context, _query=args[0])
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return

        # retrieve data
        weeks = [
            event.repeat_param_1 for event in db.query_event_by_pokemon(query_pokemon)
        ]
        if not weeks:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_event_no_result.format(query_pokemon),
            )
        sorted_results = [w + 1 for w in weeks if w + 1 >= curr_week] + [
            w + 1 for w in weeks if w + 1 < curr_week
        ]
        query_week = sorted_results[0]

    if not 1 <= query_week <= settings.num_weeks:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_week_invalid_param.format(
                settings.num_weeks, settings.num_weeks
            ),
        )

    return await context.koduck.send_message(
        receive_message=context.message,
        embed=embed_formatters.format_week_embed(query_week),
    )


async def next_week(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    args = (str(utils.get_current_week() % 24 + 1),)
    return await week(context, *args, **kwargs)


async def sm_rewards(context: KoduckContext) -> discord.Message | None:
    assert context.koduck
    reward_list = db.get_sm_rewards()
    level = "\n".join(str(reward.level) for reward in reward_list)
    first_clear = "\n".join(f"[{r.reward}] x{r.amount}" for r in reward_list)
    repeat_clear = "\n".join(
        f"[{r.reward_repeat}] x{r.amount_repeat}" for r in reward_list
    )

    embed = discord.Embed(title="Survival Mode Rewards", color=0xFF0000)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="First Clear", value=first_clear, inline=True)
    embed.add_field(name="Repeat Clear", value=repeat_clear, inline=True)
    return await context.koduck.send_message(
        receive_message=context.message, embed=embed
    )


async def drain_list(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    # allow space delimited parameters
    if len(args) == 1:
        args = tuple(args[0].split(" "))

    # first arg script name, second arg hp, third arg moves
    if len(args) != 2:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_drain_list_no_param,
        )

    try:
        hp = int(args[0])
        moves = int(args[1])
        assert hp > 0 and moves > 0
    except (ValueError, AssertionError):
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_drain_list_invalid_param,
        )

    if moves > 55:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_drain_list_invalid_param_2,
        )

    output = f"```\nhp:    {hp}\nmoves: {moves}\n\n"

    for i in range(moves):
        drain_amount = int(floor(float(hp) * 0.1))
        output += f"{moves-i:>2}: {drain_amount:>5} ({hp:>6} => {hp-drain_amount:>6})\n"
        hp -= drain_amount

    output += "```"

    return await context.koduck.send_message(
        receive_message=context.message, content=output
    )


# ? Split skill_lookup?
async def pokemon_lookup(
    context: KoduckContext,
    *args: str,
    _query: str = "",
    enable_dym: bool = True,
    skill_lookup: bool = False,
) -> str:
    """Return a corrected query of the required pokemon/skill.

    Check if it exists as an alias, and/or in an additionally provided list.
    Provide some suggestions to the user if it does not."""
    assert context.koduck
    _query = _query or args[0]
    aliases = db.get_aliases()
    _query = aliases.get(_query.lower(), _query)

    pokemon_dict = {k.lower(): k for k in db.get_pokemon_names()}
    skill_dict = {k.lower(): k for k in db.get_skill_names()}
    # get properly capitalized name
    _query = (
        skill_dict.get(_query.lower(), _query)
        if skill_lookup
        else pokemon_dict.get(_query.lower(), _query)
    )
    try:
        _query = (
            skill_dict[_query.lower()] if skill_lookup else pokemon_dict[_query.lower()]
        )
        found = True
    except KeyError:
        found = False

    if found:
        return _query

    if not enable_dym:
        return ""

    add = skill_dict.values() if skill_lookup else pokemon_dict.values()

    close_matches = difflib.get_close_matches(
        _query,
        list(aliases.keys()) + list(add),
        n=settings.dym_limit,
        cutoff=settings.dym_threshold,
    )

    if not close_matches:
        await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_pokemon_lookup_no_result.format(
                "Skill" if skill_lookup else "Pokemon", _query
            ),
        )
        return ""

    choices: list[tuple[str, str]] = []
    no_duplicates: list[str] = []
    for close_match in close_matches:
        alias = aliases.get(close_match, close_match).lower()
        if alias not in no_duplicates:
            choices.append((close_match, alias))
            no_duplicates.append(close_match.lower())

    output_string = ""
    for i, choice in enumerate(choices):
        output_string += (
            f"\n{constants.number_emojis[i + 1]} {choice[0]}" + ""
            if choice[0] == choice[1]
            else f" ({choice[1]})"
        )

    result = await choice_react(
        context,
        len(choices),
        settings.message_pokemon_lookup_no_result.format(
            "Skill" if skill_lookup else "Pokemon", _query
        )
        + "\n"
        + settings.message_pokemon_lookup_suggest
        + output_string,
    )
    if result is None:
        return ""
    return choices[result][1]


#! WIP never finished
# async def submit_comp_score(context, *args, **kwargs):
#     if len(args) < 3:
#         return await context.koduck.send_message(
#             receive_message=context.message,
#             content=settings.message_submit_comp_score_no_param,
#         )

#     # parse and check competition pokemon
#     query_pokemon = await pokemon_lookup(context, query=args[0])
#     if query_pokemon is None:
#         return "Unrecognized Pokemon"
#     comp_pokemon = set()
#     for values in yadon.ReadTable(settings.events_table).values():
#         if values[0] == "Competitive":
#             comp_pokemon.add(values[1])
#     if query_pokemon not in comp_pokemon:
#         return await context.koduck.send_message(
#             receive_message=context.message,
#             content=settings.message_submit_comp_score_no_result.format(query_pokemon),
#         )

#     # verify score is an integer > 0
#     if not args[1].isdigit():
#         return await context.koduck.send_message(
#             receive_message=context.message,
#             content=settings.message_submit_comp_score_invalid_param,
#         )
#     score = int(args[1])

#     # very screenshot link
#     link = args[2]
#     if not link.startswith("https://cdn.discordapp.com/attachments/"):
#         return await context.koduck.send_message(
#             receive_message=context.message,
#             content=settings.message_submit_comp_score_invalid_param_2,
#         )

#     yadon.WriteRowToTable(
#         settings.comp_scores_table,
#         settings.current_comp_score_id,
#         {
#             "User ID": context.message.author.id,
#             "Competition Pokemon": query_pokemon,
#             "Score": score,
#             "URL": link,
#             "Verified": 0,
#         },
#         named_columns=True,
#     )
#     context.koduck.update_setting(
#         "current_comp_score_id",
#         settings.current_comp_score_id + 1,
#         settings.max_user_level,
#     )
#     return await context.koduck.send_message(
#         receive_message=context.message,
#         content=settings.message_submit_comp_score_success,
#     )


# async def comp_scores(context, *args, **kwargs):
#     user_id = context.message.author.id
#     user_tag = "{}#{}".format(
#         context.message.author.name, context.message.author.discriminator
#     )
#     comp_scores = yadon.ReadTable(settings.comp_scores_table, named_columns=True)
#     user_comp_scores = [x for x in comp_scores.values() if int(x["User ID"]) == user_id]
#     if len(user_comp_scores) == 0:
#         return await context.koduck.send_message(
#             receive_message=context.message,
#             content=settings.message_comp_scores_no_result.format(user_tag),
#         )

#     user_comp_scores = sorted(
#         user_comp_scores, key=lambda comp_score: comp_score["Score"]
#     )
#     comp_scores_string = "``Competition Pokemon\tScore\tVerified\tURL``"
#     for comp_score in user_comp_scores:
#         comp_scores_string += "\n``{}\t{}\t{}\t``[link]({})".format(
#             comp_score["Competition Pokemon"],
#             comp_score["Score"],
#             "Yes" if int(comp_score["Verified"]) else "No",
#             comp_score["URL"],
#         )
#     embed = discord.Embed(
#         title=settings.message_comp_scores.format(user_tag),
#         description=comp_scores_string,
#     )

#     return await context.koduck.send_message(
#         receive_message=context.message, embed=embed
#     )


async def choice_react(
    context: KoduckContext, num_choices: int, question_string: str
) -> int | None:
    assert context.koduck
    # there are only 9 (10) number emojis :(
    num_choices = min(num_choices, 9)
    num_choices = min(num_choices, settings.choice_react_limit)
    the_message = await context.koduck.send_message(
        receive_message=context.message, content=question_string
    )
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
    result_emoji = reaction.emoji
    choice = choice_emojis.index(result_emoji)
    if choice == 0:
        return
    return choice - 1


async def remind_me(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    assert context.message
    assert context.message.author
    user_id = context.message.author.id
    user_reminders = db.query_reminder(user_id)
    if not user_reminders:
        user_reminders = Reminder(user_id, "", "")

    if not args:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remind_me_status.format(
                user_reminders.weeks, user_reminders.pokemon
            ),
        )

    if args[0].isdigit():
        try:
            query_week = int(args[0])
            assert 1 <= query_week <= settings.num_weeks
        except (ValueError, AssertionError):
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_week_invalid_param.format(
                    settings.num_weeks, settings.num_weeks
                ),
            )
        if query_week in user_reminders.weeks:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_remind_me_week_exists,
            )
        db.add_reminder_week(user_id, query_week)
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remind_me_week_success.format(query_week),
        )

    query_pokemon = await pokemon_lookup(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    if query_pokemon in user_reminders.pokemon:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_remind_me_pokemon_exists,
        )
    db.add_reminder_pokemon(user_id, query_pokemon)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_remind_me_pokemon_success.format(query_pokemon),
    )


async def unremind_me(context: KoduckContext, *args: str) -> discord.Message | None:
    assert context.koduck
    if not args:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_unremind_me_no_param,
        )
    assert context.message
    assert context.message.author
    user_id = context.message.author.id
    user_reminders = db.query_reminder(user_id)
    if not user_reminders:
        user_reminders = Reminder(user_id, "", "")

    if args[0].isdigit():
        try:
            query_week = int(args[0])
            assert 1 <= query_week <= settings.num_weeks
        except (ValueError, AssertionError):
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_week_invalid_param.format(
                    settings.num_weeks, settings.num_weeks
                ),
            )
        if query_week not in user_reminders.weeks:
            return await context.koduck.send_message(
                receive_message=context.message,
                content=settings.message_unremind_me_week_non_exists,
            )

        user_reminders.remove_week(query_week)  #
        db.update_reminder(user_reminders)
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_unremind_me_week_success.format(query_week),
        )
    query_pokemon = await pokemon_lookup(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    if query_pokemon not in user_reminders.pokemon:
        return await context.koduck.send_message(
            receive_message=context.message,
            content=settings.message_unremind_me_pokemon_non_exists,
        )

    user_reminders.remove_pokemon(query_pokemon)
    db.update_reminder(user_reminders)
    return await context.koduck.send_message(
        receive_message=context.message,
        content=settings.message_unremind_me_pokemon_success.format(query_pokemon),
    )


current_day = -1
current_week = -1


async def background_task(koduck_instance: Koduck) -> None:
    global current_day
    global current_week
    current_time = datetime.datetime.now(tz=pytz.timezone("Etc/GMT+6"))

    if current_day == -1 or current_week == -1:
        current_day = current_time.day
        current_week = utils.get_current_week()
        return

    if current_time.day == current_day:
        return

    current_day = current_time.day
    current_week2 = utils.get_current_week()
    week_changed, current_week = current_week2 != current_week, current_week2
    event_pokemon = utils.get_current_event_pokemon()
    for reminder in db.get_reminders():
        reminder_strings: list[str] = []
        if week_changed and current_week in reminder.weeks:
            reminder_strings.append(settings.message_reminder_week.format(current_week))
        reminder_strings.extend(
            settings.message_reminder_pokemon.format(ep)
            for ep in event_pokemon
            if ep in reminder.pokemon
        )
        if reminder_strings:
            the_user = await koduck_instance.client.fetch_user(reminder.user_id)
            await the_user.send(
                content=settings.message_reminder_header.format(
                    reminder.user_id, "\n".join(reminder_strings)
                )
            )


settings.background_task = background_task
