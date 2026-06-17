#!/usr/bin/env python3
"""Download Ido–English sentences from Tatoeba into a raw data file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.paths import TATOEBA_PATH
from ido.tatoeba import TATOEBA_URL, format_sentence, iter_sentences


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect Ido–English sentence pairs from Tatoeba into data/"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=TATOEBA_PATH,
        help="Output text file (default: data/tatoeba_ido_eng.txt)",
    )
    parser.add_argument(
        "-n",
        "--max",
        type=int,
        default=None,
        help="Stop after N Ido sentences (default: fetch all)",
    )
    parser.add_argument(
        "--direct-only",
        action="store_true",
        help="Include only direct English translations",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="Seconds between API pages (default: 0.3)",
    )
    parser.add_argument(
        "--url",
        default=TATOEBA_URL,
        help="Starting API URL (for resuming from paging.next)",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0

    with args.output.open("w", encoding="utf-8") as handle:
        handle.write("# Tatoeba Ido–English sentences (raw data)\n")
        handle.write(f"# source: {args.url}\n")
        handle.write("# format: ido sentence followed by eng translations\n\n")

        try:
            for sentence in iter_sentences(
                start_url=args.url,
                max_count=args.max,
                delay=args.delay,
            ):
                block = format_sentence(sentence, direct_only=args.direct_only)
                if block is None:
                    skipped += 1
                    continue
                handle.write(block)
                written += 1
                if written % 100 == 0:
                    print(f"  {written} sentences written...", file=sys.stderr)
        except KeyboardInterrupt:
            print("\nInterrupted.", file=sys.stderr)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    print(f"Done: {written} sentences → {args.output}")
    if skipped:
        print(f"  ({skipped} skipped without English translations)")


if __name__ == "__main__":
    main()
