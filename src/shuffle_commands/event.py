from typing import Any

import discord

import db
import embed_formatters
import settings
import utils
from koduck import KoduckContext

from .decorators import allow_space_delimiter, min_param
from .lookup import lookup_pokemon


@allow_space_delimiter()
@min_param(num=1, error=settings.message_event_no_param)
async def event(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    result_number = 1

    # parse params
    if len(args) >= 2:
        try:
            result_number = int(args[1])
            if result_number <= 0:
                return await context.send_message(
                    content=settings.message_event_invalid_param,
                )
        except ValueError:
            return await context.send_message(
                content=settings.message_event_invalid_param,
            )
    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return

    # retrieve data
    events = list(db.query_event_by_pokemon(query_pokemon))

    if not events:
        return await context.send_message(
            content=settings.message_event_result_error.format(len(events)),
        )

    try:
        selected_event = events[result_number - 1]
    except IndexError:
        return await context.send_message(
            content=settings.message_event_no_result.format(query_pokemon),
        )

    if len(events) > 1:
        return await embed_formatters.paginate_embeds(
            context,
            [embed_formatters.format_event_embed(e) for e in events],
            result_number,
        )

    return await context.send_message(
        embed=embed_formatters.format_event_embed(selected_event),
    )


async def week(context: KoduckContext, *args: str) -> discord.Message | None:
    curr_week = utils.get_current_week()
    if not args:
        return await context.send_message(
            embed=embed_formatters.format_week_embed(curr_week),
        )

    if args[0].isdigit():
        query_week = int(args[0])
    else:
        query_pokemon = await lookup_pokemon(context, _query=args[0])
        if not query_pokemon:
            print("Unrecognized Pokemon")
            return

        # retrieve data
        weeks = [
            event.repeat_param_1 for event in db.query_event_by_pokemon(query_pokemon)
        ]
        if not weeks:
            return await context.send_message(
                content=settings.message_event_no_result.format(query_pokemon),
            )
        sorted_results = [w + 1 for w in weeks if w + 1 >= curr_week] + [
            w + 1 for w in weeks if w + 1 < curr_week
        ]
        query_week = sorted_results[0]

    if not 1 <= query_week <= settings.num_weeks:
        return await context.send_message(
            content=settings.message_week_invalid_param.format(
                settings.num_weeks, settings.num_weeks
            ),
        )

    return await context.send_message(
        embed=embed_formatters.format_week_embed(query_week),
    )


async def next_week(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    args = (str(utils.get_current_week() % 24 + 1),)
    return await week(context, *args, **kwargs)
