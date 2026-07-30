#!/usr/bin/env python3
"""Look up Ido words from an English term."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.dictionary import Dictionary
from ido.display import format_search_results


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up Ido words by English gloss")
    parser.add_argument("term", help="English word or phrase fragment")
    parser.add_argument("-n", "--limit", type=int, default=20, help="Max results")
    args = parser.parse_args()

    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        entries = db.lookup_en(args.term, limit=args.limit)
        if not entries:
            print(f"No matches for: {args.term}")
            sys.exit(1)

        print(format_search_results(db, entries))
    finally:
        db.close()


if __name__ == "__main__":
    main()
