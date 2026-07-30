"""Ido sentence syntax analysis using Lark."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from lark import Lark, Token, Tree, UnexpectedInput
from lark.exceptions import LarkError

from ido.tokens import ClassifiedToken, tokenize_sentence

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"


@dataclass
class Constituent:
    role: str
    text: str
    note: str


@dataclass
class ParseResult:
    text: str
    valid: bool
    tree: Tree | None = None
    error: str | None = None
    mood: str | None = None
    constituents: list[Constituent] = field(default_factory=list)


_parser: Lark | None = None


def _reset_parser() -> None:
    global _parser
    _parser = None


def _get_parser() -> Lark:
    global _parser
    if _parser is None:
        grammar = GRAMMAR_PATH.read_text(encoding="utf-8")
        _parser = Lark(grammar, start="sentence", parser="earley", ambiguity="resolve")
    return _parser


def _type_string(tokens: list[ClassifiedToken]) -> str:
    return " ".join(t.type for t in tokens)


def _attach_values(tree: Tree, tokens: list[ClassifiedToken]) -> None:
    """Replace type placeholder tokens with original word values."""
    index = 0

    def walk(node: Tree) -> None:
        nonlocal index
        for i, child in enumerate(node.children):
            if isinstance(child, Tree):
                walk(child)
            else:
                if index < len(tokens):
                    node.children[i] = Token(child.type, tokens[index].value)
                    index += 1

    walk(tree)


def _leaf_texts(tree: Tree) -> list[str]:
    out: list[str] = []
    for child in tree.children:
        if isinstance(child, Tree):
            out.extend(_leaf_texts(child))
        else:
            out.append(str(child))
    return out


def _note_for_token(token: ClassifiedToken) -> str:
    return token.note


def _extract_predicate(tree: Tree, token_map: dict[str, str]) -> list[Constituent]:
    result: list[Constituent] = []
    for child in tree.children:
        if not isinstance(child, Tree):
            continue
        if child.data == "head":
            text = " ".join(_leaf_texts(child))
            is_copula = any(
                isinstance(c, Token) and c.type == "COPULA" for c in child.children
            )
            kind = "Copula" if is_copula else "Predicate"
            note = token_map.get(text, "")
            result.append(Constituent(kind, text, note))
        elif child.data == "modifier":
            text = " ".join(_leaf_texts(child))
            result.append(Constituent("Modifier", text, token_map.get(text, "")))
        elif child.data == "complement":
            text = " ".join(_leaf_texts(child))
            first = text.split()[0] if text else ""
            result.append(Constituent("Complement", text, token_map.get(first, "")))
    return result


def _token_map(tokens: list[ClassifiedToken]) -> dict[str, str]:
    return {t.value: t.note for t in tokens}


def _extract_constituents(tree: Tree, tokens: list[ClassifiedToken]) -> list[Constituent]:
    notes = _token_map(tokens)
    result: list[Constituent] = []

    if tree.data == "sentence":
        for child in tree.children:
            if isinstance(child, Tree):
                result.extend(_extract_constituents(child, tokens))
        return result

    if tree.data in {"declarative", "interrogative", "clause", "simple", "sub_clause", "coord_clause"}:
        for child in tree.children:
            if isinstance(child, Tree):
                result.extend(_extract_constituents(child, tokens))
        return result

    if tree.data in {"copula_adj", "copula_np"}:
        texts = _leaf_texts(tree)
        if texts:
            result.append(Constituent("Copula", texts[0], notes.get(texts[0], "")))
        if len(texts) > 1:
            result.append(Constituent("Complement", " ".join(texts[1:]), ""))
        return result

    if tree.data == "statement":
        for child in tree.children:
            if not isinstance(child, Tree):
                continue
            if child.data == "np":
                text = " ".join(_leaf_texts(child))
                first = text.split()[0] if text else ""
                result.append(Constituent("Subject", text, notes.get(first, "")))
            elif child.data == "predicate":
                result.extend(_extract_predicate(child, notes))
            elif child.data in {"copula_adj", "copula_np"}:
                result.extend(_extract_constituents(child, tokens))
        return result

    if tree.data == "question":
        for child in tree.children:
            if isinstance(child, Tree):
                if child.data in {"QU", "KAD"}:
                    text = " ".join(_leaf_texts(child))
                    result.append(Constituent("Question marker", text, notes.get(text, "")))
                else:
                    result.extend(_extract_constituents(child, tokens))
            elif isinstance(child, Token) and child.type in {"QU", "KAD"}:
                result.append(
                    Constituent("Question marker", str(child), notes.get(str(child), ""))
                )
        return result

    for child in tree.children:
        if isinstance(child, Tree):
            result.extend(_extract_constituents(child, tokens))
    return result


def analyze(text: str) -> ParseResult:
    """Parse an Ido sentence and extract grammatical constituents."""
    stripped = text.strip()
    if not stripped:
        return ParseResult(text=text, valid=False, error="Empty sentence")

    mood = None
    if stripped.endswith("?"):
        mood = "interrogative"
    elif stripped.endswith("."):
        mood = "declarative"
    elif stripped.endswith("!"):
        mood = "exclamative"

    classified = tokenize_sentence(stripped)
    if not classified:
        return ParseResult(text=stripped, valid=False, error="No tokens")

    parser = _get_parser()
    try:
        tree = parser.parse(_type_string(classified))
        _attach_values(tree, classified)
        constituents = _extract_constituents(tree, classified)
        return ParseResult(
            text=stripped,
            valid=True,
            tree=tree,
            mood=mood,
            constituents=constituents,
        )
    except UnexpectedInput as exc:
        return ParseResult(text=stripped, valid=False, error=str(exc), mood=mood)
    except LarkError as exc:
        return ParseResult(text=stripped, valid=False, error=str(exc), mood=mood)


def format_tree(tree: Tree, indent: int = 0) -> str:
    """Pretty-print a Lark parse tree."""
    prefix = "  " * indent
    lines = [f"{prefix}{tree.data}"]
    for child in tree.children:
        if isinstance(child, Tree):
            lines.append(format_tree(child, indent + 1))
        else:
            lines.append(f"{prefix}  {child.type}: {child.value}")
    return "\n".join(lines)


def format_analysis(result: ParseResult, *, show_tree: bool = False) -> str:
    """Format parse result for CLI output (English)."""
    lines = [f"Valid: {'yes' if result.valid else 'no'}", result.text]

    if result.valid:
        if result.mood:
            lines.append(f"  Mood: {result.mood}")
        for item in result.constituents:
            note = f" ({item.note})" if item.note else ""
            lines.append(f"  {item.role + ':':16} {item.text}{note}")
        if show_tree and result.tree is not None:
            lines.append("")
            lines.append("Parse tree:")
            lines.append(format_tree(result.tree))
    elif result.error:
        lines.append(f"  Error: {result.error}")

    return "\n".join(lines)
