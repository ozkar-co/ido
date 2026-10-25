"""Análisis sintáctico de frases Ido con Lark."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lark import Lark, Token, Tree, UnexpectedInput
from lark.exceptions import LarkError

from paths import ROOT
from tokens import ClassifiedToken, split_sentences, tokenize_sentence

GRAMMAR_PATH = ROOT / "grammar.lark"

EXPECTED_ES = {
    "PRON": "pronombre",
    "POSS": "posesivo",
    "DET": "determinante",
    "NOUN": "sustantivo",
    "ADJ": "adjetivo",
    "ADV": "adverbio",
    "VFIN": "verbo conjugado",
    "VINF": "infinitivo",
    "VPART": "participio",
    "VIMP": "imperativo",
    "COP": "cópula",
    "PREP": "preposición",
    "CONJ": "conjunción",
    "KE": "subordinador",
    "SE": "condicional",
    "QU": "interrogativo/relativo",
    "KAD": "partícula interrogativa",
    "NEG": "negación",
    "PART": "partícula",
    "NAME": "nombre propio",
    "NUM": "número",
    "OTHER": "palabra",
    "PUNCT_DOT": "punto",
    "PUNCT_Q": "signo de interrogación",
    "PUNCT_EX": "signo de exclamación",
    "PUNCT_COMMA": "coma",
    "PUNCT_SEMI": "punto y coma",
    "PUNCT_COLON": "dos puntos",
}


@dataclass
class Diagnostic:
    level: str
    message: str
    token_index: int | None = None


@dataclass
class Constituent:
    role: str
    text: str
    note: str = ""


@dataclass
class ParseResult:
    text: str
    valid: bool
    tree: Tree | None = None
    error: str | None = None
    mood: str | None = None
    constituents: list[Constituent] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    tokens: list[ClassifiedToken] = field(default_factory=list)
    parts: list["ParseResult"] = field(default_factory=list)


_parser: Lark | None = None


def _get_parser() -> Lark:
    global _parser
    if _parser is None:
        grammar = GRAMMAR_PATH.read_text(encoding="utf-8")
        _parser = Lark(grammar, start="start", parser="earley", ambiguity="resolve")
    return _parser


def _parse_tokens(tokens: list[ClassifiedToken]) -> list[ClassifiedToken]:
    return [token for token in tokens if token.type != "QUOTE"]


def _type_string(tokens: list[ClassifiedToken]) -> str:
    return " ".join(token.type for token in tokens)


def _tag_offsets(tokens: list[ClassifiedToken]) -> list[tuple[int, int]]:
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for token in tokens:
        offsets.append((cursor, cursor + len(token.type)))
        cursor += len(token.type) + 1
    return offsets


def _index_for_column(column: int | None, tokens: list[ClassifiedToken]) -> int | None:
    if column is None or not tokens:
        return None
    position = max(0, column - 1)
    for index, (start, end) in enumerate(_tag_offsets(tokens)):
        if start <= position <= end:
            return index
    return min(len(tokens) - 1, max(0, position // 2))


def _expected_text(exc: UnexpectedInput) -> str:
    expected = getattr(exc, "expected", None) or set()
    labels = [EXPECTED_ES.get(item, item) for item in sorted(expected)]
    if not labels:
        return "una estructura distinta"
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " o " + labels[-1]


def _diagnose_parse_error(exc: UnexpectedInput, tokens: list[ClassifiedToken]) -> tuple[str, Diagnostic]:
    index = _index_for_column(getattr(exc, "column", None), tokens)
    token = tokens[index] if index is not None and index < len(tokens) else None
    expected = _expected_text(exc)
    if token is None:
        message = f"La frase termina antes de completar la estructura; se esperaba {expected}."
        return message, Diagnostic("error", message, index)
    message = (
        f"Error cerca de «{token.value}» (posición {index + 1}): "
        f"se esperaba {expected}."
    )
    if token.known is False:
        message += " La palabra no está en el diccionario."
    return message, Diagnostic("error", message, index)


def _attach_values(tree: Tree, tokens: list[ClassifiedToken]) -> None:
    index = 0

    def walk(node: Tree) -> None:
        nonlocal index
        for position, child in enumerate(node.children):
            if isinstance(child, Tree):
                walk(child)
            else:
                if index < len(tokens):
                    node.children[position] = Token(
                        child.type, tokens[index].value
                    )
                    index += 1

    walk(tree)


def _leaf_texts(tree: Tree) -> list[str]:
    output: list[str] = []
    for child in tree.children:
        if isinstance(child, Tree):
            output.extend(_leaf_texts(child))
        else:
            output.append(str(child))
    return output


def _text(tree: Tree) -> str:
    return " ".join(_leaf_texts(tree))


def _token_map(tokens: list[ClassifiedToken]) -> dict[str, ClassifiedToken]:
    return {token.value: token for token in tokens}


def _add_constituent(
    result: list[Constituent],
    role: str,
    tree: Tree,
    notes: dict[str, ClassifiedToken],
) -> None:
    text = _text(tree)
    words = text.split()
    nominal_roles = {
        "Sujeto", "Complemento", "Vocativo", "Atributo", "Grupo nominal",
    }
    key = words[-1] if role in nominal_roles and words else (words[0] if words else "")
    token = notes.get(key)
    result.append(Constituent(role, text, token.note if token else ""))


def _leaf_types(tree: Tree) -> list[str]:
    output: list[str] = []
    for child in tree.children:
        if isinstance(child, Tree):
            output.extend(_leaf_types(child))
        else:
            output.append(child.type)
    return output


def _collect(node: Tree, result: list[Constituent], notes: dict[str, ClassifiedToken], role: str = "") -> None:
    if not isinstance(node, Tree):
        return
    data = node.data

    if data == "start":
        for child in node.children:
            if isinstance(child, Tree):
                _collect(child, result, notes)
        return

    if data == "sentence":
        for child in node.children:
            if isinstance(child, Tree):
                _collect(child, result, notes)
        return

    if data == "question":
        for child in node.children:
            if isinstance(child, Tree):
                _collect(child, result, notes)
            elif isinstance(child, Token) and child.type in {"KAD", "QU"}:
                result.append(Constituent("Marcador interrogativo", str(child), "INTERROGATIVO"))
        return

    if data == "clause":
        after_comma = False
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "unit":
                _collect(child, result, notes, "Vocativo" if after_comma else role)
            else:
                _collect(child, result, notes, role)
            after_comma = True
        return

    if data == "unit":
        for child in node.children:
            if isinstance(child, Tree):
                _collect(child, result, notes, role)
        return

    if data == "segment":
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "core":
                _collect(child, result, notes, role)
            elif child.data == "front":
                for part in child.children:
                    if isinstance(part, Tree) and part.data == "pp":
                        _add_constituent(result, "Complemento circunstancial", part, notes)
            elif child.data == "back":
                for part in child.children:
                    if isinstance(part, Tree) and part.data == "pp":
                        _add_constituent(result, "Complemento circunstancial", part, notes)
            elif child.data == "sub_clause":
                _collect(child, result, notes)
        return

    if data == "core":
        children = [child for child in node.children if isinstance(child, Tree)]
        if len(children) == 1 and children[0].data == "np":
            _collect(children[0], result, notes, role or "Sujeto")
            return
        for child in children:
            if child.data == "np":
                role_np = "Sujeto (subordinada)" if role == "Subordinada" else "Sujeto"
                _collect(child, result, notes, role_np)
            elif child.data == "predicate":
                role_pred = "Predicado (subordinada)" if role == "Subordinada" else "Predicado"
                _collect(child, result, notes, role_pred)
        return

    if data == "np":
        _add_constituent(result, role or "Grupo nominal", node, notes)
        return

    if data == "predicate":
        _add_constituent(result, role or "Predicado", node, notes)
        for child in node.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "complement":
                leaf_types = _leaf_types(child)
                if leaf_types:
                    if leaf_types[0] == "ADJ":
                        _add_constituent(result, "Atributo", child, notes)
                    elif leaf_types[0] == "VPART":
                        _add_constituent(result, "Participio", child, notes)
                    elif leaf_types[0] == "VINF":
                        _add_constituent(result, "Infinitivo", child, notes)
                    elif leaf_types[0] == "np":
                        _add_constituent(result, "Complemento", child, notes)
                    else:
                        _collect(child, result, notes, "Complemento")
            elif child.data == "pp":
                _add_constituent(result, "Complemento preposicional", child, notes)
            elif child.data in {"ke_clause", "se_clause", "qu_clause", "rel_clause"}:
                _collect(child, result, notes)
        return

    if data == "complement":
        for child in node.children:
            if isinstance(child, Tree):
                _collect(child, result, notes, "Complemento")
        return

    if data == "pp":
        _add_constituent(result, "Complemento preposicional", node, notes)
        return

    if data in {"ke_clause", "se_clause", "qu_clause", "rel_clause"}:
        _add_constituent(result, "Subordinada", node, notes)
        for child in node.children:
            if isinstance(child, Tree) and child.data == "clause":
                _collect(child, result, notes, "Subordinada")
        return

    if data == "interjection":
        _add_constituent(result, "Interjección", node, notes)
        return

    for child in node.children:
        if isinstance(child, Tree):
            _collect(child, result, notes, role)

def _constituents(tree: Tree, tokens: list[ClassifiedToken]) -> list[Constituent]:
    result: list[Constituent] = []
    _collect(tree, result, _token_map(tokens))
    return result


PREDICATE_TYPES = {"VFIN", "VIMP", "COP", "VPART", "VINF"}


def _tree_leaf_types(tree: Tree) -> list[str]:
    types: list[str] = []
    for child in tree.children:
        if isinstance(child, Tree):
            types.extend(_tree_leaf_types(child))
        else:
            types.append(child.type)
    return types


def _validate_clauses(tree: Tree, result: ParseResult) -> None:
    if not isinstance(tree, Tree):
        return
    if tree.data in {"question", "ke_clause", "se_clause", "qu_clause", "rel_clause"}:
        leaf_types = _tree_leaf_types(tree)
        if tree.data == "question" and "KAD" in leaf_types and all(
            item in {"KAD", "NEG", "PART"} for item in leaf_types
        ):
            return
        if tree.data in {"qu_clause", "rel_clause"}:
            leaves = [
                child for child in _leaf_texts(tree) if child
            ]
            first = leaves[0].lower() if leaves else ""
            if tree.data == "qu_clause" and first in {"quale", "quanta", "quala"}:
                return
            if not any(item in PREDICATE_TYPES for item in leaf_types):
                result.valid = False
                result.error = "La oración relativa no tiene predicado."
                result.diagnostics.append(Diagnostic("error", result.error))
            return
        if not any(item in PREDICATE_TYPES for item in leaf_types):
            result.valid = False
            result.error = (
                "La oración interrogativa no tiene predicado."
                if tree.data == "question"
                else "La oración subordinada no tiene predicado."
            )
            result.diagnostics.append(Diagnostic("error", result.error))
            return
    for child in tree.children:
        if isinstance(child, Tree):
            _validate_clauses(child, result)


def _validate(tokens: list[ClassifiedToken], result: ParseResult) -> None:
    """Añade advertencias y convierte fragmentos sin predicado en inválidos."""
    content = [
        token for token in tokens
        if token.type not in {
            "PUNCT_DOT", "PUNCT_Q", "PUNCT_EX", "PUNCT_COMMA",
            "PUNCT_SEMI", "PUNCT_COLON", "QUOTE",
        }
    ]
    has_predicate = any(token.type in PREDICATE_TYPES for token in content)

    if content and not has_predicate:
        has_comma = any(token.type == "PUNCT_COMMA" for token in tokens)
        has_prep = any(token.type == "PREP" for token in content)
        has_conj = any(token.type == "CONJ" for token in content)
        types = [token.type for token in content]
        pron_det = any(
            types[index] == "PRON" and types[index + 1] == "DET"
            for index in range(len(types) - 1)
        )
        noun_noun = any(
            types[index] == "NOUN" and types[index + 1] == "NOUN"
            for index in range(len(types) - 1)
        )
        demonstratives = {"ta", "ita", "to", "ito", "co", "ico"}
        pronoun_noun = any(
            types[index] == "PRON"
            and types[index + 1] == "NOUN"
            and content[index].value.lower() not in demonstratives
            for index in range(len(types) - 1)
        )
        invalid_fragment = pron_det or pronoun_noun or (
            noun_noun and not (has_comma or has_prep or has_conj)
        )
        if not invalid_fragment:
            result.diagnostics.append(
                Diagnostic("info", "Frase nominal o elíptica; no hay predicado explícito.")
            )
        else:
            result.valid = False
            result.error = "Falta un predicado: la frase no tiene verbo ni cópula."
            result.diagnostics.append(Diagnostic("error", result.error))

    if result.tree is not None:
        _validate_clauses(result.tree, result)

    for index, token in enumerate(tokens):
        if token.type in {"PUNCT_DOT", "PUNCT_Q", "PUNCT_EX", "PUNCT_COMMA", "PUNCT_SEMI", "PUNCT_COLON"}:
            continue
        if token.value.lower() == "es":
            result.diagnostics.append(
                Diagnostic("warning", "«es» no es la forma estándar; usa «esas».", index)
            )
        elif not token.known and token.type == "NAME":
            result.diagnostics.append(
                Diagnostic(
                    "info",
                    f"«{token.value}» no está en el diccionario; se trata como nombre propio.",
                    index,
                )
            )
        elif not token.known:
            result.diagnostics.append(
                Diagnostic(
                    "warning",
                    f"«{token.value}» no está en el diccionario. "
                    "Si es un nombre propio, escríbelo con mayúscula.",
                    index,
                )
            )


def analyze(text: str) -> ParseResult:
    """Analiza una sola frase y devuelve árbol, constituyentes y diagnóstico."""
    stripped = text.strip()
    if not stripped:
        return ParseResult(text=text, valid=False, error="La frase está vacía.")

    mood = None
    if stripped.endswith("?"):
        mood = "interrogative"
    elif stripped.endswith("!"):
        mood = "exclamative"
    elif stripped.endswith("."):
        mood = "declarative"

    tokens = tokenize_sentence(stripped)
    parse_tokens = _parse_tokens(tokens)
    if not parse_tokens:
        return ParseResult(text=stripped, valid=False, error="No hay palabras.", tokens=tokens)

    parser = _get_parser()
    try:
        tree = parser.parse(_type_string(parse_tokens))
        _attach_values(tree, parse_tokens)
        result = ParseResult(
            text=stripped,
            valid=True,
            tree=tree,
            mood=mood,
            constituents=_constituents(tree, parse_tokens),
            tokens=tokens,
        )
        _validate(tokens, result)
        return result
    except UnexpectedInput as exc:
        message, diagnostic = _diagnose_parse_error(exc, parse_tokens)
        return ParseResult(
            text=stripped,
            valid=False,
            error=message,
            mood=mood,
            diagnostics=[diagnostic],
            tokens=tokens,
        )
    except LarkError as exc:
        message = f"No se pudo analizar la frase: {exc}"
        return ParseResult(
            text=stripped,
            valid=False,
            error=message,
            mood=mood,
            diagnostics=[Diagnostic("error", message)],
            tokens=tokens,
        )


def analyze_text(text: str) -> list[ParseResult]:
    """Analiza cada oración de un texto y conserva los resultados parciales."""
    sentences = split_sentences(text)
    if not sentences:
        return [analyze(text)]
    return [analyze(sentence) for sentence in sentences]
