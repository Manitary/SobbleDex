import sqlite3

# TODO populating other tables with straight imports of tsv files

EB_DETAILS = "shuffle_tables/eb_details.txt"
EB_REWARDS = "shuffle_tables/eb_rewards.txt"
DB_BOT_PATH = "bot.sqlite"
DB_SHUFFLE_PATH = "shuffle.sqlite"


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
