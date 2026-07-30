"""Deterministic lexer between solid and dotted Ido word forms.

Dotted notation (idan.txt): hom.o, abad.ey.o — morpheme boundaries marked with dots.
Solid notation (everyday): homo, abadeyo — used for lookup and display.

Rules follow data/quick_gramm.txt grammatical endings; lexical suffixes are peeled
only when the remaining root stays long enough (avoids abad.o → ab.ad.o).
"""

from __future__ import annotations

from dataclasses import dataclass

from ido.morphology import MorphologyAnalyzer

# Longest match first.
GRAMMATICAL_ENDINGS = (
    "ar",
    "ir",
    "or",
    "as",
    "is",
    "os",
    "us",
    "ez",
    "o",
    "i",
    "a",
    "e",
)

MIN_ROOT_LEN = 3

_analyzer = MorphologyAnalyzer()
_LEXICAL_SUFFIXES = sorted(_analyzer.SUFFIXES.keys(), key=len, reverse=True)


@dataclass(frozen=True)
class LexedWord:
    """Result of lexing an Ido word."""

    original: str
    dotted: str
    solid: str
    root: str
    ending: str
    suffixes: tuple[str, ...]


def dotted_to_solid(dotted: str) -> str:
    """abad.o → abado, abad.ey.o → abadeyo."""
    return dotted.replace(".", "").lower().strip()


def _peel_lexical_suffixes(stem: str) -> tuple[str, list[str]]:
    """Split stem into root + suffixes (innermost to outermost)."""
    suffixes: list[str] = []
    while len(stem) > MIN_ROOT_LEN:
        matched = False
        for suffix in _LEXICAL_SUFFIXES:
            if not stem.endswith(suffix):
                continue
            candidate = stem[: -len(suffix)]
            if len(candidate) < MIN_ROOT_LEN:
                continue
            suffixes.insert(0, suffix)
            stem = candidate
            matched = True
            break
        if not matched:
            break
    return stem, suffixes


def _peel_grammatical_ending(word: str) -> tuple[str, str] | None:
    for ending in GRAMMATICAL_ENDINGS:
        if word.endswith(ending) and len(word) > len(ending) + 1:
            return word[: -len(ending)], ending
    return None


def solid_to_dotted(solid: str) -> str:
    """homo → hom.o, abadeyo → abad.ey.o (best-effort from solid form)."""
    word = solid.lower().strip()
    if "." in word:
        return word

    peeled = _peel_grammatical_ending(word)
    if peeled is None:
        return word

    stem, ending = peeled
    root, suffixes = _peel_lexical_suffixes(stem)
    parts: list[str] = [root, *suffixes, ending]
    return ".".join(parts)


def lex(word: str) -> LexedWord:
    """Analyze a word in either solid or dotted form."""
    original = word.strip()
    lowered = original.lower()

    if "." in lowered:
        dotted = lowered
        solid = dotted_to_solid(dotted)
        analysis = _analyzer.analyze(dotted)
    else:
        solid = lowered
        dotted = solid_to_dotted(solid)
        analysis = _analyzer.analyze(dotted)

    return LexedWord(
        original=original,
        dotted=dotted,
        solid=solid,
        root=analysis.root,
        ending=analysis.ending,
        suffixes=tuple(analysis.suffixes),
    )


def query_variants(query: str) -> list[str]:
    """Return lookup keys to try (deduplicated, order preserved)."""
    q = query.strip().lower()
    if not q:
        return []

    variants: list[str] = [q]
    if "." in q:
        solid = dotted_to_solid(q)
        if solid not in variants:
            variants.append(solid)
    else:
        dotted = solid_to_dotted(q)
        if dotted != q and dotted not in variants:
            variants.append(dotted)

    return variants
