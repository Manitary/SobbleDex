import itertools
from collections import defaultdict
from typing import Any

import discord

import db
import embed_formatters
import settings
import utils
from koduck import KoduckContext
from models import Param, PokemonType


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
            right = right.capitalize()
            try:
                _ = PokemonType(right)
            except ValueError:
                continue

        validated_queries.append((left, operation, right))

    return validated_queries


async def query(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
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
        return await context.send_message(
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

    return await context.send_message(
        embed=embed_formatters.format_query_results_embed(header, buckets, use_emojis),
    )


async def query_with_emojis(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    kwargs["useemojis"] = True
    return await query(context, *args, **kwargs)


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

    all_pokemon_names = db.get_db_table_column(table="pokemon", column="pokemon")

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
                # surround ss pokemon with parentheses
                # (instead of boldifying it, because, y'know... can't boldify emojis)
                if item.find("**") != -1:
                    output_string += f"([{item.replace("**", "")}])"  # fmt: skip
                else:
                    output_string += f"[{item}]"
                if farmable:
                    output_string += "\\*"
            else:
                output_string += "{}{}, ".format(
                    "**" + item if item.find("**") != -1 else item,
                    "\\*" if farmable else "",
                )
        if not use_emojis:
            output_string = output_string[:-2]
    return output_string
