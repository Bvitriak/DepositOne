from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from flask_login import UserMixin
from core_service.app.db import get_db

@dataclass(slots=True)
class User(UserMixin):
    id: int
    username: str
    email: str
    password_hash: str | None
    token: str | None
    role: str
    _is_active: bool
    created_at: str

    @property
    def is_active(self) -> bool:
        return self._is_active

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        return cls(
            id=row["id"],
            username=row["user_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            token=row["token"],
            role=row["role"],
            _is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    @classmethod
    def get_by_id(cls, user_id: int):
        db = get_db()
        row = db.execute(
            """
            SELECT id, user_name, email, password_hash, token, role, is_active, created_at
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_username(cls, user_name: str):
        db = get_db()
        row = db.execute(
            """
            SELECT id, user_name, email, password_hash, token, role, is_active, created_at
            FROM users
            WHERE user_name = ?
            LIMIT 1
            """,
            (user_name,),
        ).fetchone()
        return cls.from_row(row) if row else None
