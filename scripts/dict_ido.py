#!/usr/bin/env python3
"""Look up an Ido word (root + English gloss)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.dictionary import Dictionary


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up an Ido word")
    parser.add_argument("word", nargs="?", help="Ido word (homo or hom.o)")
    parser.add_argument("--root", help="List all words with this root")
    args = parser.parse_args()

    if not args.word and not args.root:
        parser.error("provide WORD or --root")

    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        if args.root:
            entries = db.by_root(args.root)
            if not entries:
                print(f"No words found for root: {args.root}")
                sys.exit(1)
            for entry in entries:
                print(db.format_entry(entry))
                print()
            return

        entry = db.lookup_ido(args.word)
        if not entry:
            print(f"Not found: {args.word}")
            sys.exit(1)

        derived = db.list_derived(entry.word)
        print(db.format_entry(entry, derived=derived or None))
    finally:
        db.close()


if __name__ == "__main__":
    main()
