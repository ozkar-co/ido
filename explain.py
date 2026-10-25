"""Explicación gramatical procedural a partir del árbol y la morfología."""

from __future__ import annotations

from dictionary import Dictionary
from morphology import MorphologyAnalyzer
from syntax import Constituent, ParseResult

_ANALYZER = MorphologyAnalyzer()

_MOOD_ES = {
    "declarative": "declarativa",
    "interrogative": "interrogativa",
    "exclamative": "exclamativa",
}

_ROLE_ES = {
    "Sujeto": "Sujeto",
    "Predicado": "Predicado",
    "Complemento": "Complemento",
    "Atributo": "Atributo",
    "Participio": "Participio",
    "Infinitivo": "Infinitivo",
    "Complemento preposicional": "Complemento preposicional",
    "Complemento circunstancial": "Complemento circunstancial",
    "Subordinada": "Subordinada",
    "Vocativo": "Vocativo",
    "Marcador interrogativo": "Marcador interrogativo",
    "Interjección": "Interjección",
    "Grupo nominal": "Grupo nominal",
}


def _morphology_line(token, db: Dictionary) -> str | None:
    if token.type in {"PUNCT_DOT", "PUNCT_Q", "PUNCT_EX", "PUNCT_COMMA", "PUNCT_SEMI", "PUNCT_COLON"}:
        return None
    if token.type in {"PRON", "POSS", "DET", "PREP", "CONJ", "KE", "SE", "QU", "KAD", "NEG", "PART"}:
        return f"    {token.value}: {token.note.lower()}"
    if token.type == "NAME":
        return f"    {token.value}: nombre propio"
    if token.type == "NUM":
        return f"    {token.value}: número"
    if token.type in {"VFIN", "VINF", "VPART", "VIMP", "COP", "NOUN", "ADJ", "ADV"}:
        lookup = db.find(token.lemma or token.value)
        entry = lookup.entry if lookup and lookup.entry.lemma.lower() == (token.lemma or token.value).lower() else None
        source = entry.segments if entry and entry.segments else token.value.lower()
        analysis = _ANALYZER.analyze(source)
        surface = _ANALYZER.analyze(token.value.lower())
        parts: list[str] = []
        if analysis.prefixes:
            parts.append("prefijo " + "-".join(analysis.prefixes))
        root = (entry.root if entry and entry.root else analysis.root)
        if root:
            parts.append(f"raíz {root}-")
        if analysis.suffixes:
            parts.append("sufijo " + "-".join(analysis.suffixes))
        ending = surface.ending if surface.ending else analysis.ending
        if ending:
            parts.append(f"terminación -{ending}")
        detail = ", ".join(parts) if parts else analysis.category.lower()
        features = [feature for feature in token.features if feature != "singular"]
        if features:
            detail += f" ({', '.join(features)})"
        if token.type in {"VFIN", "VINF", "VIMP"} and entry and entry.transitivity:
            detail += f", {entry.transitivity}"
        return f"    {token.value}: {detail}"
    return None


def _one(result: ParseResult, db: Dictionary) -> str:
    lines = [f"Frase: {result.text}"]
    if result.parts:
        return "\n".join(_one(part, db) for part in result.parts)

    if not result.valid:
        lines.append("No se puede analizar como una oración completa.")
        if result.error:
            lines.append(f"  {result.error}")
        for diagnostic in result.diagnostics:
            if diagnostic.level in {"error", "warning"}:
                lines.append(f"  {diagnostic.level.upper()}: {diagnostic.message}")
        return "\n".join(lines)

    mood = _MOOD_ES.get(result.mood or "", "sin puntuación final")
    lines.append(f"Tipo: oración {mood}.")

    for item in result.constituents:
        note = f" ({item.note})" if item.note else ""
        role = _ROLE_ES.get(item.role, item.role)
        lines.append(f"  {role}: {item.text}{note}")

    if any(d.message.startswith("Frase nominal") for d in result.diagnostics):
        lines.append("  Es una frase nominal/elíptica: no tiene predicado explícito.")

    morphology = []
    for token in result.tokens:
        line = _morphology_line(token, db)
        if line:
            morphology.append(line)
    if morphology:
        lines.append("Morfología:")
        lines.extend(morphology[:20])
        if len(morphology) > 20:
            lines.append(f"    … y {len(morphology) - 20} palabras más")

    warnings = [d.message for d in result.diagnostics if d.level == "warning"]
    if warnings:
        lines.append("Avisos:")
        lines.extend(f"  - {message}" for message in warnings)

    lines.append(
        "Nota: se analiza la forma gramatical; no se juzga si la afirmación es verdadera."
    )
    return "\n".join(lines)


def explain(result: ParseResult) -> str:
    """Devuelve una explicación en español de una frase analizada."""
    db = Dictionary()
    try:
        return _one(result, db)
    finally:
        db.close()
