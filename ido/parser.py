"""Backward-compatible alias for ido.syntax."""

from ido.syntax import ParseResult, analyze, format_analysis, format_tree

__all__ = ["ParseResult", "analyze", "format_analysis", "format_tree"]


class IdoParser:
    """Legacy wrapper around the syntax analyzer."""

    def __init__(self) -> None:
        pass

    def parse(self, text: str):
        result = analyze(text)
        if not result.valid or result.tree is None:
            raise ValueError(result.error or "Parse failed")
        return result.tree

    def parse_to_dict(self, text: str) -> dict:
        tree = self.parse(text)
        return _tree_to_dict(tree)


def _tree_to_dict(tree) -> dict:
    result: dict = {"type": tree.data}
    if tree.children:
        children = []
        for child in tree.children:
            if hasattr(child, "data"):
                children.append(_tree_to_dict(child))
            else:
                children.append(str(child))
        result["children"] = children
    return result
