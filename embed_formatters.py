import datetime
from typing import Sequence

import discord
import pytz

import constants
import db
import settings
import utils
import yadon
from models import EBStretch, EventType, PuzzleStage, Stage, StageType


def format_pokemon_embed(name, details):
    dex = int(details["Dex"]) if details["Dex"].isdigit() else 0
    ss = details["SS"].split("/")
    if details["Mega Power"]:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**Icons**: {} ({})\n**MSUs**: {}\n**Mega Effects**: {}".format(
            dex,
            details["Type"],
            details["Icons"],
            int(details["Icons"]) - int(details["MSU"]),
            details["MSU"],
            details["Mega Power"],
        )
    else:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**BP**: {}\n**RMLs**: {}\n**Max AP**: {}\n**Skill**: {}".format(
            dex,
            details["Type"],
            details["BP"],
            details["RML"],
            details["MaxAP"],
            details["Skill"],
        )
        if len(ss) > 0 and ss[0]:
            stats += " ({})".format(", ".join(ss))

    the_color = (
        constants.type_colors[details["Type"]]
        if details["Type"] in constants.type_colors.keys()
        else discord.Embed.Empty
    )
    embed = discord.Embed(title=name, color=the_color, description=stats)
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/{}.png".format(
            name.replace("%", "%25").replace(":", "").replace(" ", "%20")
        )
    )
    return embed


def format_skill_embed(name, details):
    def convert_to_float(f):
        try:
            return float(f)
        except ValueError:
            return 0

    bonus1 = convert_to_float(details["Bonus1"])
    bonus2 = convert_to_float(details["Bonus2"])
    bonus3 = convert_to_float(details["Bonus3"])
    bonus4 = convert_to_float(details["Bonus4"])
    rate1 = int(details["Rate1"]) if details["Rate1"].isdigit() else 0
    rate2 = int(details["Rate2"]) if details["Rate2"].isdigit() else 0
    rate3 = int(details["Rate3"]) if details["Rate3"].isdigit() else 0
    multiplier = convert_to_float(details["Multiplier"])
    sp1 = int(details["SP1"]) if details["SP1"].isdigit() else 0
    sp2 = int(details["SP2"]) if details["SP2"].isdigit() else 0
    sp3 = int(details["SP3"]) if details["SP3"].isdigit() else 0
    sp4 = int(details["SP4"]) if details["SP4"].isdigit() else 0
    notes = yadon.ReadRowFromTable(settings.skill_notes_table, name)

    stats = "**Description**: {}\n".format(details["Description"])
    if notes is not None:
        notes = notes[0].replace("\\n", "\n")
        stats += "**Notes**: {}\n".format(utils.emojify(notes))
    stats += "**Activation Rates**: {}% / {}% / {}%\n".format(rate1, rate2, rate3)
    if details["Type"] != "Mega Boost":
        stats += "**Damage Multiplier**: x{:0.2f}\n".format(multiplier)
    if details["Bonus Effect"] == "Activation Rate":
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(
            2,
            bonus1,
            min(100, rate1 + bonus1) if rate1 != 0 else 0,
            min(100, rate2 + bonus1) if rate2 != 0 else 0,
            min(100, rate3 + bonus1) if rate3 != 0 else 0,
        )
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(
            3,
            bonus2,
            min(100, rate1 + bonus2) if rate1 != 0 else 0,
            min(100, rate2 + bonus2) if rate2 != 0 else 0,
            min(100, rate3 + bonus2) if rate3 != 0 else 0,
        )
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(
            4,
            bonus3,
            min(100, rate1 + bonus3) if rate1 != 0 else 0,
            min(100, rate2 + bonus3) if rate2 != 0 else 0,
            min(100, rate3 + bonus3) if rate3 != 0 else 0,
        )
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(
            5,
            bonus4,
            min(100, rate1 + bonus4) if rate1 != 0 else 0,
            min(100, rate2 + bonus4) if rate2 != 0 else 0,
            min(100, rate3 + bonus4) if rate3 != 0 else 0,
        )
    elif details["Bonus Effect"] == "Multiply Damage":
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(
            2, bonus1, multiplier * bonus1
        )
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(
            3, bonus2, multiplier * bonus2
        )
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(
            4, bonus3, multiplier * bonus3
        )
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(
            5, bonus4, multiplier * bonus4
        )
    elif details["Bonus Effect"] == "Add Damage":
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(
            2, bonus1, multiplier + bonus1
        )
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(
            3, bonus2, multiplier + bonus2
        )
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(
            4, bonus3, multiplier + bonus3
        )
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(
            5, bonus4, multiplier + bonus4
        )
    stats += "**SP Requirements**: {} => {} => {} => {} (Total: {})\n".format(
        sp1, sp2 - sp1, sp3 - sp2, sp4 - sp3, sp4
    )

    the_color = (
        constants.skill_colors[details["Type"]]
        if details["Type"] in constants.skill_colors.keys()
        else discord.Embed.Empty
    )
    embed = discord.Embed(title=name, color=the_color, description=stats)
    return embed


def format_type_embed(values):
    type, se, nve, weak, res, imm = values
    embed = discord.Embed(title=type, color=constants.type_colors[type])
    embed.add_field(name="Super Effective Against", value=se)
    embed.add_field(name="Not Very Effective Against", value=nve)
    embed.add_field(name="Weaknesses", value=weak)
    embed.add_field(name="Resistances", value=res)
    embed.add_field(name="Status Effect Immunities", value=imm)
    return embed


def format_stage_embed(
    stage: Stage,
    eb_data: tuple[str, int, str, int] = ("", 0, "", 0),
    shorthand: bool = False,
) -> discord.Embed:
    notes = db.query_stage_notes(stage.string_id)

    if stage.hp != stage.hp_mobile:
        stats = "**3DS HP**: {}{}\n**Mobile HP**: {}{}".format(
            stage.hp,
            f" (UX: {stage.hp*3})"
            if stage.stage_type == StageType.MAIN
            and stage.is_puzzle_stage != PuzzleStage.PUZZLE
            else "",
            stage.hp_mobile,
            f" (UX: {stage.hp_mobile*3})"
            if stage.stage_type == StageType.MAIN
            and stage.is_puzzle_stage != PuzzleStage.PUZZLE
            else "",
        )
    else:
        stats = "**HP**: {}{}{}".format(
            stage.hp,
            f" (UX: {stage.hp*3})"
            if stage.stage_type == StageType.MAIN
            and stage.is_puzzle_stage != PuzzleStage.PUZZLE
            else "",
            f" + {stage.extra_hp} ({stage.hp + stage.extra_hp * eb_data[1]})"
            if stage.extra_hp
            else "",
        )

    stats += "\n**{}**: {}\n**Experience**: {}".format(
        "Moves" if stage.moves else "Seconds", stage.moves or stage.seconds, stage.exp
    )  #! broken if moves =/= mobile moves (same for exp)

    if eb_data[3] == 0:
        stats += "\n**Catchability**: {}% + {}%/{}".format(
            stage.base_catch, stage.bonus_catch, "move" if stage.moves else "3sec"
        )
        if (
            stage.base_catch != stage.base_catch_mobile
            or stage.bonus_catch != stage.bonus_catch_mobile
        ):
            stats += " (Mobile: {}% + {}%/{})".format(
                stage.base_catch_mobile,
                stage.bonus_catch_mobile,
                "move" if stage.moves else "3sec",
            )
    else:
        stats += f"\n**Catchability**: {min(eb_data[3], 100)}%"

    num_extra = max(len(stage.default_supports) - 4, 0)
    if num_extra:
        stats += "\n**Default Supports**: {} | {}".format(
            utils.emojify(
                "".join([f"[{p}]" for p in stage.default_supports[0:num_extra]])
            ),
            utils.emojify(
                "".join([f"[{p}]" for p in stage.default_supports[num_extra:]])
            ),
        )
    else:
        stats += "\n**Default Supports**: {}".format(
            utils.emojify("".join([f"[{p}]" for p in stage.default_supports]))
        )

    stats += (
        f"\n**Rank Requirements**: {stage.s_rank} / {stage.a_rank} / {stage.b_rank}"
    )

    if stage.stage_type == StageType.EXPERT:
        stats += f"\n**S-Ranks to unlock**: {stage.s_unlock}"

    stats += "\n**Attempt Cost**: {} x{}".format(
        utils.emojify(f"[{stage.cost.type}]"), stage.cost.amount
    )

    if any(d.item != "Nothing" for d in stage.drops):
        stats += "\n**Drop Items**: {}{} / {}{} / {}{}\n**Drop Rates**: {}% / {}% / {}%".format(
            utils.emojify(f"[{stage.drops[0].item}]"),
            f" x{stage.drops[0].amount}" if stage.drops[0].amount != 1 else "",
            utils.emojify(f"[{stage.drops[1].item}]"),
            f" x{stage.drops[1].amount}" if stage.drops[1].amount != 1 else "",
            utils.emojify(f"[{stage.drops[2].item}]"),
            f" x{stage.drops[2].amount}" if stage.drops[2].amount != 1 else "",
            stage.drops[0].rate,
            stage.drops[1].rate,
            stage.drops[2].rate,
        )
    # auto remove c-1 if less than 4 supports
    stats += "\n**Items**: {}".format(
        utils.emojify(
            "".join(
                [
                    f"[{item}]"
                    for item in stage.items
                    if not (len(stage.default_supports) < 4 and item == "C-1")
                ]
            )
        )
    )
    if stage.rewards != "Nothing":
        stats += f"\n**Initial clear reward**: {utils.emojify(stage.rewards)}"

    if stage.rewards_ux != "Nothing":
        stats += f"\n**UX Initial clear reward**: {utils.emojify(stage.rewards_ux)}"

    if eb_data[2]:
        stats += f"\n**EB stage clear reward**: {utils.emojify(eb_data[2])}"

    if notes:
        stats += "\n**Notes**: {}".format(utils.emojify(notes[0]).replace("\\n", "\n"))

    header = "{} Stage {}: {}{}{}".format(
        stage.stage_type,
        stage.id,
        stage.pokemon,
        " " + utils.emojify(f"[{stage.pokemon}]"),
        eb_data[0],
    )

    pokemon_type = db.query_pokemon_type(stage.pokemon)
    embed = discord.Embed(
        title=header, color=constants.type_colors[pokemon_type], description=stats
    )
    if shorthand:
        return embed

    if stage.layout_index:
        embed.set_thumbnail(
            url=(
                "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
                f"{stage.stage_type} Stages Layouts/Layout Index {stage.layout_index}.png"
            ).replace(" ", "%20")
        )
        embed.url = (
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
            f"{stage.stage_type} Stages Layouts/Layout Index {stage.layout_index}.png"
        ).replace(" ", "%20")

    for i, disruption in enumerate(stage.disruptions, 1):
        if disruption == "Nothing":
            continue
        embed.add_field(
            name=f"**Countdown {i}**",
            value=utils.emojify(disruption.replace("\\n", "\n")),
            inline=False,
        )
    return embed


def format_starting_board_embed(stage: Stage) -> discord.Embed:
    header = (
        f"{stage.stage_type} Stage Index {stage.id}: {stage.pokemon} "
        + utils.emojify(f"[{stage.pokemon}]")
    )
    pokemon_type = db.query_pokemon_type(stage.pokemon)
    embed = discord.Embed(title=header, color=constants.type_colors[pokemon_type])
    if not stage.layout_index:
        embed.description = "No initial board layout"
        return embed

    embed.set_image(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/"
            f"{stage.stage_type} Stages Layouts/Layout Index {stage.layout_index}.png"
        ).replace(" ", "%20")
    )
    return embed


def format_event_embed(values):
    (
        index,
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
    ) = values

    event_pokemon = event_pokemon.split("/")
    encounter_rates = encounter_rates.split("/")
    cost_string = "" if cost_string == "Nothing" else cost_string
    attempts_string = "" if attempts_string == "Nothing" else attempts_string

    event_pokemon_string = ""
    if stage_type == "Daily":
        header = "Daily Pokémon"
        for i in range(len(event_pokemon)):
            event_pokemon_string += "{}: {} [{}]\n".format(
                [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ][(i + 1) % 7],
                event_pokemon[i],
                event_pokemon[i],
            )
    elif stage_type == "Escalation":
        header = "Escalation Battles: {} [{}]".format(
            event_pokemon[0], event_pokemon[0]
        )
    elif stage_type == "Safari":
        header = "Pokémon Safari"
        for i in range(len(event_pokemon) - 1):
            # For some reason the first pokemon is duplicated here
            event_pokemon_string += "[{}] {} ({}%)\n".format(
                event_pokemon[i + 1], event_pokemon[i + 1], encounter_rates[i]
            )
    elif stage_type == "Monthly":
        header = "Monthly Challenge"
        for i in range(len(event_pokemon)):
            event_pokemon_string += "[{}] {} ({}%)\n".format(
                event_pokemon[i], event_pokemon[i], encounter_rates[i]
            )
    else:
        header = "{} [{}]".format(event_pokemon[0], event_pokemon[0])

    date_header = "{} Event".format(repeat_type)
    if repeat_type == "Rotation":
        date_header += ": Week {}/24".format(int(repeat_param_1) + 1)

    starts_when = None
    ends_when = None
    if repeat_type != "Weekly":
        st = start_time.split("/")
        et = end_time.split("/")
        if repeat_type == "Rotation":
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
            starts_when = start_time - datetime.datetime.now(tz=pytz.utc)
            ends_when = end_time - datetime.datetime.now(tz=pytz.utc)
            start_time = start_time.strftime("%Y/%m/%d %H:%M UTC")
            end_time = end_time.strftime("%Y/%m/%d %H:%M UTC")
        else:
            start_time = "{}/{}/{} {}:{} UTC".format(st[0], st[1], st[2], st[3], st[4])
            end_time = "{}/{}/{} {}:{} UTC".format(et[0], et[1], et[2], et[3], et[4])
            if repeat_type == "Monthly":
                add_one_month = (
                    1 if datetime.datetime.now(tz=pytz.utc).day >= int(et[2]) else 0
                )
                add_one_year = (
                    1
                    if datetime.datetime.now(tz=pytz.utc).month == 12
                    and datetime.datetime.now(tz=pytz.utc).day >= int(et[2])
                    else 0
                )
                st[0] = datetime.datetime.now(tz=pytz.utc).year + add_one_year
                et[0] = datetime.datetime.now(tz=pytz.utc).year + add_one_year
                st[1] = datetime.datetime.now(tz=pytz.utc).month + add_one_month
                et[1] = datetime.datetime.now(tz=pytz.utc).month + add_one_month
            elif repeat_type == "Yearly":
                add_one_year = (
                    1
                    if datetime.datetime.now(tz=pytz.utc).month >= int(et[1])
                    and datetime.datetime.now(tz=pytz.utc).day >= int(et[2])
                    else 0
                )
                st[0] = datetime.datetime.now(tz=pytz.utc).year + add_one_year
                et[0] = datetime.datetime.now(tz=pytz.utc).year + add_one_year
            start_time_2 = datetime.datetime(
                int(st[0]),
                int(st[1]),
                int(st[2]),
                int(st[3]),
                int(st[4]),
                tzinfo=pytz.utc,
            )
            end_time_2 = datetime.datetime(
                int(et[0]),
                int(et[1]),
                int(et[2]),
                int(et[3]),
                int(et[4]),
                tzinfo=pytz.utc,
            )
            starts_when = start_time_2 - datetime.datetime.now(tz=pytz.utc)
            ends_when = end_time_2 - datetime.datetime.now(tz=pytz.utc)

    embed = discord.Embed(
        title=utils.emojify(header), color=constants.event_type_colors[stage_type]
    )
    if event_pokemon_string:
        embed.add_field(
            name="Event Pokémon",
            value=utils.emojify(event_pokemon_string),
            inline=False,
        )
    if starts_when and starts_when > datetime.timedelta():
        event_duration_string = "{} to {} ({}) (starts in {} days {} hours)".format(
            start_time,
            end_time,
            duration_string,
            starts_when.days,
            int(starts_when.seconds / 3600),
        )
    elif ends_when and ends_when > datetime.timedelta():
        event_duration_string = "{} to {} ({}) (ends in {} days {} hours)".format(
            start_time,
            end_time,
            duration_string,
            ends_when.days,
            int(ends_when.seconds / 3600),
        )
    else:
        event_duration_string = "{} to {} ({})".format(
            start_time, end_time, duration_string
        )
    embed.add_field(
        name=date_header,
        value="Event duration: {}".format(event_duration_string),
        inline=False,
    )
    if cost_string != "" or attempts_string != "":
        embed.add_field(
            name="Misc. Details",
            value=utils.emojify(cost_string + "\n" + attempts_string),
            inline=False,
        )
    return embed


def format_eb_rewards_embed(values):
    pokemon = values[0]
    rewards = values[1:]

    stats = ""
    for entry in rewards:
        level, reward_item, reward_amount = entry.split("/")
        stats += "Level {} reward: {} x{}\n".format(
            level, utils.emojify("[{}]".format(reward_item)), reward_amount
        )
    stats = stats[:-1]

    embed = discord.Embed(
        title="{} Escalation Battles Rewards".format(pokemon),
        color=0x4E7E4E,
        description=stats,
    )
    return embed


def format_eb_details_embed(eb_stretches: Sequence[EBStretch]) -> discord.Embed:
    if not eb_stretches:
        raise ValueError("No EB stretch provided")

    stats = ""
    for leg in eb_stretches:
        stage = db.query_stage_by_index(leg.stage_index, StageType.EVENT)

        if leg.end_level == -1:
            levels = f"**Levels {leg.start_level}+**"
        elif leg.start_level == leg.end_level - 1:
            levels = f"**Level {leg.start_level}**"
        else:
            levels = f"**Levels {leg.start_level} to {leg.end_level-1}**"

        extra = ""
        if len(stage.default_supports) == 3:
            extra = " **(3 supports)**"
        elif len(stage.default_supports) == 5:
            extra = utils.emojify(f" **(5th support: [{stage.default_supports[0]}])**")

        stats += "{}: {}{} / {}{}\n".format(
            levels,
            stage.hp,
            f" + {stage.extra_hp}" if stage.extra_hp else "",
            stage.seconds or stage.moves,
            extra,
        )

    embed = discord.Embed(
        title=f"{eb_stretches[0].pokemon} Escalation Battles Details",
        color=0x4E7E4E,
        description=stats,
    )
    return embed


def format_week_embed(query_week: int) -> discord.Embed:
    comp: str = ""
    daily: str = ""
    oad: str = ""
    gc: str = ""
    eb: str = ""
    safari: str = ""

    for event in db.query_event_week(query_week):
        event_pokemon = event.pokemon.split("/")
        stage = db.get_event_stage_by_index(event.stage_ids[0])
        drops_string = stage.str_drops(utils.emojify, compact=True)
        attempt_cost_string = stage.cost.to_str(utils.emojify)
        unlock_cost_string = event.str_unlock(utils.emojify)

        # Challenge
        if event.stage_type == EventType.CHALLENGE:
            gc += "- {}{}{}{}\n".format(
                utils.emojify(f"[{event_pokemon[0]}]"),
                drops_string,
                attempt_cost_string,
                unlock_cost_string,
            )
        # Daily
        elif event.stage_type == EventType.DAILY:
            event_pokemon: list[str] = utils.remove_duplicates(event_pokemon)
            if len(event_pokemon) == 1:
                oad += "- {}{}{}".format(
                    utils.emojify(f"[{event_pokemon[0]}]"),
                    drops_string,
                    attempt_cost_string,
                )
            else:
                daily += "- " + "".join(
                    utils.emojify(f"[{pokemon}]") for pokemon in event_pokemon
                )
                daily += drops_string
        # Competition
        elif event.stage_type == EventType.COMPETITIVE:
            # There are duplicate entries... grab only one of them
            if not comp:
                items_string = "".join(
                    utils.emojify(f"[{item}]")
                    for item in stage.items_available.split("/")
                )
                comp += "- {} ({})".format(
                    utils.emojify(f"[{event_pokemon[0]}]"), items_string
                )
        # EB
        elif event.stage_type == EventType.ESCALATION:
            eb += "- {}{}".format(utils.emojify(f"[{event_pokemon[0]}]"), drops_string)
        # Safari
        elif event.stage_type == EventType.SAFARI:
            # For some reason the first pokemon is duplicated here
            safari += "- " + ", ".join(
                "{} ({:.2f}%)".format(utils.emojify(f"[{pokemon}]"), rate)
                for pokemon, rate in zip(event_pokemon[1:], event.encounter_rates)
            )
            safari += drops_string

    embed = discord.Embed(title=f"Event Rotation Week {query_week}", color=0xFF0000)
    if comp:
        embed.add_field(name="Competitive Stage", value=comp, inline=False)
    embed.add_field(name="Challenges", value=gc, inline=False)
    if eb:
        embed.add_field(name="Escalation Battles", value=eb, inline=False)
    if safari:
        embed.add_field(name="Safari", value=safari, inline=False)
    embed.add_field(name="One Chance a Day!", value=oad, inline=False)
    embed.add_field(name="Daily", value=daily, inline=False)

    return embed


def format_query_results_embed(header, buckets, use_emojis):
    embed = discord.Embed(description=header)

    for bucket_key in buckets.keys():
        output_string = ""
        for item in buckets[bucket_key]:
            if use_emojis:
                try:
                    # surround ss pokemon with parentheses (instead of boldifying it, because, y'know... can't boldify emojis)
                    if item.find("**") != -1:
                        output_string += "([{}])".format(item[:-2])
                    else:
                        output_string += "[{}]".format(item)
                except KeyError:
                    output_string += "{} ".format(
                        "**" + item if item.find("**") != -1 else item
                    )
            else:
                output_string += "{}, ".format(
                    "**" + item if item.find("**") != -1 else item
                )
        if not use_emojis:
            output_string = output_string[:-2]
        else:
            output_string = utils.emojify(output_string)
        embed.add_field(name=bucket_key, value=output_string, inline=False)

    return embed


def format_guides_embed(guides, page=0):
    embed = discord.Embed()
    return embed
