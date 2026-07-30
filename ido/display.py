"""User-facing dictionary output (solid forms, grammar, derivations)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ido.lexer import dotted_to_solid
from ido.morphology import MorphologyAnalyzer

if TYPE_CHECKING:
    from ido.dictionary import Dictionary, WordEntry

_analyzer = MorphologyAnalyzer()
_FAMILY_LIMIT = 10


def format_word(word: str) -> str:
    """Return the solid everyday form of an Ido word."""
    return dotted_to_solid(word)


def format_grammar(entry: WordEntry) -> list[str]:
    """Return grammar lines in English for a dictionary entry."""
    analysis = _analyzer.analyze(entry.word)
    lines: list[str] = [f"  Grammar: {analysis.category}"]

    if analysis.prefixes:
        parts = []
        for prefix in analysis.prefixes:
            meaning = _analyzer.PREFIXES.get(prefix, "")
            if meaning:
                parts.append(f"-{prefix}- ({meaning})")
            else:
                parts.append(f"-{prefix}-")
        lines.append(f"  Prefixes: {', '.join(parts)}")

    if analysis.suffixes:
        parts = []
        for suffix in analysis.suffixes:
            meaning = _analyzer.SUFFIXES.get(suffix, "")
            if meaning:
                parts.append(f"-{suffix}- ({meaning})")
            else:
                parts.append(f"-{suffix}-")
        lines.append(f"  Suffixes: {', '.join(parts)}")
    else:
        lines.append("  Suffixes: —")

    if analysis.ending:
        lines.append(f"  Ending: -{analysis.ending}")

    return lines


def _format_related_line(entry: WordEntry) -> str:
    """One-line summary for derived or same-root entries."""
    solid = format_word(entry.word)
    analysis = _analyzer.analyze(entry.word)
    suffix_hint = ""
    if analysis.suffixes:
        parts = []
        for suffix in analysis.suffixes:
            meaning = _analyzer.SUFFIXES.get(suffix, "")
            if meaning:
                parts.append(f"-{suffix}- {meaning}")
            else:
                parts.append(f"-{suffix}-")
        suffix_hint = f", {', '.join(parts)}"
    category_short = analysis.category.split(" (")[0] if " (" in analysis.category else analysis.category
    return f"    {solid} — {entry.translation} ({category_short}{suffix_hint})"


def format_entry(
    db: Dictionary,
    entry: WordEntry,
    *,
    include_family: bool = True,
) -> str:
    """Format a full dictionary entry for display."""
    lines = [format_word(entry.word)]
    lines.append(f"  English: {entry.translation}")
    lines.extend(format_grammar(entry))

    if entry.root and entry.root != format_word(entry.word):
        lines.append(f"  Root: {entry.root}")

    if entry.source != "idan":
        lines.append(f"  Source: {entry.source}")
    if entry.notes:
        lines.append(f"  Notes: {entry.notes}")

    derived = db.list_derived(entry.word)
    if derived:
        lines.append("  Derived:")
        for child in derived:
            lines.append(_format_related_line(child))

    if include_family and entry.root:
        derived_words = {d.word for d in derived}
        siblings = [
            e
            for e in db.by_root(entry.root)
            if e.id != entry.id and e.word not in derived_words
        ]
        if siblings:
            lines.append("  Same root:")
            for sibling in siblings[:_FAMILY_LIMIT]:
                lines.append(_format_related_line(sibling))
            if len(siblings) > _FAMILY_LIMIT:
                lines.append(f"    … and {len(siblings) - _FAMILY_LIMIT} more")

    return "\n".join(lines)


def format_search_results(db: Dictionary, entries: list[WordEntry]) -> str:
    """Format English search results, one full entry per match."""
    blocks = [format_entry(db, entry) for entry in entries]
    return "\n\n".join(blocks)
