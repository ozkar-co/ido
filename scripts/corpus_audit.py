#!/usr/bin/env python3
"""Audit Tatoeba sentences against the Ido syntax parser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.corpus import iter_tatoeba
from ido.paths import AUDIT_FAILURES_PATH, TATOEBA_PATH
from ido.syntax import analyze


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Tatoeba corpus against syntax parser")
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=TATOEBA_PATH,
        help="Tatoeba snapshot file",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=None,
        help="Process only first N sentences",
    )
    parser.add_argument(
        "--failures",
        action="store_true",
        help="Write failures to output file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=AUDIT_FAILURES_PATH,
        help="Failure report path",
    )
    args = parser.parse_args()

    total = 0
    parsed = 0
    failures: list[str] = []

    for entry in iter_tatoeba(args.input):
        total += 1
        result = analyze(entry.ido)
        if result.valid:
            parsed += 1
        else:
            failures.append(
                f"{entry.id} | {entry.ido}\n         | {result.error or 'unknown error'}"
            )
        if args.limit is not None and total >= args.limit:
            break

    failed = total - parsed
    pct = (parsed / total * 100) if total else 0.0
    print(f"Total:     {total}")
    print(f"Parsed:    {parsed}  ({pct:.1f}%)")
    print(f"Failed:    {failed}  ({100 - pct:.1f}%)")

    if args.failures and failures:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n\n".join(failures) + "\n", encoding="utf-8")
        print(f"Failures written to {args.output}")


if __name__ == "__main__":
    main()
