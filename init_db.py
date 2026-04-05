import sqlite3
from pathlib import Path

DB_PATH = Path("database/depositBank.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    token TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS depositors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    createdbyuserid INTEGER NOT NULL,
    lastname TEXT NOT NULL,
    firstname TEXT NOT NULL,
    middlename TEXT,
    passportseries TEXT NOT NULL,
    passportnumber TEXT NOT NULL,
    issuedby TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    createdat TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (createdbyuserid) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depositor_id INTEGER NOT NULL,
    opened_by_user_id INTEGER NOT NULL,
    deposit_type TEXT NOT NULL,
    amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    currency TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL,
    capitalization INTEGER NOT NULL DEFAULT 0,
    auto_renewal INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (depositor_id) REFERENCES depositors(id),
    FOREIGN KEY (opened_by_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deposit_id INTEGER NOT NULL,
    created_by_user_id INTEGER NOT NULL,
    contract_number TEXT NOT NULL UNIQUE,
    contract_date TEXT NOT NULL,
    term_description TEXT,
    special_conditions TEXT,
    is_signed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (deposit_id) REFERENCES deposits(id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS interest_accruals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deposit_id INTEGER NOT NULL,
    accrual_date TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (deposit_id) REFERENCES deposits(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deposit_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,
    amount REAL NOT NULL,
    operation_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (deposit_id) REFERENCES deposits(id)
);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
        print(f"Schema initialized in {DB_PATH}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
