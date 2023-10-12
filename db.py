import sqlite3
from typing import Any, Iterator

from models import (
    Command,
    Drop,
    EBReward,
    EBStretch,
    Event,
    EventPokemon,
    EventStageRotation,
    Pokemon,
    PokemonType,
    Reminder,
    RotationEvent,
    Setting,
    Skill,
    SMReward,
    Stage,
    StageType,
)

DB_BOT_PATH = "bot.sqlite"
DB_SHUFFLE_PATH = "shuffle.sqlite"
STAGE_TYPE_TABLE = {
    StageType.MAIN: "main_stages",
    StageType.EXPERT: "expert_stages",
    StageType.EVENT: "event_stages",
}

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


def get_all_event_pokemon() -> Iterator[EventPokemon]:
    q = shuffle_connection.execute(
        """
        SELECT
            stage_type, pokemon, repeat_type, repeat_param_1,
            repeat_param_2, date_start, date_end, duration
        FROM events
        """,
    )
    for p in q.fetchall():
        yield EventPokemon(**p)


def query_stage_by_index(index: int, stage_type: StageType) -> Stage:
    q = shuffle_connection.execute(
        f"""
        SELECT * FROM {STAGE_TYPE_TABLE[stage_type]}
        WHERE id = :id
        """,
        {"id": index},
    ).fetchone()
    if not q:
        raise ValueError(f"Invalid stage index: {index}")
    return Stage(stage_type=stage_type, **q)


def query_stage_by_pokemon(pokemon: str, stage_type: StageType) -> Iterator[Stage]:
    q = shuffle_connection.execute(
        f"""
        SELECT * FROM {STAGE_TYPE_TABLE[stage_type]}
        WHERE pokemon = :pokemon
        COLLATE NOCASE
        """,
        {"pokemon": pokemon},
    )
    for stage in q.fetchall():
        yield Stage(stage_type=stage_type, **stage)


def query_event_by_pokemon(pokemon: str) -> Iterator[Event]:
    q = shuffle_connection.execute(
        """
        SELECT * FROM events
        WHERE pokemon = ':pokemon'
        OR pokemon LIKE ':pokemon/%' 
        OR pokemon LIKE '%/:pokemon'
        OR pokemon LIKE '%/:pokemon/%'
        COLLATE NOCASE
        """,
        {"pokemon": pokemon},
    )
    for event in q.fetchall():
        yield Event(**event)


def get_all_stages(stage_type: StageType) -> Iterator[Stage]:
    q = shuffle_connection.execute(f"SELECT * FROM {STAGE_TYPE_TABLE[stage_type]}")
    for stage in q.fetchall():
        yield Stage(stage_type=stage_type, **stage)


def get_pokemon_names() -> set[str]:
    q = shuffle_connection.execute(
        """
        SELECT pokemon
        FROM pokemon
        """
    ).fetchall()
    return {x["pokemon"] for x in q}


def get_skill_names() -> set[str]:
    q = shuffle_connection.execute(
        """
        SELECT skill
        FROM skills
        """
    ).fetchall()
    return {x["skill"] for x in q}


def query_eb_pokemon(pokemon: str) -> list[EBStretch]:
    q = shuffle_connection.execute(
        """
        SELECT pokemon, start_level, end_level, stage_index
        FROM eb_details
        WHERE pokemon = :pokemon
        ORDER BY id
        """,
        {"pokemon": pokemon},
    )
    return [EBStretch(**leg) for leg in q.fetchall()]


def query_pokemon_type(pokemon: str) -> PokemonType:
    q = shuffle_connection.execute(
        """
        SELECT type
        FROM pokemon
        WHERE pokemon = :pokemon
        """,
        {"pokemon": pokemon},
    )
    return PokemonType(q.fetchone()["type"])


def query_stage_notes(stage_id: str) -> str:
    q = shuffle_connection.execute(
        """
        SELECT notes
        FROM stage_notes
        WHERE stage_id = :stage_id
        """,
        {"stage_id": stage_id},
    ).fetchone()
    if not q:
        return ""
    return q["notes"]


def query_eb_rewards_pokemon(pokemon: str) -> list[EBReward]:
    q = shuffle_connection.execute(
        """
        SELECT pokemon, level, reward, amount, alternative
        FROM eb_rewards
        WHERE pokemon = :pokemon
        ORDER BY id
        """,
        {"pokemon": pokemon},
    )
    return [EBReward(**stage) for stage in q.fetchall()]


def query_weak_against(t: PokemonType) -> list[PokemonType]:
    q = shuffle_connection.execute(
        """
        SELECT weak
        FROM types
        WHERE type = :type
        """,
        {"type": str(t)},
    ).fetchone()
    if not q:
        return []
    return [PokemonType(t) for t in q["weak"].split(", ")]


def get_all_pokemon() -> Iterator[Pokemon]:
    q = shuffle_connection.execute(
        """
        SELECT * FROM pokemon ORDER BY id
        """
    )
    for pokemon in q.fetchall():
        yield Pokemon(**pokemon)


def query_pokemon(pokemon: str) -> Pokemon | None:
    q = shuffle_connection.execute(
        """
        SELECT * FROM pokemon
        WHERE pokemon = :pokemon
        """,
        {"pokemon": pokemon},
    ).fetchone()
    if not q:
        return None
    return Pokemon(**q)


def get_sm_rewards() -> list[SMReward]:
    q = shuffle_connection.execute(
        """
        SELECT
        level, first_reward_type AS reward, first_reward_amount AS amount,
        repeat_reward_type AS reward_repeat, repeat_reward_amount AS amount_repeat
        FROM sm_rewards
        ORDER BY level
        """
    )
    return [SMReward(**reward) for reward in q.fetchall()]


def get_reminders() -> Iterator[Reminder]:
    q = shuffle_connection.execute(
        """
        SELECT user_id, weeks AS _weeks, pokemon AS _pokemon
        FROM reminders
        ORDER BY id
        """
    )
    for reminder in q.fetchall():
        yield Reminder(**reminder)


def query_skill(skill: str) -> Skill | None:
    q = shuffle_connection.execute(
        """
        SELECT * FROM skills
        LEFT JOIN skill_notes
        ON skills.name = skill_notes.name
        WHERE skill = :skill
        """,
        {"skill": skill},
    ).fetchone()
    if not q:
        return None
    return Skill(**q)


def query_ap(bp: int) -> list[int]:
    q = shuffle_connection.execute(
        f"""
        SELECT {', '.join(f"lvl{i}" for i in range(1, 31))} FROM ap
        WHERE base_ap = :bp
        """,
        {"bp": bp},
    ).fetchone()
    if not q:
        return []
    return sorted(q.values())

def query_exp(bp: int) -> list[int]:
    q = shuffle_connection.execute(
        f"""
        SELECT {', '.join(f"lvl{i}" for i in range(1, 31))} FROM exp
        WHERE base_ap = :bp
        """,
        {"bp": bp},
    ).fetchone()
    if not q:
        return []
    return sorted(q.values())

if __name__ == "__main__":
    ...
