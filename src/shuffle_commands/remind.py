from typing import Any

import db
import settings
from koduck import KoduckContext
from models import Payload, Reminder

from .lookup import lookup_pokemon


async def remind_me(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    assert context.message
    assert context.message.author
    user_id = context.message.author.id
    user_reminders = db.query_reminder(user_id)
    if not user_reminders:
        user_reminders = Reminder(user_id, "", "")

    if not args:
        return Payload(
            content=settings.message_remind_me_status.format(
                user_reminders.weeks_str, user_reminders.pokemon_str
            )
        )

    if args[0].isdigit():
        try:
            query_week = int(args[0])
            assert 1 <= query_week <= settings.num_weeks
        except (ValueError, AssertionError):
            return Payload(
                content=settings.message_week_invalid_param.format(
                    settings.num_weeks, settings.num_weeks
                )
            )
        if query_week in user_reminders.weeks:
            return Payload(content=settings.message_remind_me_week_exists)
        db.add_reminder_week(user_id, query_week)
        return Payload(
            content=settings.message_remind_me_week_success.format(query_week)
        )

    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return Payload()

    if query_pokemon in user_reminders.pokemon:
        return Payload(content=settings.message_remind_me_pokemon_exists)

    db.add_reminder_pokemon(user_id, query_pokemon)
    return Payload(
        content=settings.message_remind_me_pokemon_success.format(query_pokemon),
    )


async def unremind_me(context: KoduckContext, *args: str, **kwargs: Any) -> Payload:
    if not args:
        return Payload(content=settings.message_unremind_me_no_param)
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
            return Payload(
                content=settings.message_week_invalid_param.format(
                    settings.num_weeks, settings.num_weeks
                ),
            )

        if query_week not in user_reminders.weeks:
            return Payload(content=settings.message_unremind_me_week_non_exists)

        user_reminders.remove_week(query_week)
        db.update_reminder(user_reminders)
        return Payload(
            content=settings.message_unremind_me_week_success.format(query_week),
        )

    query_pokemon = await lookup_pokemon(context, _query=args[0])
    if not query_pokemon:
        print("Unrecognized Pokemon")
        return Payload()

    if query_pokemon not in user_reminders.pokemon:
        return Payload(
            content=settings.message_unremind_me_pokemon_non_exists,
        )

    user_reminders.remove_pokemon(query_pokemon)
    db.update_reminder(user_reminders)
    return Payload(
        content=settings.message_unremind_me_pokemon_success.format(query_pokemon),
    )
