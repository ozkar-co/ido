"""Salida legible del diccionario y de las consultas."""

from __future__ import annotations

from dictionary import Dictionary, Lookup, WordEntry
from morphology import MorphologicalAnalysis, MorphologyAnalyzer

_ANALYZER = MorphologyAnalyzer()
_FAMILY_LIMIT = 8


def _pos_label(entry: WordEntry) -> str:
    labels = {
        "noun": "sustantivo",
        "verb": "verbo",
        "adj": "adjetivo",
        "adv": "adverbio",
        "participle": "participio",
        "affix": "afijo",
        "phrase": "expresión",
        "interj": "interjección",
        "prep": "preposición",
        "conj": "conjunción",
        "pron": "pronombre",
        "num": "número",
        "other": "otro",
    }
    label = labels.get(entry.pos, entry.pos)
    if entry.transitivity:
        label += f", {entry.transitivity}"
    if entry.proper:
        label += ", nombre propio"
    return label


def _analysis_for(entry: WordEntry) -> MorphologicalAnalysis:
    return _ANALYZER.analyze(entry.segments or entry.lemma)


def _category_es(analysis: MorphologicalAnalysis) -> str:
    category = analysis.category
    translations = {
        "VERB (infinitive)": "verbo, infinitivo",
        "VERB (present)": "verbo, presente",
        "VERB (past)": "verbo, pasado",
        "VERB (future)": "verbo, futuro",
        "VERB (conditional)": "verbo, condicional",
        "VERB (imperative)": "verbo, imperativo",
        "NOUN (singular)": "sustantivo singular",
        "NOUN (plural)": "sustantivo plural",
        "ADJECTIVE": "adjetivo",
        "ADVERB": "adverbio",
        "PARTICIPLE (adjective form)": "participio en función adjetiva",
        "PARTICIPLE (adverb form)": "participio en función adverbial",
    }
    return translations.get(category, category)


def format_word(word: str) -> str:
    """La forma visible es siempre la sólida."""
    return word


def format_morphology(entry: WordEntry, *, show_segments: bool = False) -> list[str]:
    """Líneas de morfología y, opcionalmente, segmentación punteada."""
    if entry.pos == "phrase":
        return ["  Categoría: expresión multi-palabra"]
    if entry.pos == "interj":
        return ["  Categoría: interjección"]
    analysis = _analysis_for(entry)
    lines = [f"  Categoría: {_category_es(analysis)}"]

    if show_segments and entry.segments and "." in entry.segments:
        lines.append(f"  Segmentación: {entry.segments}")
    if analysis.prefixes:
        parts = [f"-{prefix}- ({_ANALYZER.PREFIXES.get(prefix, '')})" for prefix in analysis.prefixes]
        lines.append(f"  Prefijos: {', '.join(parts)}")
    if analysis.suffixes:
        parts = []
        for suffix in analysis.suffixes:
            meaning = _ANALYZER.SUFFIXES.get(suffix, "")
            parts.append(f"-{suffix}- ({meaning})" if meaning else f"-{suffix}-")
        lines.append(f"  Sufijos: {', '.join(parts)}")
    if analysis.root:
        lines.append(f"  Raíz: {analysis.root}")
    if analysis.ending:
        lines.append(f"  Terminación: -{analysis.ending}")
    return lines


def _related_line(entry: WordEntry) -> str:
    if entry.pos == "phrase":
        return f"    {entry.lemma} — {entry.translation} (expresión)"
    if entry.pos == "interj":
        return f"    {entry.lemma} — {entry.translation} (interjección)"
    analysis = _analysis_for(entry)
    note = _category_es(analysis)
    if entry.pos == "verb" and entry.transitivity:
        note += f", {entry.transitivity}"
    return f"    {entry.lemma} — {entry.translation} ({note})"


def format_entry(
    db: Dictionary,
    entry: WordEntry,
    *,
    include_family: bool = True,
    show_segments: bool = False,
) -> str:
    """Formatea una entrada completa."""
    lines = [format_word(entry.lemma)]
    lines.append(f"  English: {entry.translation}")
    lines.append(f"  Grammar: {_pos_label(entry)}")
    lines.extend(format_morphology(entry, show_segments=show_segments))

    derived = db.list_derived(entry.lemma)
    if derived:
        lines.append("  Derivadas:")
        for child in derived[:_FAMILY_LIMIT]:
            lines.append(_related_line(child))

    if include_family and entry.root:
        derived_words = {child.id for child in derived}
        siblings = [
            item
            for item in db.by_root(entry.root)
            if item.id != entry.id and item.id not in derived_words
        ]
        if siblings:
            lines.append("  Misma raíz:")
            for sibling in siblings[:_FAMILY_LIMIT]:
                lines.append(_related_line(sibling))
            if len(siblings) > _FAMILY_LIMIT:
                lines.append(f"    … y {len(siblings) - _FAMILY_LIMIT} más")

    if entry.source != "idan":
        lines.append(f"  Fuente: {entry.source}")
    if entry.notes:
        lines.append(f"  Notas: {entry.notes}")
    return "\n".join(lines)


def format_lookup(
    db: Dictionary,
    result: Lookup,
    *,
    include_family: bool = True,
    show_segments: bool = False,
) -> str:
    """Entrada más una nota si la consulta era una forma conjugada."""
    text = format_entry(
        db, result.entry, include_family=include_family, show_segments=show_segments
    )
    if result.note:
        text = f"{text}\n  Consulta: {result.query} → {result.note}"
    elif result.entry.lemma.lower() != result.query.strip().lower():
        text = f"{text}\n  Consulta: {result.query} → {result.entry.lemma}"
    return text


def format_search_results(
    db: Dictionary, entries: list[WordEntry], *, show_segments: bool = False
) -> str:
    """Resultados compactos de inglés → Ido."""
    if not entries:
        return ""
    blocks = [
        format_entry(db, entry, include_family=False, show_segments=show_segments)
        for entry in entries
    ]
    return "\n\n".join(blocks)


def format_search_compact(entries: list[WordEntry]) -> str:
    """Una línea por resultado; útil para listas largas."""
    lines = []
    for entry in entries:
        label = _pos_label(entry)
        lines.append(f"{entry.lemma:20} {entry.translation} ({label})")
    return "\n".join(lines)
