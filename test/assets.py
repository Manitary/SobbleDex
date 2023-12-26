import json
from pathlib import Path
from typing import Any, NotRequired, TypedDict

import discord


def import_json_asset(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data


class EmbedField(TypedDict):
    name: str
    value: str
    inline: bool


class EmbedDict(TypedDict):
    title: str
    color: str | int
    description: NotRequired[str]
    fields: NotRequired[list[EmbedField]]


def parse_embed(embed_dict: EmbedDict) -> discord.Embed:
    colour = embed_dict["color"]
    if isinstance(colour, str):
        colour = int(colour[2:], 16)
    embed = discord.Embed(
        title=embed_dict["title"],
        color=colour,
        description=embed_dict.get("description", None),
    )
    for field in embed_dict.get("fields", []):
        embed.add_field(**field)
    return embed


ASSETS_PATH = Path() / "test" / "assets"

WEEK_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "week_embeds.json"))
)

EB_REWARDS_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "eb_rewards_embeds.json"))
)

EB_DETAILS_EMBEDS = list(
    map(parse_embed, import_json_asset(ASSETS_PATH / "eb_details_embeds.json"))
)
