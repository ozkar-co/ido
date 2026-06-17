#!/usr/bin/env python3
"""Search stored Ido-English phrases."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.phrases import PhraseStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Search stored phrases")
    parser.add_argument("query", nargs="?", default="", help="Search term")
    parser.add_argument("--ido", action="store_true", help="Search Ido text only")
    parser.add_argument("--en", action="store_true", help="Search English text only")
    parser.add_argument("-n", "--limit", type=int, default=20, help="Max results")
    args = parser.parse_args()

    if args.ido and args.en:
        print("Error: use at most one of --ido or --en", file=sys.stderr)
        sys.exit(1)

    field = "both"
    if args.ido:
        field = "ido"
    elif args.en:
        field = "en"

    try:
        store = PhraseStore()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        if not args.query:
            phrases = store.list_recent(limit=args.limit)
        else:
            phrases = store.search(args.query, field=field, limit=args.limit)

        if not phrases:
            print("No phrases found.")
            sys.exit(1)

        for phrase in phrases:
            print(store.format_phrase(phrase))
            print()
    finally:
        store.close()


if __name__ == "__main__":
    main()
