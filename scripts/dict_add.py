#!/usr/bin/env python3
"""Add or update a dictionary entry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.dictionary import Dictionary


def main() -> None:
    parser = argparse.ArgumentParser(description="Add or update an Ido dictionary entry")
    parser.add_argument("word", nargs="?", help="Ido word (e.g. hom.o)")
    parser.add_argument("root", nargs="?", help="Morphological root")
    parser.add_argument("translation", nargs="?", help="English gloss")
    parser.add_argument("--notes", help="Optional notes")
    args = parser.parse_args()

    word = args.word
    root = args.root
    translation = args.translation

    if not word:
        word = input("Ido word: ").strip()
    if not root:
        root = input("Root (leave blank to infer): ").strip() or None
    if not translation:
        translation = input("English: ").strip()

    if not word or not translation:
        print("Error: word and translation are required", file=sys.stderr)
        sys.exit(1)

    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        entry = db.add_word(word, root, translation, notes=args.notes)
        print("Saved:")
        print(db.format_entry(entry))
    finally:
        db.close()


if __name__ == "__main__":
    main()
