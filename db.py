import sqlite3
from typing import Any, Iterator

from models import Command, Drop, EventStageRotation, RotationEvent, Setting

DB_BOT_PATH = "bot.sqlite"
DB_SHUFFLE_PATH = "shuffle.sqlite"

# TODO Initialise these connections in main where appropriate instead of using global variables


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict[str, Any]:
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))


bot_connection = sqlite3.connect(DB_BOT_PATH)
bot_connection.row_factory = dict_factory

shuffle_connection = sqlite3.connect(DB_SHUFFLE_PATH)
shuffle_connection.row_factory = dict_factory


def query_event_week(week: int) -> Iterator[RotationEvent]:
    q = shuffle_connection.execute(
        """
        SELECT stage_type, pokemon, stage_ids, cost_unlock, encounter_rates
        FROM events
        WHERE repeat_type = "Rotation"
        AND repeat_param_1 + 1 = :query_week
        """,
        {"query_week": week},
    )
    for event in q.fetchall():
        yield RotationEvent(**event)


def get_event_stage_by_index(index: int) -> EventStageRotation:
    q = shuffle_connection.execute(
        """
        SELECT cost_type, attempt_cost,
        drop_1_item, drop_1_amount, drop_2_item, drop_2_amount, drop_3_item, drop_3_amount,
        drop_1_rate, drop_2_rate, drop_3_rate, items_available
        FROM event_stages
        WHERE id = :stage_id""",
        {"stage_id": index},
    ).fetchone()
    if not q:
        raise ValueError(f"No event stage with index {index}")
    drops = [
        Drop(q["drop_1_item"], q["drop_1_amount"], q["drop_1_rate"]),
        Drop(q["drop_2_item"], q["drop_2_amount"], q["drop_2_rate"]),
        Drop(q["drop_3_item"], q["drop_3_amount"], q["drop_3_rate"]),
    ]
    stage = EventStageRotation(
        q["cost_type"], q["attempt_cost"], drops, q["items_available"]
    )
    return stage


def get_settings() -> Iterator[Setting]:
    q = bot_connection.execute(
        """
        SELECT key, value, tier
        FROM settings
        """
    )
    for setting in q.fetchall():
        yield Setting(**setting)


def get_commands() -> Iterator[Command]:
    q = bot_connection.execute(
        """
        SELECT command_name, module_name, method_name, command_type, command_tier, description
        FROM commands
        """
    )
    for command in q.fetchall():
        yield Command(**command)


def get_aliases() -> dict[str, str]:
    q = shuffle_connection.execute(
        """
        SELECT alias, original_name
        FROM aliases
        """
    )
    return {entry["alias"].lower(): entry["original_name"] for entry in q.fetchall()}


def query_eb_pokemon_by_week(week: int) -> str:
    q = shuffle_connection.execute(
        """
        SELECT pokemon
        FROM events
        WHERE 
        stage_type = "Escalation"
        AND  (
            repeat_param_1 + 1 = :week
            OR (
                repeat_param_1 + 2 = :week
                AND duration = "14 days"
            )
        )
        """,
        {"week": week},
    ).fetchone()
    if not q:
        return ""
    return q["pokemon"]


def get_farmable_pokemon() -> set[str]:
    q = shuffle_connection.execute(
        """
        SELECT pokemon
        FROM main_stages
        WHERE (drop_1_item = "PSB" or drop_2_item = "PSB" or drop_3_item = "PSB")
        UNION
        SELECT pokemon
        FROM expert_stages
        WHERE (drop_1_item = "PSB" or drop_2_item = "PSB" or drop_3_item = "PSB")
        UNION
        SELECT pokemon
        FROM event_stages
        WHERE (drop_1_item = "PSB" or drop_2_item = "PSB" or drop_3_item = "PSB")
        """
    )
    return {x["pokemon"] for x in q.fetchall()}


def add_aliases(original: str, *aliases: str) -> tuple[list[str], list[str], list[str]]:
    success: list[str] = []
    duplicate: list[str] = []
    failure: list[str] = []
    for alias in aliases:
        try:
            shuffle_connection.execute(
                """
                INSERT INTO aliases (alias, original_name)
                VALUES (?, ?)
                """,
                (alias, original),
            )
            shuffle_connection.commit()
        except sqlite3.IntegrityError:
            print("Integrity:", alias)
            duplicate.append(alias)
        except sqlite3.DatabaseError as e:
            print(f"{alias} - {e}")
            failure.append(alias)
        else:
            success.append(alias)
    return success, duplicate, failure


def remove_aliases(*aliases: str) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    success: list[tuple[str, str]] = []
    not_exist: list[str] = []
    failure: list[str] = []
    for alias in aliases:
        try:
            q = shuffle_connection.execute(
                """
                DELETE FROM aliases 
                WHERE alias = :alias
                COLLATE NOCASE
                RETURNING alias, original_name
                """,
                {"alias": alias},
            ).fetchone()
            shuffle_connection.commit()
        except sqlite3.DatabaseError as e:
            print(f"{alias} - {e}")
            failure.append(alias)
        else:
            if q:
                success.append((q["original_name"], q["alias"]))
            else:
                not_exist.append(alias)
    return success, not_exist, failure


if __name__ == "__main__":
    ...
