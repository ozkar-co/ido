"""Formato de resultados del analizador."""

from __future__ import annotations

from lark import Tree

from syntax import ParseResult



def format_tree(tree: Tree, indent: int = 0) -> str:
    """Imprime el árbol de Lark de forma legible."""
    prefix = "  " * indent
    lines = [f"{prefix}{tree.data}"]
    for child in tree.children:
        if isinstance(child, Tree):
            lines.append(format_tree(child, indent + 1))
        else:
            lines.append(f"{prefix}  {child.type}: {child.value}")
    return "\n".join(lines)


MOOD_ES = {
    "declarative": "declarativa",
    "interrogative": "interrogativa",
    "exclamative": "exclamativa",
}


def _format_one(result: ParseResult, *, show_tree: bool = False) -> str:
    lines = [f"Válida: {'sí' if result.valid else 'no'}", result.text]
    if result.mood:
        lines.append(f"  Modo: {MOOD_ES.get(result.mood, result.mood)}")
    if result.valid:
        for item in result.constituents:
            note = f" ({item.note})" if item.note else ""
            lines.append(f"  {item.role + ':':22} {item.text}{note}")
    elif result.error:
        lines.append(f"  Error: {result.error}")

    for diagnostic in result.diagnostics:
        icon = {"error": "ERROR", "warning": "AVISO", "info": "INFO"}.get(
            diagnostic.level, diagnostic.level.upper()
        )
        lines.append(f"  {icon}: {diagnostic.message}")

    if show_tree and result.tree is not None:
        lines.append("")
        lines.append("Árbol sintáctico:")
        lines.append(format_tree(result.tree))
    return "\n".join(lines)


def format_analysis(result: ParseResult, *, show_tree: bool = False) -> str:
    """Formatea uno o varios resultados."""
    if result.parts:
        blocks = []
        for index, part in enumerate(result.parts, start=1):
            blocks.append(f"--- Oración {index} ---")
            blocks.append(_format_one(part, show_tree=show_tree))
        return "\n".join(blocks)
    return _format_one(result, show_tree=show_tree)
