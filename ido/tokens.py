"""Tokenize and classify Ido sentence words for syntax parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ido.morphology import MorphologyAnalyzer

_analyzer = MorphologyAnalyzer()

PRONOUNS = {
    "me", "tu", "vu", "il", "ilu", "el", "elu", "ol", "olu", "lu",
    "ni", "vi", "li", "ili", "eli", "oli", "on", "onu", "su",
    "to", "ito", "co", "ico", "ta", "ita",
}

POSSESSIVES = {
    "mea", "tua", "vua", "ilua", "elua", "olua", "lua", "nia", "via",
    "ilia", "elia", "olia", "onua", "sua",
}

DETERMINERS = {"la", "le", "un", "ua", "l'"}

QUESTION_PARTS = {"ka", "kad", "qua", "quo", "qui", "ube", "kande", "quale", "quanta", "quala"}

PARTICLES = {
    "ja", "plu", "min", "maxim", "minim", "tam", "kam",
    "sempre", "nur", "ankore", "tre", "multe", "poko", "foye", "mem",
    "ton", "lo", "yes", "no",
}

PREPOSITIONS = {
    "de", "di", "en", "kun", "por", "pro", "al", "a", "pri", "sur", "sub",
    "inter", "antee", "post", "til", "dum", "sin", "per", "ad", "dil", "dal",
}

COPULAS = {
    "esas", "esis", "esos", "esus", "esez", "esar", "esir", "esor",
    "esus", "esez",
}

CONJUNCTIONS = {"kaj", "sed", "ma", "od", "o", "nam"}

WORD_RE = re.compile(r"[a-zA-Z']+")
VERB_RE = re.compile(
    r"^[a-z']+(?:"
    r"ab(?:as|is|os|us|ez)|"
    r"(?:ant|int|ont|at|it|ot)(?:a|e|o|i|as|is|os|us|ar|ir|or)?|"
    r"ar|ir|or|as|is|os|us|ez"
    r")$",
    re.IGNORECASE,
)
NOUN_RE = re.compile(r"^[a-z']+[oi]$", re.IGNORECASE)
ADJ_RE = re.compile(r"^[a-z']+a$", re.IGNORECASE)
ADV_RE = re.compile(r"^[a-z']+e$", re.IGNORECASE)


@dataclass(frozen=True)
class ClassifiedToken:
    type: str
    value: str
    note: str


def _normalize_apostrophe(word: str) -> str:
    if word.startswith("l'") or word.startswith("L'"):
        return "l'" + word[2:]
    return word


def classify_word(word: str) -> tuple[str, str]:
    """Return (token_type, grammar_note) for one word."""
    raw = word
    word = _normalize_apostrophe(word)
    lower = word.lower()

    if lower in PRONOUNS:
        return "PRON", "PRONOUN"
    if lower in POSSESSIVES:
        return "POSS", "POSSESSIVE"
    if lower in DETERMINERS or lower == "l'":
        return "DET", "DETERMINER"
    if lower in COPULAS:
        tense = "present" if lower.endswith("as") else "past" if lower.endswith("is") else "future" if lower.endswith("os") else "copula"
        return "COPULA", f"COPULA ({tense})"
    if lower in PREPOSITIONS:
        return "PREP", "PREPOSITION"
    if lower in CONJUNCTIONS:
        return "CONJ", "CONJUNCTION"
    if lower in QUESTION_PARTS:
        return "QU", "INTERROGATIVE"
    if lower == "ke":
        return "KE", "SUBORDINATOR"
    if lower in {"ka", "kad"}:
        return "KAD", "YES/NO PARTICLE"
    if lower == "ne":
        return "NEG", "NEGATION"
    if lower in PARTICLES:
        return "PART", "PARTICLE"
    if lower == "pro quo":
        return "QU", "INTERROGATIVE (why)"

    if VERB_RE.match(lower):
        analysis = _analyzer.analyze(lower)
        return "VERB", analysis.category
    if ADJ_RE.match(lower):
        return "ADJ", "ADJECTIVE"
    if ADV_RE.match(lower):
        return "ADV", "ADVERB"
    if NOUN_RE.match(lower):
        analysis = _analyzer.analyze(lower)
        return "NOUN", analysis.category

    if raw[0].isupper():
        return "NAME", "PROPER NOUN"

    return "OTHER", "UNKNOWN"


def split_sentence(text: str) -> tuple[list[str | tuple[str, str]], str | None]:
    """Split text into word/punctuation items and trailing sentence mood marker."""
    text = text.strip()
    if not text:
        return [], None

    mood: str | None = None
    if text.endswith("?"):
        mood = "interrogative"
        text = text[:-1].strip()
    elif text.endswith("."):
        mood = "declarative"
        text = text[:-1].strip()
    elif text.endswith("!"):
        mood = "exclamative"
        text = text[:-1].strip()

    items: list[str | tuple[str, str]] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in ",;:":
            punct_type = {",": "PUNCT_COMMA", ";": "PUNCT_SEMI", ":": "PUNCT_COLON"}.get(
                ch, f"PUNCT_{ch}"
            )
            items.append((punct_type, ch))
            i += 1
            continue
        if ch in "\"'":
            items.append(("QUOTE", ch))
            i += 1
            continue
        match = WORD_RE.match(text, i)
        if match:
            word = match.group(0)
            if word.lower() == "pro" and i + 4 <= len(text) and text[i + 4 : i + 8].lower() == " quo":
                items.append(("QU", "pro quo"))
                i += 8
                continue
            items.append(word)
            i = match.end()
            continue
        i += 1

    return items, mood


def tokenize_sentence(text: str) -> list[ClassifiedToken]:
    """Tokenize and classify an Ido sentence."""
    items, mood = split_sentence(text)
    tokens: list[ClassifiedToken] = []
    for item in items:
        if isinstance(item, tuple):
            tok_type, value = item
            tokens.append(ClassifiedToken(tok_type, value, tok_type))
            continue
        tok_type, note = classify_word(item)
        tokens.append(ClassifiedToken(tok_type, item, note))

    if mood == "interrogative":
        tokens.append(ClassifiedToken("PUNCT_Q", "?", "INTERROGATIVE"))
    elif mood == "declarative":
        tokens.append(ClassifiedToken("PUNCT_DOT", ".", "DECLARATIVE"))
    elif mood == "exclamative":
        tokens.append(ClassifiedToken("PUNCT_EX", "!", "EXCLAMATIVE"))
    return tokens
