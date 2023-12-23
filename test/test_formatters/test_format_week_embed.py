import discord
from helper import check_embed_equal

import embed_formatters


def test_format_week_embed(week_embed: tuple[int, discord.Embed]) -> None:
    week, embed = week_embed
    real = embed_formatters.format_week_embed(week)
    expected = embed
    check_embed_equal(real, expected)


def test_format_week_embed_fake_week_less() -> None:
    real = embed_formatters.format_week_embed(0)
    expected = discord.Embed(title="Event Rotation Week 0", color=0xFF0000)
    expected.add_field(inline=False, name="Challenges", value="")
    expected.add_field(inline=False, name="One Chance a Day!", value="")
    expected.add_field(inline=False, name="Daily", value="")

    check_embed_equal(expected, real)


def test_format_week_embed_fake_week_more() -> None:
    real = embed_formatters.format_week_embed(25)
    expected = discord.Embed(title="Event Rotation Week 25", color=0xFF0000)
    expected.add_field(inline=False, name="Challenges", value="")
    expected.add_field(inline=False, name="One Chance a Day!", value="")
    expected.add_field(inline=False, name="Daily", value="")

    check_embed_equal(expected, real)
