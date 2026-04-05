import os
import sqlite3
from pathlib import Path
from threading import Lock
from flask import g
from core_service.app.constants import DEFAULT_MASTER_DB, DEFAULT_SLAVE_DB

MASTER_DB = os.environ.get("DB_MASTER", DEFAULT_MASTER_DB)
SLAVE_DB = os.environ.get("DB_SLAVE", DEFAULT_SLAVE_DB)
_replication_lock = Lock()

def _apply_pragmas(conn: sqlite3.Connection, *, readonly: bool = False):
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    if not readonly:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")

def connect(path: str, *, readonly: bool = False):
    if readonly:
        conn = sqlite3.connect(
            f"file:{path}?mode=ro",
            uri=True,
            check_same_thread=False,
        )
    else:
        conn = sqlite3.connect(path, check_same_thread=False)

    _apply_pragmas(conn, readonly=readonly)
    return conn

def _ensure_parent_dirs():
    Path(MASTER_DB).parent.mkdir(parents=True, exist_ok=True)
    Path(SLAVE_DB).parent.mkdir(parents=True, exist_ok=True)

def sync_slave_db(force: bool = False) -> bool:
    master = Path(MASTER_DB)
    slave = Path(SLAVE_DB)

    if not master.exists():
        return False

    _ensure_parent_dirs()

    with _replication_lock:
        if not force and slave.exists() and master.stat().st_mtime <= slave.stat().st_mtime:
            return True

        temp_slave = slave.with_suffix(slave.suffix + ".tmp")

        with (
            sqlite3.connect(str(master), check_same_thread=False) as src,
            sqlite3.connect(str(temp_slave), check_same_thread=False) as dst,
        ):
            src.execute("PRAGMA wal_checkpoint(FULL)")
            src.backup(dst)

        os.replace(temp_slave, slave)
        return True

def get_db():
    if "db_master" not in g:
        _ensure_parent_dirs()
        g.db_master = connect(str(Path(MASTER_DB)), readonly=False)
    return g.db_master

def get_db_read():
    if "db_slave" not in g:
        try:
            sync_slave_db()
            if Path(SLAVE_DB).exists():
                g.db_slave = connect(str(Path(SLAVE_DB)), readonly=True)
            else:
                g.db_slave = connect(str(Path(MASTER_DB)), readonly=True)
        except (sqlite3.Error, OSError):
            g.db_slave = connect(str(Path(MASTER_DB)), readonly=False)
    return g.db_slave

def refresh_slave_after_write() -> bool:
    try:
        master = get_db()
        master.execute("PRAGMA wal_checkpoint(FULL)")
        master.commit()
        return sync_slave_db(force=True)
    except (sqlite3.Error, OSError):
        return False

def teardown_db(_exception):
    for attr in ("db_master", "db_slave"):
        conn = g.pop(attr, None)
        if conn is not None:
            conn.close()
