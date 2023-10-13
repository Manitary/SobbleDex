#!/usr/bin/env python3

import difflib
import json
import os
import re
from typing import Any

import discord

from koduck import KoduckContext
from models import SMStageResult, SMTeam, WMTeam

scriptdir = os.path.dirname(os.path.realpath(__file__)) + os.sep
shuffle_calc_json_filename = f"{scriptdir}shuffle_calc_data.json"


def initialize_shuffle_calc_json_data(
    _filename: str,
) -> tuple[
    list[SMStageResult],
    list[list[str]],
    list[str],
    list[SMTeam],
    list[WMTeam],
    dict[str, str],
]:
    json_data = {}
    if os.path.isfile(_filename):
        with open(_filename, encoding="utf-8") as json_file:
            try:
                json_data: dict[str, Any] = json.load(json_file)
            except Exception as e:
                print(str(e))
    _sm_data: list[SMTeam] = json_data.get("sm_teams", [])
    _wm_data: list[WMTeam] = json_data.get("wm_teams", [])
    _sm_stages_data: list[SMStageResult] = json_data.get("sm_stages_results", [])
    _explain_data: dict[str, str] = json_data.get("explainations", {})
    _sm_stage_aliases_by_stage = [k["aliases"] for k in _sm_stages_data]
    _sm_stage_aliases = [m for k in _sm_stages_data for m in k["aliases"]]
    return (
        _sm_stages_data,
        _sm_stage_aliases_by_stage,
        _sm_stage_aliases,
        _sm_data,
        _wm_data,
        _explain_data,
    )


(
    sm_stages_data,
    sm_stage_aliases_by_stage,
    sm_stage_aliases,
    sm_data,
    wm_data,
    explain_data,
) = initialize_shuffle_calc_json_data(shuffle_calc_json_filename)


async def sm(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    if len(sm_data) == 0 or len(sm_stages_data) < 300 or context["message"].author.bot:
        return
    selected_stage_index = -1
    selected_strategy = ["bhs", "btc", "cso"]
    show_help = False
    for al in [k.strip().lower().replace(":", "") for k in " ".join(args).split(",")]:
        if len(al) == 0:
            continue
        elif al in ["help"]:
            show_help = True
            break
        elif al in ["main"]:
            selected_strategy = ["bhs", "btc", "cso"]
        elif al in ["all"]:
            selected_strategy = ["bhs", "btc", "ptc", "cso", "cth"]
        elif al in ["hs", "hammeringstreak", "hammering streak"]:
            selected_strategy = ["bhs"]
        elif al in ["tc", "typelesscombo", "typeless combo"]:
            selected_strategy = ["btc", "ptc"]
        elif al in ["so", "shotout", "shot out"]:
            selected_strategy = ["cso"]
        elif al in ["th", "tryhard", "try hard", "sc", "supercheer", "super cheer"]:
            selected_strategy = ["cth"]
        elif selected_stage_index < 0:
            if len(al) > 0 and al == re.sub(r"[^0-9]+", "", al):
                psid = int(al)
                if psid > 0 and selected_stage_index < 300:
                    selected_stage_index = psid - 1
            else:
                possible_stages = difflib.get_close_matches(al, sm_stage_aliases)
                if len(possible_stages) > 0:
                    best_selected_stage_index = -1
                    for i, st in enumerate(sm_stage_aliases_by_stage):
                        if possible_stages[0] in st:
                            best_selected_stage_index = i
                            break
                    if best_selected_stage_index >= 0:
                        selected_stage_index = best_selected_stage_index
    if show_help or selected_stage_index == -1:
        txt = [
            "Test accuracy: 10 repeats per move",
            "```Win%  Exp (Std%)  Moves  Team",
        ]
        for strat in sm_data:
            if not strat["show"]:
                continue
            if len(txt) == 5:
                txt.append("=" * 32)
            txt.append(
                f"{strat['winrate']:4.1f}  {strat['exp']:4.0f}  "
                f"{strat['exp_stdm']:4.1f}  {strat['moves_left']:5.1f}  {strat['team']}"
            )
        txt[-1] += "```"
        return await context.koduck.send_message(
            context.message, content="\n".join(txt).strip()
        )
    if selected_stage_index < 0 or selected_stage_index >= 300:
        return await context.koduck.send_message(
            context.message, content="Couldn't reverse the SM stage index! :warning:"
        )

    selected_stage_data = sm_stages_data[selected_stage_index]
    txt = [
        f"Stage **{selected_stage_index + 1}**: **{selected_stage_data['aliases'][0].title()}**"
        f" ({selected_stage_data['encounter']:.1f}% encounter)",
        "```Strategy  Moves Std%    Range-68%    Range-95%",
    ]
    for strat in selected_strategy:
        tmega = ""
        if strat[0] == "b":
            tmega = "Bee"
        elif strat[0] == "p":
            tmega = "Pin"
        elif strat[0] == "c":
            tmega = "MCX"
        else:
            tmega = "Mega"
        team_name = f"{tmega}-{strat[1:].upper()}"
        txt.append(
            "{:8.8}  {:5.2f}  {:3.0f}  {:4.1f} ~ {:4.1f}  {:4.1f} ~ {:4.1f}".format(
                team_name,
                max(1.0, selected_stage_data["results"][strat][0]),
                100.0
                * selected_stage_data["results"][strat][2]
                / selected_stage_data["results"][strat][0],
                max(
                    1.0,
                    selected_stage_data["results"][strat][0]
                    - selected_stage_data["results"][strat][2],
                ),
                selected_stage_data["results"][strat][0]
                + selected_stage_data["results"][strat][2],
                max(
                    1.0,
                    selected_stage_data["results"][strat][0]
                    - 2 * selected_stage_data["results"][strat][2],
                ),
                selected_stage_data["results"][strat][0]
                + 2 * selected_stage_data["results"][strat][2],
            )
        )
    txt[-1] += "```"
    return await context.koduck.send_message(
        context.message, content="\n".join(txt).strip()
    )


async def wm(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    if not wm_data or context.message.author.bot:
        return
    txt = ["Moves used: **15** (*+5 price not applied*)", "```Coins Std%  Team"]
    txt.extend(
        f"{strat['coins15m']}  {strat['std']:4.1f}  {strat['team']}"
        for strat in wm_data
        if strat["show"]
    )
    txt[-1] += "```"
    return await context.koduck.send_message(
        context.message, content="\n".join(txt).strip()
    )


async def explain(
    context: KoduckContext, *args: str, **kwargs: Any
) -> discord.Message | None:
    assert context.koduck
    assert context.message
    if not explain_data or context.message.author.bot:
        return
    question = [
        k.strip().lower().replace(":", "") for k in " ".join(args).split(",") + ["help"]
    ][0]
    if question in explain_data:
        txt = explain_data[question].replace("@", "\n")
    else:
        txt = (
            "Usage: **explain argument**. "
            f"Valid arguments are: {', '.join(sorted(explain_data.keys()))}\n"
            "For more details, visit the Advanced Game Mechanics guide: "
            "https://old.reddit.com/r/PokemonShuffle/comments/bdvau1/advanced_game_mechanics/"
        )

    return await context.koduck.send_message(context["message"], content=txt)
