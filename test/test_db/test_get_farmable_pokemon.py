import json

from db import get_farmable_pokemon


def test_get_farmable_pokemon() -> None:
    with open("test/test_db/farmable_pokemon.txt", encoding="utf-8") as f:
        expected = json.load(f)
    assert set(expected) == get_farmable_pokemon()
