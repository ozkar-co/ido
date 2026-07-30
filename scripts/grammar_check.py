#!/usr/bin/env python3
"""Validate and analyze an Ido sentence."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ido.syntax import analyze, format_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and analyze an Ido sentence")
    parser.add_argument("sentence", nargs="?", help="Ido sentence to analyze")
    parser.add_argument("--tree", action="store_true", help="Show parse tree")
    args = parser.parse_args()

    sentence = args.sentence
    if not sentence:
        sentence = input("Ido sentence: ").strip()

    if not sentence:
        print("Error: sentence required", file=sys.stderr)
        sys.exit(1)

    result = analyze(sentence)
    print(format_analysis(result, show_tree=args.tree))
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
