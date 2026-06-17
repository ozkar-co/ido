#!/usr/bin/env python3
"""Add an Ido-English phrase pair."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.phrases import PhraseStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Add an Ido-English phrase")
    parser.add_argument("ido", nargs="?", help="Phrase in Ido")
    parser.add_argument("english", nargs="?", help="English translation")
    args = parser.parse_args()

    ido = args.ido or input("Ido: ").strip()
    english = args.english or input("English: ").strip()

    if not ido or not english:
        print("Error: both Ido and English are required", file=sys.stderr)
        sys.exit(1)

    try:
        store = PhraseStore()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        phrase = store.add(ido, english)
        print(f"Saved phrase #{phrase.id}")
        print(store.format_phrase(phrase))
        print(f"\nTotal phrases: {store.count()}")
    finally:
        store.close()


if __name__ == "__main__":
    main()
