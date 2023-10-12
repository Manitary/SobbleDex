import datetime
import re
from typing import TypeVar

import pytz

import db
import settings
from models import EventType, RepeatType

T = TypeVar("T")

emojis = {}


def alias(query: str) -> str:
    aliases = db.get_aliases()
    return aliases.get(query.lower(), query)


def strip_punctuation(string: str) -> str:
    return (
        string.replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace("'", "")
        .replace("é", "e")
        .replace(".", "")
        .replace("%", "")
        .replace("+", "")
        .replace(":", "")
        .replace("#", "")
    )


def remove_duplicates(l: list[T]) -> list[T]:
    ans: list[T] = []
    for item in l:
        if item not in ans:
            ans.append(item)
    return ans


def emojify(the_message: str, check_aliases: bool = False) -> str:
    emojified_message = the_message

    possible_emojis = re.findall(r"\[[^\[\]]*\]", the_message)
    possible_emojis = remove_duplicates(possible_emojis)

    # for each of the strings that were in []
    for i in range(len(possible_emojis)):
        raw = possible_emojis[i][1:-1]
        # figure out the string that is trying to be emojified
        if check_aliases:
            try:
                emoji_name = alias(raw)
            except:
                emoji_name = raw
        else:
            emoji_name = raw
        # replace it with the emoji if it exists
        try:
            emojified_message = emojified_message.replace(
                "[{}]".format(raw), emojis[strip_punctuation(emoji_name.lower())]
            )
        except KeyError:
            emojified_message = emojified_message.replace("[{}]".format(raw), raw)

    return emojified_message


def get_current_week():
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
    return [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ][(day + 1) % 7]


if __name__ == "__main__":
    print(get_current_event_pokemon())
