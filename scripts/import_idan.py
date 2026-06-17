#!/usr/bin/env python3
"""Import idan.txt into data/ido.db (idempotent; preserves user entries)."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import init_db, rebuild_fts
from ido.paths import DB_PATH, IDAN_PATH


def parse_root(word: str) -> str:
    """Return the morphological root (first dot-separated segment)."""
    if "." in word:
        return word.split(".", 1)[0]
    return word


def is_letter_header(line: str) -> bool:
    return bool(re.match(r"^\s*[A-Z]\s*$", line))


def is_entry_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("---"):
        return False
    if line.startswith("        "):
        return True
    if not (stripped[0].isalpha() or stripped[0] in "-["):
        return False
    return bool(re.search(r"\s\s+|\t", line))


def parse_entry(line: str) -> dict | None:
    if not is_entry_line(line):
        return None

    is_derived = line.startswith("        ")
    clean = line.strip()

    if clean.startswith("["):
        clean = clean.lstrip("[")

    parts = re.split(r"\s\s+|\t", clean, maxsplit=1)
    if len(parts) < 2:
        return None

    word_part = parts[0].strip()
    rest = parts[1].strip()

    word_part = re.sub(r"\s*\[[^\]]+\]", "", word_part)
    word_part = re.sub(r"\s*\{[^}]+\}", "", word_part)
    word_part = re.sub(r"\s*\([^)]+\)", "", word_part).strip()
    if not word_part:
        return None

    rest = re.sub(r"^\([^)]+\)\s*", "", rest)
    rest = re.sub(r"^\{[^}]+\}\s*", "", rest)
    rest = re.sub(r"^\[[^\]]+\]\s*", "", rest)

    return {
        "word": word_part,
        "root": parse_root(word_part),
        "translation": rest,
        "is_derived": is_derived,
    }


def find_abbr_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if "Abreviuri en Ido" in line or "Abbreviations in Ido" in line:
            return i
    return len(lines)


def _insert_word(
    conn: sqlite3.Connection,
    entry: dict,
    parent_id: int | None,
) -> tuple[int | None, bool]:
    parent = parent_id if entry["is_derived"] else None
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO words (word, root, translation, parent_id, source)
        VALUES (?, ?, ?, ?, 'idan')
        """,
        (entry["word"], entry["root"], entry["translation"], parent),
    )
    if cursor.rowcount:
        return cursor.lastrowid, True
    return None, False


def import_idan(
    conn: sqlite3.Connection,
    lines: list[str],
    *,
    end_line: int,
) -> dict[str, int]:
    stats = {"inserted": 0, "skipped": 0, "derived": 0}
    current_parent_id: int | None = None
    pending: dict | None = None

    def flush_pending() -> None:
        nonlocal pending, current_parent_id
        if not pending:
            return
        row_id, inserted = _insert_word(conn, pending, current_parent_id)
        if inserted:
            stats["inserted"] += 1
            if pending["is_derived"]:
                stats["derived"] += 1
            elif row_id is not None:
                current_parent_id = row_id
        else:
            stats["skipped"] += 1
            if not pending["is_derived"]:
                row = conn.execute(
                    "SELECT id FROM words WHERE word = ?", (pending["word"],)
                ).fetchone()
                if row:
                    current_parent_id = row[0]
        pending = None

    for line_num, line in enumerate(lines[:end_line], start=1):
        if line_num < 47 or is_letter_header(line):
            continue

        if not is_entry_line(line) and line.strip():
            if pending and not line.startswith("        "):
                pending["translation"] += " " + line.strip()
            continue

        entry = parse_entry(line)
        if not entry:
            continue

        flush_pending()
        pending = entry

    flush_pending()
    conn.commit()
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Import idan.txt into data/ido.db")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="Database path")
    parser.add_argument("--dict", type=Path, default=IDAN_PATH, help="idan.txt path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate the database from schema before importing",
    )
    args = parser.parse_args()

    if not args.dict.exists():
        print(f"Error: dictionary file not found: {args.dict}", file=sys.stderr)
        sys.exit(1)

    if args.force:
        init_db(args.db, force=True)
    elif not args.db.exists():
        init_db(args.db)

    lines = args.dict.read_text(encoding="utf-8").splitlines(keepends=True)
    end_line = max(0, find_abbr_start(lines) - 10)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    try:
        stats = import_idan(conn, lines, end_line=end_line)
        rebuild_fts(conn)
        total = conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    finally:
        conn.close()

    print("Import complete")
    print(f"  Inserted: {stats['inserted']}")
    print(f"  Skipped (already present): {stats['skipped']}")
    print(f"  Derived entries inserted: {stats['derived']}")
    print(f"  Total words in database: {total}")
    print(f"Database: {args.db}")


if __name__ == "__main__":
    main()
