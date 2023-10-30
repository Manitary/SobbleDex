import datetime
import re
from typing import Any, Callable, Protocol

import discord
import pytz

import db
import settings
from koduck import KoduckContext
from models import EventType, RepeatType

RE_PUNCTUATION = re.compile(r"[- ()'.%+:#]")

WEEKDAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


def alias(query: str) -> str:
    aliases = db.get_aliases()
    return aliases.get(query.lower(), query)


def strip_punctuation(string: str) -> str:
    return RE_PUNCTUATION.sub("", string).replace("é", "e")


def remove_duplicates[T](l: list[T]) -> list[T]:  # pylint: disable=E0602
    ans: list[T] = []
    for item in l:
        if item in ans:
            continue
        ans.append(item)
    return ans


def emojify(text: str, emojis: dict[str, str], check_aliases: bool = False) -> str:
    if not text:
        return ""
    emojified_text = text
    possible_emojis: list[str] = re.findall(r"\[[^\[\]]*\]", text)
    possible_emojis = remove_duplicates(possible_emojis)

    # for each of the strings that were in []
    for emoji in possible_emojis:
        raw = emoji[1:-1]
        # figure out the string that is trying to be emojified
        emoji_name = alias(raw) if check_aliases else raw
        # replace it with the emoji if it exists
        emojified_text = emojified_text.replace(
            f"[{raw}]", emojis.get(strip_punctuation(emoji_name.lower()), raw)
        )

    return emojified_text


def get_current_week() -> int:
    er_start_time = datetime.datetime(
        settings.er_start_year,
        settings.er_start_month,
        settings.er_start_day,
        settings.er_start_hour,
        tzinfo=pytz.utc,
    )
    current_time = datetime.datetime.now(tz=pytz.utc)
    td = current_time - er_start_time
    query_week = ((td.days // 7) % 24) + 1
    return query_week


def current_eb_pokemon() -> str:
    return db.query_eb_pokemon_by_week(get_current_week())


def get_current_event_pokemon() -> list[str]:
    date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(6)
    ans: list[str] = []
    for event in db.get_all_event_pokemon():
        if (
            event.repeat_type == RepeatType.WEEKLY
            and date.weekday() == event.repeat_param_1
        ):
            ans.extend(event.pokemon)
        elif (
            event.repeat_type == RepeatType.MONTHLY and date.day == event.repeat_param_1
        ):
            ans.extend(event.pokemon)
        elif (
            event.repeat_type == RepeatType.YEARLY
            and date.month == event.repeat_param_1
        ):
            # assuming all yearly events are daily stage type
            # assuming the format "3 days"
            td = date - event.this_year_start_date
            if 0 <= td.days < event.duration:
                ans.append(event.pokemon[td.days % len(event.pokemon)])  # maybe td+1
        elif event.repeat_type == RepeatType.ROTATION:
            start_time = event.latest_start_time_for(date)

            if event.stage_type == EventType.DAILY:
                td = date - start_time
                if 0 <= td.days < event.duration:
                    try:
                        ans.append(event.pokemon[(td.days + 1) % 7])
                    except IndexError:
                        pass
            elif (
                date.year == start_time.year
                and date.month == start_time.month
                and date.day == start_time.day
            ):
                ans.extend([pokemon for pokemon in event.pokemon if pokemon not in ans])
    return ans


def event_week_day(day: int) -> str:
    return WEEKDAYS[(day + 1) % 7]


class BotCommand(Protocol):
    async def __call__(
        self, context: KoduckContext, *args: str, **kwargs: Any
    ) -> discord.Message | None:
        ...


def min_param(num: int, error: str) -> Callable[[BotCommand], BotCommand]:
    """If the bot command receives less than ``num`` arguments, send the ``error`` message."""

    def decorator(func: BotCommand) -> BotCommand:
        async def wrapper(
            context: KoduckContext, *args: str, **kwargs: Any
        ) -> discord.Message | None:
            assert context.koduck
            if len(args) < num:
                return await context.koduck.send_message(
                    receive_message=context.message, content=error
                )
            return await func(context, *args, **kwargs)

        return wrapper

    return decorator


def allow_space_delimiter() -> Callable[[BotCommand], BotCommand]:
    """Make the command accept both comma- and space-delimited arguments."""

    def decorator(func: BotCommand) -> BotCommand:
        async def wrapper(
            context: KoduckContext, *args: str, **kwargs: Any
        ) -> discord.Message | None:
            if len(args) != 1:
                # Comma-separated arguments -> do nothing
                return await func(context, *args, **kwargs)
            temp = tuple(args[0].split())
            if len(temp) == 1:
                # No space separation -> do nothing
                return await func(context, *args, **kwargs)
            try:
                first_num = next(i for i, x in enumerate(temp) if x.isdigit())
                assert first_num > 0
            except (StopIteration, AssertionError):
                # No element is a number, or the first element is a number -> do nothing
                pass
            else:
                # Merge all arguments before the first number
                # (at least >=2 args due to previous assertion)
                args = ("".join(temp[:first_num]),) + temp[first_num:]

                if args[0].lower() == "zygarde" and args[1] in {"10", "50", "100"}:
                    # Special case with the only pokemon including a number in the name
                    args = (args[0] + args[1],) + args[2:]

            return await func(context, *args, **kwargs)

        return wrapper

    return decorator
