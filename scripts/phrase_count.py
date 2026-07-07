#!/usr/bin/env python3
"""Show how many phrases are stored."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.db import DatabaseError, die_on_db_error
from ido.phrases import PhraseStore


def main() -> None:
    try:
        store = PhraseStore()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        print(store.count())
    finally:
        store.close()


if __name__ == "__main__":
    main()
