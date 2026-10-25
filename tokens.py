"""Tokenización y etiquetado de Ido para el analizador sintáctico.

El léxico manda: primero se consulta la base, después la morfología regular y
solo al final se aplican heurísticas. Así ``kato`` es sustantivo y ``manjas``
es una forma de ``manjar``.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from functools import lru_cache

from db import DatabaseError, connect
from morphology import MorphologicalAnalysis, MorphologyAnalyzer
from paths import DB_PATH

_ANALYZER = MorphologyAnalyzer()

PRONOUNS = {
    "me", "tu", "vu", "il", "ilu", "el", "elu", "ol", "olu", "lu",
    "ni", "vi", "li", "ili", "eli", "oli", "on", "onu", "su",
    "to", "ito", "co", "ico", "ta", "ita", "lo", "ulu",
}
POSSESSIVES = {
    "mea", "tua", "vua", "ilua", "elua", "olua", "lua", "nia", "via",
    "ilia", "elia", "olia", "onua", "sua",
}
DETERMINERS = {"la", "le", "ua", "l'"}
COPULAS = {"esar", "esas", "esis", "esos", "esus", "esez", "es"}
QUESTION_PARTS = {
    "qua", "qui", "quo", "quan", "quon", "quantan", "qualan", "quin",
    "ube", "kande", "quale", "quanta", "quala", "pro quo",
}
PREPOSITIONS = {
    "de", "di", "en", "kun", "por", "pro", "al", "a", "pri", "sur", "sub",
    "inter", "ante", "post", "til", "dum", "sin", "per", "ad", "dil", "dal",
    "tra", "trans", "kontre", "apud", "cis", "ultra", "ye", "sen", "koncerne",
    "malgre", "segun", "proxim", "proche", "ek", "for", "de", "til",
    "pos", "depos", "ecepte", "plus", "kom", "del", "da",
}
CONJUNCTIONS = {
    "kaj", "e", "ed", "sed", "ma", "od", "o", "nam", "sive", "quankam", "kam",
}
NEGATIONS = {"ne", "no"}
NUMERALS = {
    "un", "du", "tri", "quar", "kin", "sis", "sep", "ok", "non", "dek",
    "cent", "mil", "miliono", "biliono", "triliono",
}
PARTICLES = {
    "ja", "plu", "min", "maxim", "minim", "tam", "sempre", "nur",
    "ankore", "tre", "multe", "poko", "foye", "mem", "ton", "yes",
    "yen", "hura", "do",
}
KE_MARKERS = {"ke", "por ke", "pro ke", "pos ke", "dum ke"}
SE_MARKERS = {"se", "si"}

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]+(?:[-'][A-Za-zÀ-ÿ]+)*")
NUM_RE = re.compile(r"^\d+(?:[.,]\d+)?(?::\d+)?(?:[a-z]{1,3})?$", re.IGNORECASE)
NUM_SCAN_RE = re.compile(r"\d+(?:[.,]\d+)?(?::\d+)?(?:[a-z]{1,3})?", re.IGNORECASE)
NUMBER_WORD_RE = re.compile(
    r"^(?:un|du|tri|quar|kin|sis|sep|ok|non|dek|cent|mil|milion|bilion)"
    r"(?:adek|acent|amil|esm|im|op|opl)?$",
    re.IGNORECASE,
)
ADVERB_WORDS = {
    "nun", "ibe", "hike", "hodie", "morge", "hiere", "olim", "ore",
    "nultempe", "tamen", "forsan", "sendube", "uladie", "omnadie",
    "recente", "jus", "nu", "anke", "samatempe", "tro", "probable", "cirkum", "sat",
}
ACCUSATIVE_RE = re.compile(r"^(.+?)n$", re.IGNORECASE)
PARTICIPLE_RE = re.compile(r"^(.+?)(ant|int|ont|at|it|ot)([aeoi])$", re.IGNORECASE)
PERFECT_RE = re.compile(r"^(.+?)(abas|abis|abos|abus)$", re.IGNORECASE)


@dataclass(frozen=True)
class ClassifiedToken:
    """Una palabra o signo con su categoría, lema y rasgos."""

    type: str
    value: str
    note: str
    lemma: str = ""
    form: str | None = None
    features: tuple[str, ...] = ()
    known: bool = True
    position: int = 0


@dataclass(frozen=True)
class Lexicon:
    by_lemma: dict[str, tuple[str, ...]]
    by_root: dict[str, tuple[str, ...]]
    proper: frozenset[str]


@lru_cache(maxsize=1)
def load_lexicon(db_path: str = str(DB_PATH)) -> Lexicon:
    """Carga el léxico en memoria una vez por proceso."""
    by_lemma: dict[str, set[str]] = {}
    by_root: dict[str, set[str]] = {}
    proper: set[str] = set()
    try:
        conn = connect(db_path)
    except DatabaseError:
        return Lexicon({}, {}, frozenset())
    try:
        for row in conn.execute("SELECT lemma, root, pos, proper FROM words"):
            lemma = row["lemma"].lower()
            pos = row["pos"]
            if pos == "affix":
                continue
            by_lemma.setdefault(lemma, set()).add(pos)
            if row["proper"]:
                proper.add(lemma)
            if row["root"]:
                by_root.setdefault(row["root"].lower(), set()).add(pos)
    finally:
        conn.close()
    return Lexicon(
        {key: tuple(sorted(value)) for key, value in by_lemma.items()},
        {key: tuple(sorted(value)) for key, value in by_root.items()},
        frozenset(proper),
    )


def reset_lexicon() -> None:
    """Olvida el léxico cacheado (útil después de importar o en tests)."""
    load_lexicon.cache_clear()


def _pick_pos(types: tuple[str, ...], lower: str) -> str:
    """Elige la categoría más probable para un lema del diccionario."""
    if "verb" in types:
        if lower.endswith(("ar", "ir", "or", "as", "is", "os", "us", "ez")):
            return "verb"
    for preferred in ("noun", "adj", "adv", "participle", "other"):
        if preferred in types:
            return preferred
    return types[0] if types else "other"


def _note_for_pos(pos: str, analysis: MorphologicalAnalysis | None = None) -> str:
    if pos == "noun":
        return "SUSTANTIVO"
    if pos == "verb":
        return _ANALYZER and (analysis.category if analysis else "VERBO")
    if pos == "adj":
        return "ADJETIVO"
    if pos == "adv":
        return "ADVERBIO"
    if pos == "participle":
        return "PARTICIPIO"
    return pos.upper()


def _tag_lexicon_word(lower: str, raw: str, position: int) -> ClassifiedToken | None:
    lex = load_lexicon()
    types = lex.by_lemma.get(lower)
    if not types:
        return None
    pos = _pick_pos(types, lower)
    analysis = _ANALYZER.analyze(lower)
    if pos == "verb":
        if lower.endswith("ez"):
            token_type, form, features = "VIMP", "imperative", ("imperative",)
        elif lower.endswith(("ar", "ir", "or")):
            token_type, form, features = "VINF", "infinitive", ("infinitive",)
        elif PARTICIPLE_RE.match(lower):
            token_type, form, features = "VPART", "participle", ("participle",)
        else:
            token_type, form = "VFIN", "finite"
            tense = {"as": "present", "is": "past", "os": "future", "us": "conditional"}
            features = (tense.get(lower[-2:], "finite"),)
            if "ab" in lower[-5:]:
                features += ("perfect",)
        return ClassifiedToken(
            token_type, raw, f"VERBO ({form})", lemma=lower, form=form,
            features=features, known=True, position=position,
        )
    if pos == "noun":
        plural = lower.endswith("i")
        return ClassifiedToken(
            "NOUN", raw, "SUSTANTIVO (plural)" if plural else "SUSTANTIVO",
            lemma=lower, form="plural" if plural else "singular",
            features=("plural",) if plural else ("singular",),
            known=True, position=position,
        )
    if pos == "adj":
        return ClassifiedToken("ADJ", raw, "ADJETIVO", lemma=lower, known=True, position=position)
    if pos == "adv":
        return ClassifiedToken("ADV", raw, "ADVERBIO", lemma=lower, known=True, position=position)
    if pos == "participle":
        return ClassifiedToken("VPART", raw, "PARTICIPIO", lemma=lower, form="participle", known=True, position=position)
    if pos == "interj":
        return ClassifiedToken("PART", raw, "INTERJECCIÓN", lemma=lower, known=True, position=position)
    return ClassifiedToken("OTHER", raw, "OTRO", lemma=lower, known=True, position=position)


def _tag_verb_form(lower: str, raw: str, position: int) -> ClassifiedToken | None:
    lex = load_lexicon()

    def known_verb(root: str) -> str | None:
        roots = [root]
        # Un participio puede llevar sufijos antes del infijo: mort.ig.it.a.
        for suffix in ("ig", "es", "ad", "iz", "if", "esk", "ar", "er", "et", "eg"):
            if root.endswith(suffix) and len(root) > len(suffix) + 2:
                roots.append(root[: -len(suffix)])
        for candidate_root in roots:
            for ending in ("ar", "ir", "or"):
                candidate = candidate_root + ending
                if candidate in lex.by_lemma:
                    return candidate
        return None

    perfect = PERFECT_RE.match(lower)
    if perfect:
        lemma = known_verb(perfect.group(1))
        if lemma:
            return ClassifiedToken(
                "VFIN", raw, "VERBO (perfecto)", lemma=lemma, form="finite",
                features=("perfect",), known=True, position=position,
            )

    if lower.endswith(("as", "is", "os", "us")):
        lemma = known_verb(lower[:-2])
        if lemma:
            tense = {"as": "present", "is": "past", "os": "future", "us": "conditional"}[lower[-2:]]
            return ClassifiedToken(
                "VFIN", raw, f"VERBO ({tense})", lemma=lemma, form="finite",
                features=(tense,), known=True, position=position,
            )
    if lower.endswith("ez"):
        lemma = known_verb(lower[:-2])
        if lemma:
            return ClassifiedToken(
                "VIMP", raw, "VERBO (imperativo)", lemma=lemma, form="imperative",
                features=("imperative",), known=True, position=position,
            )
    if lower.endswith(("ar", "ir", "or")):
        if lower in lex.by_lemma:
            return ClassifiedToken(
                "VINF", raw, "VERBO (infinitivo)", lemma=lower, form="infinitive",
                features=("infinitive",), known=True, position=position,
            )

    participle = PARTICIPLE_RE.match(lower)
    if participle:
        lemma = known_verb(participle.group(1))
        if lemma:
            return ClassifiedToken(
                "VPART", raw, "PARTICIPIO", lemma=lemma, form="participle",
                features=("participle",), known=True, position=position,
            )
    return None


def _tag_accusative_or_plural(lower: str, raw: str, position: int) -> ClassifiedToken | None:
    lex = load_lexicon()
    base = lower
    case = None
    if lower.endswith("n") and len(lower) > 2:
        base = lower[:-1]
        case = "accusative"
    if base.endswith("i") and len(base) > 2:
        singular = base[:-1] + "o"
        if singular in lex.by_lemma:
            return ClassifiedToken(
                "NOUN", raw, "SUSTANTIVO (plural acusativo)" if case else "SUSTANTIVO (plural)",
                lemma=singular, form="plural", features=("plural",) + (("accusative",) if case else ()),
                known=True, position=position,
            )
    if base in lex.by_lemma:
        pos = _pick_pos(lex.by_lemma[base], base)
        if pos == "noun":
            return ClassifiedToken(
                "NOUN", raw, "SUSTANTIVO (acusativo)" if case else "SUSTANTIVO",
                lemma=base, form="singular", features=(("accusative",) if case else ("singular",)),
                known=True, position=position,
            )
    return None


def _tag_morphology(lower: str, raw: str, position: int) -> ClassifiedToken | None:
    analysis = _ANALYZER.analyze(lower)
    category = analysis.category
    known = analysis.root in load_lexicon().by_root
    if category.startswith("NOUN"):
        return ClassifiedToken("NOUN", raw, category, lemma=analysis.root, known=known, position=position)
    if category.startswith("ADJECTIVE"):
        return ClassifiedToken("ADJ", raw, category, lemma=analysis.root, known=known, position=position)
    if category.startswith("ADVERB"):
        return ClassifiedToken("ADV", raw, category, lemma=analysis.root, known=known, position=position)
    if category.startswith("VERB"):
        if "infinitive" in category:
            token_type = "VINF"
        elif "imperative" in category:
            token_type = "VIMP"
        else:
            token_type = "VFIN"
        return ClassifiedToken(token_type, raw, category, lemma=analysis.root, known=known, position=position)
    if category.startswith("PARTICIPLE"):
        return ClassifiedToken("VPART", raw, category, lemma=analysis.root, known=known, position=position)
    return None


def _tag_word(raw: str, position: int, *, first: bool = False) -> ClassifiedToken:
    lower = raw.lower().replace("’", "'")
    if lower in {"ka", "kad"}:
        return ClassifiedToken("KAD", raw, "PARTÍCULA INTERROGATIVA", known=True, position=position)
    if lower in QUESTION_PARTS:
        return ClassifiedToken("QU", raw, "INTERROGATIVO/RELATIVO", lemma=lower, known=True, position=position)
    if lower in KE_MARKERS:
        return ClassifiedToken("KE", raw, "SUBORDINADOR", lemma=lower, known=True, position=position)
    if lower in SE_MARKERS:
        return ClassifiedToken("SE", raw, "CONDICIONAL", lemma=lower, known=True, position=position)
    if lower in COPULAS:
        note = "CÓPULA (variante no estándar)" if lower == "es" else "CÓPULA"
        return ClassifiedToken("COP", raw, note, lemma="esar", form="finite", known=lower != "es", position=position)
    if lower in DETERMINERS:
        return ClassifiedToken("DET", raw, "DETERMINANTE", known=True, position=position)
    if lower in POSSESSIVES:
        return ClassifiedToken("POSS", raw, "POSESIVO", known=True, position=position)
    if lower in PRONOUNS:
        return ClassifiedToken("PRON", raw, "PRONOMBRE", known=True, position=position)
    if lower in PREPOSITIONS:
        return ClassifiedToken("PREP", raw, "PREPOSICIÓN", known=True, position=position)
    if lower in CONJUNCTIONS:
        return ClassifiedToken("CONJ", raw, "CONJUNCIÓN", known=True, position=position)
    if lower in NEGATIONS:
        return ClassifiedToken("NEG", raw, "NEGACIÓN", known=True, position=position)
    if lower in PARTICLES:
        return ClassifiedToken("PART", raw, "PARTÍCULA", known=True, position=position)
    if lower in ADVERB_WORDS:
        return ClassifiedToken("ADV", raw, "ADVERBIO", known=True, position=position)

    if NUM_RE.match(raw) or lower in NUMERALS or NUMBER_WORD_RE.match(lower):
        return ClassifiedToken("NUM", raw, "NÚMERO", known=True, position=position)

    if "-" in lower:
        # Los compuestos se buscan también sin guion: sen-kulpa -> senkulpa.
        solid = lower.replace("-", "")
        if solid in load_lexicon().by_lemma:
            inner = _tag_lexicon_word(solid, raw, position)
            if inner:
                return ClassifiedToken(
                    inner.type, raw, f"COMPUESTO ({inner.note})", lemma=solid,
                    form=inner.form, features=inner.features, known=True,
                    position=position,
                )
        last = lower.rsplit("-", 1)[-1]
        inner = _tag_word(last, position)
        if inner.type in {"NOUN", "ADJ", "ADV", "VINF", "VFIN", "VPART"}:
            return ClassifiedToken(
                inner.type, raw, f"COMPUESTO ({inner.note})", lemma=lower,
                form=inner.form, features=inner.features, known=False,
                position=position,
            )

    tagged = _tag_lexicon_word(lower, raw, position)
    if tagged:
        return tagged
    tagged = _tag_verb_form(lower, raw, position)
    if tagged:
        return tagged
    tagged = _tag_accusative_or_plural(lower, raw, position)
    if tagged:
        return tagged

    # Un verbo conjugado capitalizado (Retrodonez) no es un nombre propio.
    if raw[:1].isupper() and lower.endswith(("ez", "as", "is", "os", "us")):
        tagged = _tag_morphology(lower, raw, position)
        if tagged and tagged.type in {"VFIN", "VIMP"}:
            return tagged

    # Al inicio de frase, una palabra capitalizada desconocida puede ser un
    # adverbio (Sendube), un sustantivo (Belegeso) o un nombre propio (Maria).
    if raw[:1].isupper() and lower not in load_lexicon().by_lemma:
        if lower.endswith("e"):
            tagged = _tag_morphology(lower, raw, position)
            if tagged and tagged.type == "ADV":
                return tagged
        if lower.endswith(("o", "i")):
            tagged = _tag_morphology(lower, raw, position)
            if tagged and tagged.type == "NOUN":
                return tagged
        return ClassifiedToken("NAME", raw, "NOMBRE PROPIO", known=False, position=position)

    tagged = _tag_morphology(lower, raw, position)
    if tagged:
        return tagged

    return ClassifiedToken("OTHER", raw, "DESCONOCIDO", lemma=lower, known=False, position=position)


def classify_word(word: str) -> tuple[str, str]:
    """Compatibilidad: devuelve (tipo, nota) para una palabra suelta."""
    token = _tag_word(word, 0, first=True)
    return token.type, token.note


def _split_items(text: str) -> list[str | tuple[str, str]]:
    """Separa palabras, números, compuestos y signos de puntuación."""
    items: list[str | tuple[str, str]] = []
    i = 0
    length = len(text)
    while i < length:
        char = text[i]
        if char.isspace():
            i += 1
            continue
        if char in ",;:":
            kind = {",": "PUNCT_COMMA", ";": "PUNCT_SEMI", ":": "PUNCT_COLON"}[char]
            items.append((kind, char))
            i += 1
            continue
        if char in "?!.":
            kind = {"?": "PUNCT_Q", "!": "PUNCT_EX", ".": "PUNCT_DOT"}[char]
            items.append((kind, char))
            i += 1
            continue
        if char in "\"'“”«»":
            items.append(("QUOTE", char))
            i += 1
            continue
        if char in "—–":
            items.append(("PUNCT_SEMI", char))
            i += 1
            continue
        if char in "()[]{}":
            i += 1
            continue

        # l'Angla se separa en determinante + palabra.
        if text[i : i + 2].lower() == "l'":
            items.append(("DET", "l'"))
            i += 2
            continue

        match = WORD_RE.match(text, i)
        if match:
            word = match.group(0)
            # Expresiones de dos palabras que funcionan como una unidad.
            tail = text[match.end() :].lstrip()
            if word.lower() in {"pro", "por", "pos"}:
                second = WORD_RE.match(tail)
                if second:
                    pair = f"{word.lower()} {second.group(0).lower()}"
                    if pair in QUESTION_PARTS or pair in KE_MARKERS:
                        items.append(("QU" if pair in QUESTION_PARTS else "KE", pair))
                        i = match.end() + (len(text[match.end() :]) - len(tail)) + second.end()
                        continue
            items.append(word)
            i = match.end()
            continue

        match = NUM_SCAN_RE.match(text, i)
        if match:
            items.append(match.group(0))
            i = match.end()
            continue
        i += 1
    return items


def split_sentences(text: str) -> list[str]:
    """Divide en oraciones; las comillas se ignoran en el análisis."""
    text = text.strip()
    if not text:
        return []
    sentences: list[str] = []
    start = 0
    for index, char in enumerate(text):
        if char not in ".?!":
            continue
        following = text[index + 1 :].lstrip()
        if not following or following[:1].isupper() or following[:1] in "\"“«":
            sentence = re.sub(r'^[\s"“”«»,;:]+|[\s"“”«»,;:]+$', '', text[start : index + 1])
            if sentence:
                sentences.append(sentence)
            start = index + 1
    tail = re.sub(r'^[\s"“”«»,;:]+|[\s"“”«»,;:]+$', '', text[start:])
    if tail:
        sentences.append(tail)
    return [sentence for sentence in sentences if sentence]


def tokenize_sentence(text: str) -> list[ClassifiedToken]:
    """Tokeniza una frase completa, incluyendo la puntuación final."""
    items = _split_items(text)
    tokens: list[ClassifiedToken] = []
    for index, item in enumerate(items):
        if isinstance(item, tuple):
            token_type, value = item
            tokens.append(ClassifiedToken(token_type, value, token_type, position=index))
            continue
        tokens.append(_tag_word(item, index, first=not tokens))
    return tokens
