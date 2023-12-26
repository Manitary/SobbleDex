import sqlite3
from pathlib import Path
from typing import Any, Iterator

from exceptions import InvalidBP, InvalidLevel
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
    TypeInfo,
)

DB_BOT_PATH = Path(__file__).resolve().parent.parent / "db" / "bot.sqlite"
DB_SHUFFLE_PATH = Path(__file__).resolve().parent.parent / "db" / "shuffle.sqlite"
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


def query_setting(key: str) -> Setting | None:
    q = bot_connection.execute(
        """
        SELECT key, value, tier
        FROM settings
        WHERE key = :key
        """,
        {"key": key},
    ).fetchone()
    if not q:
        return None
    return Setting(**q)


def update_setting(key: str, value: str) -> None:
    bot_connection.execute(
        """
        UPDATE settings
        SET value = :value
        WHERE key = :key
        """,
        {"key": key, "value": value},
    )
    bot_connection.commit()


def add_setting(setting: Setting) -> None:
    bot_connection.execute(
        """
        INSERT INTO settings (key, value, tier)
        VALUES (:key, :value, :tier)
        """,
        {"key": setting.key, "value": setting.value, "tier": setting.tier},
    )
    bot_connection.commit()


def remove_setting(key: str) -> None:
    bot_connection.execute(
        """
        DELETE FROM settings
        WHERE key = :key
        """,
        {"key": key},
    )
    bot_connection.commit()


def update_user_level(user_id: int, level: int) -> None:
    bot_connection.execute(
        """
        INSERT INTO user_levels (user_id, level)
        VALUES (:user_id, :level)
        ON CONFLICT DO UPDATE
        SET level = :level
        WHERE user_id = :user_id
        """,
        {"user_id": user_id, "level": level},
    )
    bot_connection.commit()


def query_user_level(user_id: int) -> int | None:
    q = bot_connection.execute(
        """
        SELECT level FROM user_levels
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
    ).fetchone()
    if not q:
        return None
    return q["level"]


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
        WHERE
            pokemon = :pokemon
        OR  pokemon LIKE :pokemon || '/%'
        OR  pokemon LIKE '%/' || :pokemon || '/%'
        OR  pokemon LIKE '%/' || :pokemon
        GROUP BY pokemon, date_start
        """,
        {"pokemon": pokemon},
    )
    for event in q.fetchall():
        yield Event(**event)


def get_all_stages(stage_type: StageType) -> Iterator[Stage]:
    q = shuffle_connection.execute(f"SELECT * FROM {STAGE_TYPE_TABLE[stage_type]}")
    for stage in q.fetchall():
        yield Stage(stage_type=stage_type, **stage)


def get_db_table_column(
    table: str, column: str, conn: sqlite3.Connection = shuffle_connection
) -> set[str]:
    #! Make sure the arguments can never be chosen by the end user.
    #! Otherwise, make sure to have some sanitisation is in place.
    q = conn.execute(
        f"""
        SELECT {column}
        FROM {table}
        """
    ).fetchall()
    return {x[column] for x in q}


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
        SELECT user_id, weeks, pokemon
        FROM reminders
        ORDER BY id
        """
    )
    for reminder in q.fetchall():
        yield Reminder(**reminder)


def query_reminder(user_id: int) -> Reminder | None:
    q = shuffle_connection.execute(
        """
        SELECT user_id, weeks, pokemon
        FROM reminders
        WHERE user_id = :user_id
        """,
        {"user_id": user_id},
    ).fetchone()
    if not q:
        return None
    return Reminder(**q)


def query_skill(skill: str) -> Skill | None:
    q = shuffle_connection.execute(
        """
        SELECT
        s.id AS id, s.skill AS skill, description, rate1, rate2, rate3,
        type, multiplier, bonus_effect, bonus1, bonus2, bonus3, bonus4,
        sp1, sp2, sp3, sp4, notes
        FROM skills s
        LEFT JOIN skill_notes sn
        ON s.skill = sn.skill
        WHERE s.skill = :skill
        """,
        {"skill": skill},
    ).fetchone()
    if not q:
        return None
    return Skill(**q)


def query_ap(bp: int) -> list[int]:
    """Return the sorted list of AP for the given BP.

    Raises:
        InvalidBP: if `bp` is not 30, 40, ..., 90.
    """
    q = shuffle_connection.execute(
        f"""
        SELECT {', '.join(f"lvl{i}" for i in range(1, 31))} FROM ap
        WHERE base_ap = :bp
        """,
        {"bp": bp},
    ).fetchone()

    if not q:
        raise InvalidBP()

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


def query_type(t: PokemonType) -> TypeInfo:
    q = shuffle_connection.execute(
        """
        SELECT * FROM types
        WHERE type = :type
        """,
        {"type": t.value},
    ).fetchone()
    return TypeInfo(**q)


def add_reminder_week(user_id: int, week: int) -> None:
    shuffle_connection.execute(
        """
        UPDATE reminders
        SET weeks = weeks || ", " || :week
        WHERE user_id = :user_id
        """,
        {"user_id": user_id, "week": str(week)},
    )
    shuffle_connection.commit()


def add_reminder_pokemon(user_id: int, pokemon: str) -> None:
    shuffle_connection.execute(
        """
        UPDATE reminders
        SET pokemon = pokemon || ", " || :pokemon
        WHERE user_id = :user_id
        """,
        {"user_id": user_id, "pokemon": pokemon},
    )
    shuffle_connection.commit()


def update_reminder(reminder: Reminder) -> None:
    shuffle_connection.execute(
        """
        UPDATE reminders
        SET weeks = :weeks, pokemon = :pokemon
        WHERE user_id = :user_id
        """,
        {
            "user_id": reminder.user_id,
            "weeks": reminder.weeks_str,
            "pokemon": reminder.pokemon_str,
        },
    )
    shuffle_connection.commit()


def query_custom_response(message: str) -> str:
    q = bot_connection.execute(
        """
        SELECT response
        FROM custom_responses
        WHERE message = :message
        """,
        {"message": message},
    ).fetchone()
    if not q:
        return ""
    return q["response"]


def query_help_message(message: str) -> str:
    q = shuffle_connection.execute(
        """
        SELECT message_text
        FROM help_messages
        WHERE message_type = 'message_help' || :message
        """,
        {"message": f"_{message}" if message else ""},
    ).fetchone()
    if not q:
        return ""
    return q["message_text"]


def query_commands(command: str) -> Command | None:
    q = bot_connection.execute(
        """
        SELECT
        command_name, module_name, method_name,
        command_type, command_tier, description
        FROM commands
        WHERE command_name = :command 
        """,
        {"command": command},
    ).fetchone()
    if not q:
        return None
    return Command(**q)


def add_custom_response(trigger: str, response: str) -> bool:
    try:
        bot_connection.execute(
            """
            INSERT INTO custom_responses
            (message, response)
            VALUES (:trigger, :response)
            """,
            {"trigger": trigger, "response": response},
        )
        bot_connection.execute(
            """
            INSERT INTO commands
            (command_name, module_name, method_name, command_type, command_tier)
            VALUES
            (:trigger, 'user_commands', 'custom_response', 'match', 1)
            """,
            {"trigger": trigger},
        )
        bot_connection.commit()
        return True
    except sqlite3.DatabaseError:
        bot_connection.rollback()
        return False


def remove_custom_response(trigger: str) -> bool:
    q = bot_connection.execute(
        """
        DELETE FROM custom_responses
        WHERE message = :message
        RETURNING message
        """,
        {"message": trigger},
    ).fetchone()
    if not q:
        return False
    bot_connection.execute(
        """
        DELETE FROM commands
        WHERE command_name = :message
        """,
        {"message": trigger},
    )
    bot_connection.commit()
    return True


def add_requestable_roles(guild_id: int, *role_id: int) -> None:
    bot_connection.executemany(
        """
        INSERT INTO requestable_roles (guild_id, role_id)
        VALUES (:guild, :role)
        ON CONFLICT DO NOTHING
        """,
        ({"guild": guild_id, "role": x} for x in role_id),
    )
    bot_connection.commit()


def remove_requestable_roles(guild_id: int, *role_id: int) -> None:
    bot_connection.executemany(
        """
        DELETE FROM requestable_roles
        WHERE guild_id = :guild AND role_id = :role
        """,
        ({"guild": guild_id, "role": x} for x in role_id),
    )
    bot_connection.commit()


def query_requestable_roles(guild_id: int) -> Iterator[int]:
    q = bot_connection.execute(
        """
        SELECT role_id
        FROM requestable_roles
        WHERE guild_id = :guild
        """,
        {"guild": guild_id},
    )
    for role in q.fetchall():
        yield role["role_id"]


def farming_stages(pokemon_name: str) -> list[Stage]:
    q = shuffle_connection.execute(
        """
        SELECT 'Main' AS stage_type, * FROM main_stages
        WHERE pokemon = :pokemon
        AND (drop_1_item = "PSB" or drop_2_item = "PSB" or drop_3_item = "PSB")
        UNION
        SELECT 'Event' AS stage_type, * FROM event_stages
        WHERE pokemon = :pokemon
        AND (drop_1_item = "PSB" or drop_2_item = "PSB" or drop_3_item = "PSB")
        """,
        {"pokemon": pokemon_name},
    )
    return [Stage(**stage) for stage in q.fetchall()]


def get_ap_at_level(bp: int, level: int) -> int:
    """Return the AP of a pokemon with the given BP and level.

    Raises:
        InvalidLevel: `level` is not 1, 2, ..., 30.
        InvalidBP: `bp` is not 30, 40, ..., 90.
    """
    try:
        assert isinstance(level, int)
        q = shuffle_connection.execute(
            f"""
            SELECT lvl{level} AS ap FROM ap
            WHERE base_ap = :bp
            """,
            {"bp": bp},
        ).fetchone()
    except (AssertionError, sqlite3.OperationalError) as e:
        raise InvalidLevel() from e
    if not q:
        raise InvalidBP()
    return q["ap"]


if __name__ == "__main__":
    ...
