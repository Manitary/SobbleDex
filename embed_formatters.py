import datetime
from typing import Any, Sequence

import discord
import pytz

import constants
import db
import utils
from models import (
    EBReward,
    EBStretch,
    Event,
    EventType,
    Pokemon,
    PuzzleStage,
    RepeatType,
    Skill,
    SkillBonus,
    SkillType,
    Stage,
    StageType,
    TypeInfo,
)

DATE_FORMAT = "%Y/%m/%d %H:%M UTC"
DATE_MANUAL_FORMAT = "{}/{}/{} {}:{} UTC"


def format_pokemon_embed(pokemon: Pokemon) -> discord.Embed:
    if pokemon.mega_power:
        stats = (
            f"**Dex**: {pokemon.dex:03d}\n**Type**: {pokemon.type}\n"
            f"**Icons**: {pokemon.icons} ({pokemon.evo_speed})\n"
            f"**MSUs**: {pokemon.msu}\n**Mega Effects**: {pokemon.mega_power}"
        )
    else:
        stats = (
            f"**Dex**: {pokemon.dex:03d}\n**Type**: {pokemon.type}\n"
            f"**BP**: {pokemon.bp}\n**RMLs**: {pokemon.rml}\n"
            f"**Max AP**: {pokemon.max_ap}\n**Skill**: {pokemon.skill}"
        )
        if pokemon.ss_skills:
            stats += f" ({', '.join(pokemon.ss_skills)})"

    the_color = constants.type_colors[pokemon.type]
    embed = discord.Embed(title=pokemon.pokemon, color=the_color, description=stats)
    embed.set_thumbnail(
        url=(
            "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/"
            f"{pokemon.pokemon}.png"
        )
        .replace("%", "%25")
        .replace(" ", "%20")
    )
    return embed


def format_skill_embed(skill: Skill) -> discord.Embed:
    stats = f"**Description**: {skill.description}\n"
    if skill.notes:
        stats += f"**Notes**: {utils.emojify(skill.notes.replace('\\n', '\n'))}\n"

    stats += "**Activation Rates**: {}% / {}% / {}%\n".format(*skill.rates)

    if skill.type != SkillType.MEGA_BOOST:
        stats += f"**Damage Multiplier**: x{skill.multiplier:0.2f}\n"

    if skill.bonus_effect == SkillBonus.ACTIVATION_RATE:
        for i, bonus in enumerate(skill.bonus, 2):
            stats += (
                "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(
                    i,
                    skill.bonus[0],
                    min(100, skill.rates[0] + bonus) if skill.rates[0] else 0,
                    min(100, skill.rates[1] + bonus) if skill.rates[1] else 0,
                    min(100, skill.rates[2] + bonus) if skill.rates[2] else 0,
                )
            )
    elif skill.bonus_effect == SkillBonus.MULTIPLY_DAMAGE:
        for i, bonus in enumerate(skill.bonus, 2):
            stats += (
                f"**SL{i} Bonus**: x{bonus:0.2f} (x{skill.multiplier*bonus:0.2f})\n"
            )
    elif skill.bonus_effect == SkillBonus.ADD_DAMAGE:
        for i, bonus in enumerate(skill.bonus, 2):
            stats += (
                f"**SL{i} Bonus**: +{bonus:0.2f} (x{skill.multiplier+bonus:0.2f})\n"
            )

    stats += "**SP Requirements**: {} => {} => {} => {} (Total: {})\n".format(
        *skill.sp_cost_partial
    )

    the_color = constants.skill_colors[skill.type]
    embed = discord.Embed(title=skill.skill, color=the_color, description=stats)
    return embed


def format_type_embed(t: TypeInfo) -> discord.Embed:
    embed = discord.Embed(title=t.type.value, color=constants.type_colors[t.type.value])
    embed.add_field(name="Super Effective Against", value=t.se)
    embed.add_field(name="Not Very Effective Against", value=t.nve)
    embed.add_field(name="Weaknesses", value=t.weak)
    embed.add_field(name="Resistances", value=t.resist)
    embed.add_field(name="Status Effect Immunities", value=t.status_immune)
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
        stats += "\n**Notes**: {}".format(utils.emojify(notes).replace("\\n", "\n"))

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


def format_event_embed(event: Event) -> discord.Embed:
    event_pokemon_string = ""
    if event.event_type == EventType.DAILY:
        header = "Daily Pokémon"
        for i, pokemon in enumerate(event.pokemon):
            event_pokemon_string += (
                f"{utils.event_week_day(i)}: {pokemon} [{pokemon}]\n"
            )
    elif event.event_type == EventType.ESCALATION:
        header = f"Escalation Battles: {event.pokemon[0]} [{event.pokemon[0]}]"
    elif event.event_type == EventType.SAFARI:
        header = "Pokémon Safari"
        for pokemon, rate in zip(event.pokemon[1:], event.encounter_rates):
            # For some reason the first pokemon is duplicated here
            event_pokemon_string += f"[{pokemon}] {pokemon} ({rate}%)\n"
    elif event.event_type == EventType.MONTHLY:
        header = "Monthly Challenge"
        for pokemon, rate in zip(event.pokemon, event.encounter_rates):
            event_pokemon_string += f"[{pokemon}] {pokemon} ({rate}%)\n"
    else:
        header = f"{event.pokemon[0]} [{event.pokemon[0]}]"

    date_header = f"{event.repeat_type} Event"
    if event.repeat_type == RepeatType.ROTATION:
        date_header += f": Week {event.repeat_param_1+1}/24"

    starts_when = None
    ends_when = None
    start_time = None
    end_time = None
    now = datetime.datetime.now(tz=pytz.utc)
    current_year, current_month, current_day = now.year, now.month, now.day
    # TODO find a way to do this better
    if event.repeat_type != RepeatType.WEEKLY:
        st = event.date_start
        et = event.date_end
        if event.repeat_type == RepeatType.ROTATION:
            start_time = event.date_start_datetime.strftime(DATE_FORMAT)
            end_time = event.date_end_datetime.strftime(DATE_FORMAT)
            starts_when = event.next_appearance[0] - datetime.datetime.now(tz=pytz.utc)
            ends_when = event.next_appearance[1] - datetime.datetime.now(tz=pytz.utc)
        else:
            start_time = DATE_MANUAL_FORMAT.format(*event.date_start)
            end_time = DATE_MANUAL_FORMAT.format(*event.date_end)
            if event.repeat_type == RepeatType.MONTHLY:
                add_one_month = int(current_day >= int(event.date_end[2]))
                add_one_year = int(
                    current_month == 12 and current_day >= int(event.date_end[2])
                )
                st[0] = current_year + add_one_year
                et[0] = current_year + add_one_year
                st[1] = current_month + add_one_month
                et[1] = current_month + add_one_month
            elif event.repeat_type == RepeatType.YEARLY:
                add_one_year = int(
                    current_month >= int(event.date_end[1])
                    and current_day >= int(event.date_end[2])
                )
                st[0] = current_year + add_one_year
                et[0] = current_year + add_one_year
            start_time_2 = datetime.datetime(*map(int, st), tzinfo=pytz.utc)
            end_time_2 = datetime.datetime(*map(int, et), tzinfo=pytz.utc)
            starts_when = start_time_2 - datetime.datetime.now(tz=pytz.utc)
            ends_when = end_time_2 - datetime.datetime.now(tz=pytz.utc)

    embed = discord.Embed(
        title=utils.emojify(header), color=constants.event_type_colors[event.event_type]
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
            event.duration,
            starts_when.days,
            starts_when.seconds // 3600,
        )
    elif ends_when and ends_when > datetime.timedelta():
        event_duration_string = "{} to {} ({}) (ends in {} days {} hours)".format(
            start_time,
            end_time,
            event.duration,
            ends_when.days,
            ends_when.seconds // 3600,
        )
    else:
        event_duration_string = f"{start_time} to {end_time} ({ event.duration})"
    embed.add_field(
        name=date_header,
        value=f"Event duration: {event_duration_string}",
        inline=False,
    )
    if event.cost_unlock or event.notes:
        embed.add_field(
            name="Misc. Details",
            value=utils.emojify(f"{event.cost_unlock}\n{event.notes}"),
            inline=False,
        )
    return embed


def format_eb_rewards_embed(rewards: Sequence[EBReward]) -> discord.Embed:
    pokemon = rewards[0].pokemon
    stats = "\n".join(
        f"Level {r.level} reward: {utils.emojify(f'[{r.reward}]')} x{r.amount} {r.alternative}"
        for r in rewards
    )
    embed = discord.Embed(
        title=f"{pokemon} Escalation Battles Rewards",
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


def format_query_results_embed(
    header: str, buckets: dict[Any, list[str]], use_emojis: bool
) -> discord.Embed:
    embed = discord.Embed(description=header)

    for bucket_key, items in buckets.items():
        output_string = ""
        for item in items:
            if use_emojis:
                try:
                    # surround ss pokemon with parentheses
                    # (instead of boldifying it, because, y'know... can't boldify emojis)
                    # TODO seems a complicated way to remove a trailing **
                    if item.find("**") != -1:
                        output_string += f"([{item[:-2]}])"
                    else:
                        output_string += f"[{item}]"
                except KeyError:
                    output_string += "{} ".format(
                        "**" + item if item.find("**") != -1 else item
                    )
            else:
                output_string += "{}, ".format(
                    f"**{item}" if item.find("**") != -1 else item
                )
        if use_emojis:
            output_string = utils.emojify(output_string)
        else:
            output_string = output_string[:-2]

        embed.add_field(name=bucket_key, value=output_string, inline=False)

    return embed


def format_guides_embed(guides, page: int = 0) -> discord.Embed:
    embed = discord.Embed()
    return embed
