from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from typing import Any, Sequence
from core_service.app.db import get_db

@dataclass(slots=True)
class BaseModel:
    table_name: str = field(init=False, repr=False, default="")
    db: sqlite3.Connection | None = field(default=None, repr=False)

    @property
    def conn(self) -> sqlite3.Connection:
        return self.db if self.db is not None else get_db()

    def execute(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> sqlite3.Cursor:
        cursor = self.conn.execute(sql, params or [])
        self.conn.commit()
        return cursor

    def fetch_one(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> sqlite3.Row | None:
        return self.conn.execute(sql, params or []).fetchone()

    def fetch_all(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params or []).fetchall()
