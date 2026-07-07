"""Ido-English dictionary access."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from ido.db import connect
from ido.lexer import dotted_to_solid, format_word_display, lex, query_variants
from ido.paths import DB_PATH


@dataclass
class WordEntry:
    id: int
    word: str
    root: str | None
    translation: str
    parent_id: int | None
    source: str
    notes: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> WordEntry:
        return cls(
            id=row["id"],
            word=row["word"],
            root=row["root"],
            translation=row["translation"],
            parent_id=row["parent_id"],
            source=row["source"],
            notes=row["notes"],
        )


class Dictionary:
    """Query and update the Ido-English word list."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(DB_PATH)
        self._conn = connect(self.db_path)

    def close(self) -> None:
        self._conn.close()

    def lookup_ido(self, word: str) -> WordEntry | None:
        """Look up an Ido word (dotted, solid, or inferred form)."""
        for variant in query_variants(word):
            row = self._conn.execute(
                "SELECT * FROM words WHERE word = ?", (variant,)
            ).fetchone()
            if row:
                return WordEntry.from_row(row)

            row = self._conn.execute(
                "SELECT * FROM words WHERE word = ? COLLATE NOCASE", (variant,)
            ).fetchone()
            if row:
                return WordEntry.from_row(row)

        solid = dotted_to_solid(word) if "." in word else word.strip().lower()
        row = self._conn.execute(
            """
            SELECT * FROM words
            WHERE replace(word, '.', '') = ? COLLATE NOCASE
            LIMIT 1
            """,
            (solid,),
        ).fetchone()
        return WordEntry.from_row(row) if row else None

    def lookup_en(self, term: str, *, limit: int = 20) -> list[WordEntry]:
        """Find Ido words by English gloss (FTS token search)."""
        query = term.strip()
        if not query:
            return []

        rows = self._conn.execute(
            """
            SELECT w.*
            FROM words_fts f
            JOIN words w ON w.id = f.rowid
            WHERE words_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        ).fetchall()

        if rows:
            return [WordEntry.from_row(r) for r in rows]

        # Fallback: substring match on translation.
        rows = self._conn.execute(
            """
            SELECT * FROM words
            WHERE translation LIKE ?
            ORDER BY word
            LIMIT ?
            """,
            (f"%{query}%", limit),
        ).fetchall()
        return [WordEntry.from_row(r) for r in rows]

    def by_root(self, root: str) -> list[WordEntry]:
        """Return all words sharing a morphological root."""
        rows = self._conn.execute(
            "SELECT * FROM words WHERE root = ? ORDER BY word",
            (root,),
        ).fetchall()
        return [WordEntry.from_row(r) for r in rows]

    def list_derived(self, word: str) -> list[WordEntry]:
        """Return words derived from the given headword."""
        rows = self._conn.execute(
            """
            SELECT child.*
            FROM words parent
            JOIN words child ON child.parent_id = parent.id
            WHERE parent.word = ?
            ORDER BY child.word
            """,
            (word,),
        ).fetchall()
        return [WordEntry.from_row(r) for r in rows]

    def add_word(
        self,
        word: str,
        root: str | None,
        translation: str,
        *,
        notes: str | None = None,
        parent_id: int | None = None,
    ) -> WordEntry:
        """Add or update a user-sourced dictionary entry."""
        parsed = lex(word)
        canonical = parsed.dotted
        if root is None:
            root = parsed.root

        self._conn.execute(
            """
            INSERT INTO words (word, root, translation, parent_id, source, notes)
            VALUES (?, ?, ?, ?, 'user', ?)
            ON CONFLICT(word) DO UPDATE SET
                root = excluded.root,
                translation = excluded.translation,
                notes = COALESCE(excluded.notes, words.notes),
                source = 'user'
            """,
            (canonical, root, translation, parent_id, notes),
        )
        self._conn.commit()
        entry = self.lookup_ido(canonical)
        if entry is None:
            raise RuntimeError(f"Failed to save word: {canonical}")
        return entry

    def format_entry(self, entry: WordEntry, *, derived: list[WordEntry] | None = None) -> str:
        lines = [format_word_display(entry.word)]
        if entry.root:
            lines.append(f"  Root: {entry.root}")
        lines.append(f"  English: {entry.translation}")
        if entry.source != "idan":
            lines.append(f"  Source: {entry.source}")
        if entry.notes:
            lines.append(f"  Notes: {entry.notes}")
        if derived:
            lines.append("  Derived:")
            for child in derived:
                child_display = format_word_display(child.word)
                lines.append(f"    {child_display}  {child.translation}")
        return "\n".join(lines)
