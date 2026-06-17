"""Fetch Ido–English sentence pairs from the Tatoeba API."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

TATOEBA_URL = (
    "https://api.tatoeba.org/v1/sentences"
    "?sort=created&lang=ido&showtrans:lang=eng"
)


def fetch_page(url: str, *, timeout: float = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ido-study-tool/0.2 (personal corpus collector)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def format_sentence(sentence: dict[str, Any], *, direct_only: bool = False) -> str | None:
    """Format one Tatoeba sentence block, or None if it has no English translations."""
    translations = sentence.get("translations") or []
    if direct_only:
        translations = [t for t in translations if t.get("is_direct")]

    eng = [t for t in translations if t.get("lang") == "eng"]
    if not eng:
        return None

    lines = [
        f"=== {sentence['id']} ===",
        f"license: {sentence.get('license', '')}",
        f"ido: {sentence['text']}",
    ]
    for item in eng:
        tag = " [direct]" if item.get("is_direct") else ""
        lines.append(f"eng: {item['text']}{tag}")
    lines.append("")
    return "\n".join(lines)


def iter_sentences(
    *,
    start_url: str | None = None,
    max_count: int | None = None,
    delay: float = 0,
) -> Iterator[dict[str, Any]]:
    """Yield sentence records, following Tatoeba pagination."""
    url = start_url or TATOEBA_URL
    fetched = 0

    while url:
        page = fetch_page(url)
        for sentence in page.get("data", []):
            yield sentence
            fetched += 1
            if max_count is not None and fetched >= max_count:
                return

        paging = page.get("paging") or {}
        if not paging.get("has_next"):
            return

        url = paging.get("next")
        if delay > 0 and url:
            time.sleep(delay)
