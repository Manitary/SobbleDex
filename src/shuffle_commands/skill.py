from typing import Any

import db
import embed_formatters
import settings
from koduck import KoduckContext
from models import Param, Payload

from .decorators import min_param
from .lookup import lookup_skill
from .query import pokemon_filter, pokemon_filter_results_to_string, validate_query


@min_param(num=1, error=settings.message_skill_no_param)
async def skill(context: KoduckContext, *args: str, **kwargs: Any) -> Payload | None:
    # parse params
    query_skill = await lookup_skill(context, _query=args[0])
    if not query_skill:
        print("Unrecognized Skill")
        return Payload()

    # retrieve data
    skill_ = db.query_skill(query_skill)
    if not skill_:
        return Payload(content=settings.message_skill_no_result.format(query_skill))

    return Payload(embed=embed_formatters.format_skill_embed(skill_))


async def skill_with_pokemon(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload:
    use_emojis = kwargs.get("useemojis", False)

    if not args:
        return Payload(content=settings.message_skill_no_param)

    query_skill = args[0]

    # lookup and validate skill
    query_skill = await lookup_skill(context, _query=query_skill)
    if not query_skill:
        print("Unrecognized Skill")
        return Payload()

    # retrieve skill data
    skill_ = db.query_skill(query_skill)
    if not skill_:
        return Payload(
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
    if "?farmable" in args:  # ? default behaviour, should get deprecated
        farmable = Param.IGNORE
    if "farmable" in kwargs:
        if kwargs["farmable"] == "yes":
            farmable = Param.INCLUDE
        elif kwargs["farmable"] == "no":
            farmable = Param.EXCLUDE
        elif kwargs["farmable"] == "both":  # ? default behaviour, should get deprecated
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

    field_name = (
        "Pokemon with this skill"
        + (f" ({query_string})" if query_string else "")
        + (f" sorted by {sortby_string}" if sortby_string else "")
    )

    embed = embed_formatters.format_skill_embed(skill_)
    embed.add_field(name=field_name, value=field_value)

    return Payload(embed=embed)


async def skill_with_pokemon_with_emojis(
    context: KoduckContext, *args: str, **kwargs: Any
) -> Payload:
    kwargs["useemojis"] = True
    return await skill_with_pokemon(context, *args, **kwargs)
