"""Conexión y creación de la base SQLite."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from paths import DB_PATH, SCHEMA_PATH


class DatabaseError(RuntimeError):
    """La base no existe, está incompleta o no se puede abrir."""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Abre la base y falla rápido si falta o está incompleta."""
    path = Path(db_path) if db_path else DB_PATH
    if not path.exists():
        raise DatabaseError(
            f"No existe la base: {path}\n"
            "Ejecuta: .venv/bin/python main.py import --force"
        )

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _verify_schema(conn)
    return conn


def _verify_schema(conn: sqlite3.Connection) -> None:
    required = {"words", "words_fts"}
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table')"
    ).fetchall()
    present = {row["name"] for row in rows}
    missing = required - present
    if missing:
        raise DatabaseError(
            "La base está incompleta "
            f"(faltan: {', '.join(sorted(missing))}).\n"
            "Ejecuta: .venv/bin/python main.py import --force"
        )


def init_db(db_path: Path | str | None = None, *, force: bool = False) -> Path:
    """Crea una base nueva desde data/schema.sql."""
    path = Path(db_path) if db_path else DB_PATH
    if path.exists():
        if force:
            path.unlink()
        else:
            raise DatabaseError(f"La base ya existe: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    if not SCHEMA_PATH.exists():
        raise DatabaseError(f"No existe el esquema: {SCHEMA_PATH}")

    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
    return path


def rebuild_fts(conn: sqlite3.Connection) -> None:
    """Reconstruye el índice de texto completo."""
    conn.execute("INSERT INTO words_fts(words_fts) VALUES ('rebuild')")
    conn.commit()


def die_on_db_error(exc: DatabaseError) -> None:
    """Muestra el error y termina con código 1."""
    print(exc, file=sys.stderr)
    sys.exit(1)
