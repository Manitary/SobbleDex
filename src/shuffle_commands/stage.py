from typing import Any, Awaitable, Callable

import discord

import constants
import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import Payload, QueryType, Stage, StageType, UserQuery

from .eb import eb_details
from .lookup import choice_react, lookup_pokemon


async def stage(
    context: KoduckContext,
    *args: str,
    choice_selector: Callable[
        [KoduckContext, int, str], Awaitable[int | None]
    ] = choice_react,
    **kwargs: Any,
) -> Payload:
    assert context.koduck
    assert context.message
    user_query_history = context.koduck.query_history[context.message.author.id]
    # change last (current) query type to ANY in case stage does not return a stage message
    user_query_history[-1] = UserQuery(QueryType.ANY, args=args, kwargs=kwargs)

    if not args:
        return Payload(content=settings.message_stage_no_param)

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
            assert result_number > 0
        except (ValueError, AssertionError):
            return Payload(content=settings.message_stage_invalid_param)

    results: list[Stage] = []
    # retrieve data
    if stage_type == StageType.MAIN:
        try:
            candidate_stage = db.query_stage_by_index(stage_index, stage_type)
            results.append(candidate_stage)
        except ValueError:
            return Payload(
                content=settings.message_stage_main_invalid_param.format(
                    settings.main_stages_min_index, settings.main_stages_max_index
                ),
            )
    elif stage_type == StageType.EXPERT:
        try:
            candidate_stage = db.query_stage_by_index(stage_index, stage_type)
            results.append(candidate_stage)
        except ValueError:
            return Payload(
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
            return Payload(
                content=settings.message_stage_event_invalid_param.format(
                    settings.event_stages_min_index, settings.event_stages_max_index
                ),
            )
    elif stage_type == StageType.ALL:
        query_pokemon = await lookup_pokemon(context, _query=query_pokemon)
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return Payload()

        # redirect to EB if queried pokemon is in EB table
        if db.query_eb_pokemon(query_pokemon):
            # ? no giving the option to select a specific stage?
            payload = await eb_details(context, *[query_pokemon], **kwargs)
            assert isinstance(payload, dict)
            return payload

        results = (
            list(db.query_stage_by_pokemon(query_pokemon, StageType.MAIN))
            + list(db.query_stage_by_pokemon(query_pokemon, StageType.EXPERT))
            + list(db.query_stage_by_pokemon(query_pokemon, StageType.EVENT))
        )

    if not results:
        return Payload(content=settings.message_stage_no_result.format(query_pokemon))

    # if a result number is given
    if result_number:
        if not 1 <= result_number <= len(results):
            return Payload(
                content=settings.message_stage_result_error.format(len(results))
            )
        res = results[result_number - 1]
        user_query_history[-1] = UserQuery(
            QueryType.STAGE, args=(res.string_id,), kwargs=kwargs
        )
        if stage_starting_board:
            return Payload(embed=embed_formatters.format_starting_board_embed(res))
        return Payload(
            embed=embed_formatters.format_stage_embed(res, shorthand=shorthand),
        )

    if len(results) == 1:
        user_query_history[-1] = UserQuery(
            QueryType.STAGE, args=(results[0].string_id,), kwargs=kwargs
        )
        if stage_starting_board:
            return Payload(
                embed=embed_formatters.format_starting_board_embed(results[0])
            )
        return Payload(
            embed=embed_formatters.format_stage_embed(results[0], shorthand=shorthand)
        )

    indices: list[str] = []
    output_string = ""
    for i, candidate_stage in enumerate(results):
        indices.append(candidate_stage.string_id)
        if i < settings.choice_react_limit:
            output_string += f"\n{constants.number_emojis[i + 1]} {indices[i]}"

    choice: int | None = await choice_selector(
        context,
        min(len(indices), settings.choice_react_limit),
        settings.message_stage_multiple_results + output_string,
    )
    if choice is None:
        return Payload()
    user_query_history[-1] = UserQuery(
        QueryType.STAGE, args=(results[choice].string_id,), kwargs=kwargs
    )
    if stage_starting_board:
        return Payload(
            embed=embed_formatters.format_starting_board_embed(results[choice]),
        )
    return Payload(
        embed=embed_formatters.format_stage_embed(results[choice], shorthand=shorthand)
    )


async def stage_shorthand(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    kwargs["shorthand"] = True
    return await stage(context, *args, **kwargs)


async def starting_board(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    kwargs["startingboard"] = True
    return await stage(context, *args, **kwargs)


async def next_stage(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | Payload | None:
    query_ = await latest_stage_query(context)
    if not query_:
        return await context.send_message(
            content=settings.message_no_previous_stage,
        )

    if not query_.args:
        return await context.send_message(
            content=settings.message_last_query_error,
        )

    last_stage_id = query_.args[0]
    assert isinstance(last_stage_id, str)

    if last_stage_id.startswith("s"):
        return await context.send_message(
            content=settings.message_last_query_invalid_stage,
        )
    if last_stage_id.startswith("ex"):
        return await stage(
            context, f"ex{int(last_stage_id[2:]) + 1}", kwargs=query_.kwargs
        )
    if last_stage_id.isdigit():
        next_id = int(last_stage_id) + 1
        if next_id == 701:
            next_id = 1
        return await stage(context, str(next_id), kwargs=query_.kwargs)

    return await context.send_message(
        content=settings.message_last_query_error,
    )


async def next_stage_shorthand(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | Payload | None:
    kwargs["shorthand"] = True
    return await next_stage(context, *args, **kwargs)


async def latest_stage_query(context: KoduckContext) -> UserQuery | None:
    assert context.koduck
    assert context.message
    user_id = context.message.author.id
    query_history = context.koduck.query_history[user_id]

    try:
        query_ = next(q for q in reversed(query_history) if q.type == QueryType.STAGE)
    except StopIteration:
        return

    return query_
