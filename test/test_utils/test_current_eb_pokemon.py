from pytest import MonkeyPatch

import utils

RESULTS = [
    "",
    "Decidueye",
    "Volcanion",
    "Volcanion",
    "Latios",
    "Latios",
    "Giratina (Altered Forme)",
    "Giratina (Altered Forme)",
    "Latias",
    "Latias",
    "Diancie",
    "Diancie",
    "Darkrai",
    "Darkrai",
    "Kyurem",
    "Kyurem",
    "Zygarde (50% Forme)",
    "Zygarde (50% Forme)",
    "Meloetta (Aria Forme)",
    "Meloetta (Aria Forme)",
    "Giratina (Origin Forme)",
    "Giratina (Origin Forme)",
    "Magearna",
    "Incineroar",
    "Primarina",
    "",
]


def test_current_eb_pokemon(monkeypatch: MonkeyPatch) -> None:
    def patch_week(week: int) -> None:
        monkeypatch.setattr(utils, "get_current_week", lambda: week)

    for i, expected in enumerate(RESULTS):
        patch_week(i)
        assert expected == utils.current_eb_pokemon()
