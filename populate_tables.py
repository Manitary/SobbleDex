import sqlite3
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas

# TODO populating other tables with straight imports of tsv files

EB_DETAILS = "shuffle_tables/eb_details.txt"
EB_REWARDS = "shuffle_tables/eb_rewards.txt"
DB_BOT_PATH = "bot.sqlite"
DB_SHUFFLE_PATH = "shuffle.sqlite"

BOT_TABLES_PATH = Path(".") / "tables"
SHUFFLE_TABLES_PATH = Path(".") / "shuffle_tables"


@dataclass
class Table:
    name: str
    columns: OrderedDict[str, Callable[[Any], Any]]
    has_header: bool
    has_id_col: bool = False
    id_label: str = ""


def int_or_none(x: str) -> int | None:
    try:
        return int(x)
    except ValueError:
        return None


BOT_TABLES = (
    Table(
        "commands",
        OrderedDict(
            {
                "command_name": str,
                "module_name": str,
                "method_name": str,
                "command_type": str,
                "command_tier": int,
                "description": str,
            }
        ),
        True,
    ),
    Table("custom_responses", OrderedDict({"message": str, "response": str}), False),
    Table(
        "settings", OrderedDict({"key": str, "value": str, "tier": int_or_none}), True
    ),
)

SHUFFLE_TABLES = (
    Table("aliases", OrderedDict({"alias": str, "original_name": str}), True),
    Table(
        "ap",
        OrderedDict({"base_ap": int} | {f"lvl{x}": int for x in range(1, 31)}),
        False,
        has_id_col=True,
        id_label="base_ap",
    ),
    Table(
        "events",
        OrderedDict(
            {
                "id": int,
                "stage_type": str,
                "pokemon": str,
                "stage_ids": str,
                "repeat_type": str,
                "repeat_param_1": int,
                "repeat_param_2": int,
                "date_start": str,
                "date_end": str,
                "duration": str,
                "cost_unlock": str,
                "notes": str,
                "encounter_rates": str,
            }
        ),
        False,
        True,
    ),
    Table(
        "event_stages",
        OrderedDict(
            {
                "id": int,
                "pokemon": str,
                "hp": int,
                "hp_mobile": int,
                "moves": int,
                "seconds": int,
                "exp": int,
                "base_catch": int,
                "bonus_catch": int,
                "base_catch_mobile": int,
                "bonus_catch_mobile": int,
                "default_supports": str,
                "s_rank": int,
                "a_rank": int,
                "b_rank": int,
                "num_s_ranks_to_unlock": int,
                "is_puzzle_stage": str,
                "extra_hp": int,
                "layout_index": int,
                "cost_type": str,
                "attempt_cost": int,
                "drop_1_item": str,
                "drop_1_amount": int,
                "drop_2_item": str,
                "drop_2_amount": int,
                "drop_3_item": str,
                "drop_3_amount": int,
                "drop_1_rate": float,
                "drop_2_rate": float,
                "drop_3_rate": float,
                "items_available": str,
                "rewards": str,
                "rewards_ux": str,
                "cd1": str,
                "cd2": str,
                "cd3": str,
            }
        ),
        True,
        True,
    ),
    Table(
        "exp",
        OrderedDict({"base_ap": int} | {f"lvl{x}": int for x in range(31)}),
        False,
        has_id_col=True,
        id_label="base_ap",
    ),
    Table(
        "expert_stages",
        OrderedDict(
            {
                "id": int,
                "pokemon": str,
                "hp": int,
                "hp_mobile": int,
                "moves": int,
                "seconds": int,
                "exp": int,
                "base_catch": int,
                "bonus_catch": int,
                "base_catch_mobile": int,
                "bonus_catch_mobile": int,
                "default_supports": str,
                "s_rank": int,
                "a_rank": int,
                "b_rank": int,
                "num_s_ranks_to_unlock": int,
                "is_puzzle_stage": str,
                "extra_hp": int,
                "layout_index": int,
                "cost_type": str,
                "attempt_cost": int,
                "drop_1_item": str,
                "drop_1_amount": int,
                "drop_2_item": str,
                "drop_2_amount": int,
                "drop_3_item": str,
                "drop_3_amount": int,
                "drop_1_rate": float,
                "drop_2_rate": float,
                "drop_3_rate": float,
                "items_available": str,
                "rewards": str,
                "rewards_ux": str,
                "cd1": str,
                "cd2": str,
                "cd3": str,
            }
        ),
        False,
        True,
    ),
    Table(
        "help_messages", OrderedDict({"message_type": str, "message_text": str}), False
    ),
    Table(
        "main_stages",
        OrderedDict(
            {
                "id": int,
                "pokemon": str,
                "hp": int,
                "hp_mobile": int,
                "moves": str,
                "seconds": int,
                "exp": str,
                "base_catch": float,
                "bonus_catch": int,
                "base_catch_mobile": float,
                "bonus_catch_mobile": int,
                "default_supports": str,
                "s_rank": int,
                "a_rank": int,
                "b_rank": int,
                "num_s_ranks_to_unlock": int,
                "is_puzzle_stage": str,
                "extra_hp": int,
                "layout_index": int,
                "cost_type": str,
                "attempt_cost": int,
                "drop_1_item": str,
                "drop_1_amount": int,
                "drop_2_item": str,
                "drop_2_amount": int,
                "drop_3_item": str,
                "drop_3_amount": int,
                "drop_1_rate": float,
                "drop_2_rate": float,
                "drop_3_rate": float,
                "items_available": str,
                "rewards": str,
                "rewards_ux": str,
                "cd1": str,
                "cd2": str,
                "cd3": str,
            }
        ),
        True,
        True,
    ),
    Table(
        "pokemon",
        OrderedDict(
            {
                "pokemon": str,
                "dex": int,
                "type": str,
                "bp": int,
                "rml": int,
                "max_ap": int,
                "skill": str,
                "ss": str,
                "icons": int,
                "msu": int,
                "mega_power": str,
            }
        ),
        True,
    ),
    Table(
        "skills",
        OrderedDict(
            {
                "skill": str,
                "description": str,
                "rate1": int,
                "rate2": int,
                "rate3": int,
                "type": str,
                "multiplier": float,
                "bonus_effect": str,
                "bonus1": float,
                "bonus2": float,
                "bonus3": float,
                "bonus4": float,
                "sp1": int,
                "sp2": int,
                "sp3": int,
                "sp4": int,
            }
        ),
        True,
    ),
    Table("skill_notes", OrderedDict({"skill": str, "notes": str}), False),
    Table(
        "sm_rewards",
        OrderedDict(
            {
                "level": int,
                "first_reward_type": str,
                "first_reward_amount": int,
                "repeat_reward_type": str,
                "repeat_reward_amount": int,
            }
        ),
        False,
        has_id_col=True,
        id_label="level",
    ),
    Table("stage_notes", OrderedDict({"stage_id": str, "notes": str}), False),
    Table(
        "types",
        OrderedDict(
            {
                "type": str,
                "se": str,
                "nve": str,
                "weak": str,
                "resist": str,
                "status_immune": str,
            }
        ),
        False,
    ),
)


def populate_eb_details() -> None:
    with open(EB_DETAILS, encoding="utf-8") as f:
        data = f.readlines()

    db = sqlite3.connect(DB_SHUFFLE_PATH)
    with db:
        for row in data:
            pokemon, *pokemon_data = row.split("\t")
            db.executemany(
                """
                INSERT INTO eb_details (pokemon, start_level, end_level, stage_index)
                VALUES (?, ?, ?, ?)""",
                (
                    (pokemon,) + tuple(map(int, range_data.split("/")))
                    for range_data in pokemon_data
                ),
            )


def populate_eb_rewards() -> None:
    with open(EB_REWARDS, encoding="utf-8") as f:
        data = f.readlines()

    db = sqlite3.connect(DB_SHUFFLE_PATH)
    with db:
        for row in data:
            pokemon, *pokemon_data = row.split("\t")
            for stage_data in pokemon_data:
                level, reward, other = stage_data.split("/")
                amount, *alternative = other.split()
                db.execute(
                    """
                INSERT INTO eb_rewards (pokemon, level, reward, amount, alternative)
                VALUES (?, ?, ?, ?, ?)""",
                    (
                        pokemon,
                        int(level),
                        reward,
                        int(amount),
                        " ".join(alternative),
                    ),
                )


def populate_special_tables() -> None:
    populate_eb_details()
    populate_eb_rewards()


def make_table(
    table: Table, base_path: Path, conn: sqlite3.Connection
) -> pandas.DataFrame:
    df = pandas.read_csv(
        base_path / f"{table.name}.txt",
        sep="\t",
        names=list(table.columns.keys()),
        converters=table.columns,
        skiprows=1 if table.has_header else lambda _: False,
    )
    df.to_sql(
        name=table.name,
        con=conn,
        if_exists="append",
        index=not table.has_id_col,
        index_label=None if table.id_label else "id",
    )
    return df


def make_tables() -> None:
    with open("queries/create_bot_tables.sql", encoding="utf-8") as f:
        query = f.read()
    sqlite3.Connection(DB_BOT_PATH).executescript(query)
    with open("queries/create_shuffle_tables.sql", encoding="utf-8") as f:
        query = f.read()
    sqlite3.Connection(DB_SHUFFLE_PATH).executescript(query)


def main() -> None:
    make_tables()
    bot_c = sqlite3.Connection(DB_BOT_PATH)
    for table in BOT_TABLES:
        make_table(table, BOT_TABLES_PATH, bot_c)
    shuffle_c = sqlite3.Connection(DB_SHUFFLE_PATH)
    for table in SHUFFLE_TABLES:
        make_table(table, SHUFFLE_TABLES_PATH, shuffle_c)
    populate_special_tables()


if __name__ == "__main__":
    main()
