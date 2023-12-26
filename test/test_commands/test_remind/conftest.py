import shutil
import sqlite3
from pathlib import Path
from typing import Iterator

import pytest

import db


@pytest.fixture(name="db_copy", scope="session")
def _db_copy(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    tmp_dir = tmp_path_factory.mktemp("db_copy")
    original = db.DB_SHUFFLE_PATH
    new_path = tmp_dir / "shuffle_copy.sqlite"
    shutil.copy(original, new_path)
    yield new_path


@pytest.fixture(scope="function", autouse=True)
def patch_shuffle_db_wipe_reminders(
    monkeypatch: pytest.MonkeyPatch, db_copy: Path
) -> Iterator[None]:
    _db = sqlite3.Connection(db_copy)
    _db.row_factory = db.dict_factory
    _db.execute("DELETE FROM reminders")
    _db.execute("UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'reminders'")
    _db.commit()
    monkeypatch.setattr(db, "shuffle_connection", _db)
    yield
    _db.close()
