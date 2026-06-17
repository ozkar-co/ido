"""Database connection and schema management."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from ido.paths import DB_PATH, SCHEMA_PATH


class DatabaseError(RuntimeError):
    """Raised when the database is missing or invalid."""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection to the Ido database.

    Fails fast if the database file does not exist.
    """
    path = Path(db_path) if db_path else DB_PATH
    if not path.exists():
        raise DatabaseError(
            f"Database not found: {path}\nRun: python scripts/import_idan.py"
        )

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _verify_schema(conn)
    return conn


def _verify_schema(conn: sqlite3.Connection) -> None:
    required = {"words", "words_fts", "phrases", "phrases_fts"}
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table')"
    ).fetchall()
    present = {row["name"] for row in rows}
    missing = required - present
    if missing:
        raise DatabaseError(
            f"Database schema is incomplete (missing: {', '.join(sorted(missing))}).\n"
            "Run: python scripts/import_idan.py"
        )


def init_db(db_path: Path | str | None = None, *, force: bool = False) -> Path:
    """Create a new database from schema.sql."""
    path = Path(db_path) if db_path else DB_PATH
    if path.exists():
        if force:
            path.unlink()
        else:
            raise DatabaseError(f"Database already exists: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    if not SCHEMA_PATH.exists():
        raise DatabaseError(f"Schema file not found: {SCHEMA_PATH}")

    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return path


def rebuild_fts(conn: sqlite3.Connection) -> None:
    """Rebuild FTS indexes from content tables."""
    conn.execute("INSERT INTO words_fts(words_fts) VALUES ('rebuild')")
    conn.execute("INSERT INTO phrases_fts(phrases_fts) VALUES ('rebuild')")
    conn.commit()


def die_on_db_error(exc: DatabaseError) -> None:
    """Print a helpful message and exit."""
    print(exc, file=sys.stderr)
    sys.exit(1)
