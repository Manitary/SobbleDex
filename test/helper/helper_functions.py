import discord

from models import Payload


def check_payload_equal(p1: Payload, p2: Payload) -> None:
    assert p1.keys() == p2.keys()
    if "content" in p1:
        assert "content" in p2
        assert p1["content"] == p2["content"]
    if "embed" in p1:
        assert "embed" in p2
        check_embed_equal(p1["embed"], p2["embed"])
    if "check_aliases" in p1:
        assert "check_aliases" in p2
        assert p1["check_aliases"] == p2["check_aliases"]


def check_embed_equal(e1: discord.Embed, e2: discord.Embed) -> None:
    assert e1.title == e2.title
    assert e1.description == e2.description
    assert e1.color == e2.color
    assert e1.thumbnail == e2.thumbnail
    assert e1.url == e2.url
    assert e1.image == e2.image

    assert len(e1.fields) == len(e2.fields)
    for f1, f2 in zip(e1.fields, e2.fields):
        assert f1.name == f2.name
        assert f1.value == f2.value
        assert f1.inline == f2.inline

    assert e1 == e2
