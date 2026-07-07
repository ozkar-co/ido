"""Phrase collection for Ido-English sentence pairs."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from ido.db import connect
from ido.paths import DB_PATH


@dataclass
class Phrase:
    id: int
    ido: str
    english: str
    source: str
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Phrase:
        return cls(
            id=row["id"],
            ido=row["ido"],
            english=row["english"],
            source=row["source"],
            created_at=row["created_at"],
        )


class PhraseStore:
    """Store and search Ido-English phrase pairs."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(DB_PATH)
        self._conn = connect(self.db_path)

    def close(self) -> None:
        self._conn.close()

    def add(self, ido: str, english: str, *, source: str = "user") -> Phrase:
        cursor = self._conn.execute(
            """
            INSERT INTO phrases (ido, english, source)
            VALUES (?, ?, ?)
            """,
            (ido.strip(), english.strip(), source),
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM phrases WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return Phrase.from_row(row)

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS n FROM phrases").fetchone()
        return int(row["n"])

    def search(
        self,
        query: str,
        *,
        field: str = "both",
        limit: int = 20,
    ) -> list[Phrase]:
        q = query.strip()
        if not q:
            return []

        if field == "ido":
            rows = self._conn.execute(
                """
                SELECT p.*
                FROM phrases_fts f
                JOIN phrases p ON p.id = f.rowid
                WHERE phrases_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (q, limit),
            ).fetchall()
        elif field == "en":
            rows = self._conn.execute(
                """
                SELECT p.*
                FROM phrases_fts f
                JOIN phrases p ON p.id = f.rowid
                WHERE phrases_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (q, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT p.*
                FROM phrases_fts f
                JOIN phrases p ON p.id = f.rowid
                WHERE phrases_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (q, limit),
            ).fetchall()

        if rows:
            return [Phrase.from_row(r) for r in rows]

        pattern = f"%{q}%"
        if field == "ido":
            rows = self._conn.execute(
                "SELECT * FROM phrases WHERE ido LIKE ? ORDER BY id DESC LIMIT ?",
                (pattern, limit),
            ).fetchall()
        elif field == "en":
            rows = self._conn.execute(
                "SELECT * FROM phrases WHERE english LIKE ? ORDER BY id DESC LIMIT ?",
                (pattern, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT * FROM phrases
                WHERE ido LIKE ? OR english LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (pattern, pattern, limit),
            ).fetchall()
        return [Phrase.from_row(r) for r in rows]

    def list_recent(self, *, limit: int = 20) -> list[Phrase]:
        rows = self._conn.execute(
            "SELECT * FROM phrases ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [Phrase.from_row(r) for r in rows]

    def format_phrase(self, phrase: Phrase) -> str:
        return f"[{phrase.id}] {phrase.ido}\n  → {phrase.english}"
