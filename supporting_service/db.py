from __future__ import annotations
import os
import sqlite3
from typing import Final
from supporting_service.constants import DEFAULT_DATABASE

BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE: Final[str] = os.path.join(BASE_DIR, DEFAULT_DATABASE)

def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(
        DATABASE,
        detect_types=sqlite3.PARSE_DECLTYPES,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn
