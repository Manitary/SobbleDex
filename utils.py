import datetime
import re

import pytz

import settings
import yadon

emojis = {}


def alias(query):
    aliases = {
        k.lower(): v[0] for k, v in yadon.ReadTable(settings.aliases_table).items()
    }
    try:
        return aliases[query.lower()]
    except KeyError:
        return query


def strip_punctuation(string):
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


def remove_duplicates(list):
    ans = []
    for item in list:
        if item not in ans:
            ans.append(item)
    return ans


def emojify(the_message, check_aliases=False):
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


def current_eb_pokemon():
    query_week = get_current_week()
    events = yadon.ReadTable(settings.events_table)
    for index, values in events.items():
        (
            stage_type,
            event_pokemon,
            _,
            repeat_type,
            repeat_param_1,
            _,
            _,
            _,
            duration_string,
            _,
            _,
            _,
        ) = values
        event_week = int(repeat_param_1) + 1
        # assumes EBs are either 1 week or 2 weeks
        event_week_2 = event_week + 1 if duration_string == "14 days" else event_week
        if (
            stage_type == "Escalation"
            and repeat_type == "Rotation"
            and (event_week == query_week or event_week_2 == query_week)
        ):
            return event_pokemon
    return None


def get_current_event_pokemon():
    date = datetime.datetime.now(tz=pytz.utc)
    ans = []
    for k, v in yadon.ReadTable(settings.events_table).items():
        (
            stage_type,
            event_pokemon,
            _,
            repeat_type,
            repeat_param_1,
            repeat_param_2,
            start_time,
            end_time,
            duration_string,
            cost_string,
            attempts_string,
            encounter_rates,
        ) = v
        if repeat_type == "Weekly" and date.weekday() == repeat_param_1:
            ans += event_pokemon.split("/")
        elif repeat_type == "Monthly" and date.day == repeat_param_1:
            ans += event_pokemon.split("/")
        elif repeat_type == "Yearly" and date.month == repeat_param_1:
            # assuming all yearly events are daily stage type
            event_start_date = datetime.datetime(
                date.year, repeat_param_1, repeat_param_2
            )
            # assuming the format "3 days"
            duration = int(duration_string.split(" ")[0])
            td = date - event_start_date
            if td.days >= 0 and td.days < duration:
                ans.append(event_pokemon.split("/")[td.days])
        elif repeat_type == "Rotation":
            st = start_time.split("/")
            et = end_time.split("/")
            start_time = datetime.datetime(
                int(st[0]),
                int(st[1]),
                int(st[2]),
                int(st[3]),
                int(st[4]),
                tzinfo=pytz.utc,
            )
            end_time = datetime.datetime(
                int(et[0]),
                int(et[1]),
                int(et[2]),
                int(et[3]),
                int(et[4]),
                tzinfo=pytz.utc,
            )
            while end_time < datetime.datetime.now(tz=pytz.utc):
                start_time = start_time + datetime.timedelta(168)
                end_time = end_time + datetime.timedelta(168)

            if stage_type == "Daily":
                duration = int(duration_string.split(" ")[0])
                td = date - start_time
                if td.days >= 0 and td.days < duration:
                    try:
                        ans.append(event_pokemon.split("/")[(td.days + 1) % 7])
                    except IndexError:
                        pass
            elif (
                date.year == start_time.year
                and date.month == start_time.month
                and date.day == start_time.day
                and event_pokemon not in ans
            ):
                ans += event_pokemon.split("/")
    return ans


def get_farmable_pokemon():
    farmable_pokemon = []

    main_stages = yadon.ReadTable(settings.main_stages_table)
    for main_stage in main_stages.values():
        drops = [main_stage[20], main_stage[22], main_stage[24]]
        if "PSB" in drops:
            farmable_pokemon.append(main_stage[0])

    expert_stages = yadon.ReadTable(settings.expert_stages_table)
    for expert_stage in expert_stages.values():
        drops = [expert_stage[20], expert_stage[22], expert_stage[24]]
        if "PSB" in drops:
            farmable_pokemon.append(expert_stage[0])

    event_stages = yadon.ReadTable(settings.event_stages_table)
    for event_stage in event_stages.values():
        drops = [event_stage[20], event_stage[22], event_stage[24]]
        if "PSB" in drops:
            farmable_pokemon.append(event_stage[0])

    return farmable_pokemon
