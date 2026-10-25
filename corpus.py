"""Read sentence corpora from plain-text files."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from paths import TATOEBA_PATH

_ENTRY_RE = re.compile(r"^=== (\d+) ===$")
_IDO_RE = re.compile(r"^ido: (.+)$")
_ENG_RE = re.compile(r"^eng: (.+)$")
_LICENSE_RE = re.compile(r"^license: (.+)$")


@dataclass(frozen=True)
class TatoebaEntry:
    id: int
    ido: str
    english: tuple[str, ...]
    license: str | None = None


def iter_tatoeba(path: Path | str | None = None) -> Iterator[TatoebaEntry]:
    """Yield Tatoeba entries from a snapshot file."""
    file_path = Path(path) if path else TATOEBA_PATH
    if not file_path.exists():
        raise FileNotFoundError(f"Tatoeba corpus not found: {file_path}")

    entry_id: int | None = None
    ido: str | None = None
    english: list[str] = []
    license: str | None = None

    def flush() -> TatoebaEntry | None:
        nonlocal entry_id, ido, english, license
        if entry_id is None or not ido:
            return None
        result = TatoebaEntry(
            id=entry_id,
            ido=ido,
            english=tuple(english),
            license=license,
        )
        entry_id = None
        ido = None
        english = []
        license = None
        return result

    with file_path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            match = _ENTRY_RE.match(line)
            if match:
                finished = flush()
                if finished:
                    yield finished
                entry_id = int(match.group(1))
                continue

            if entry_id is None:
                continue

            ido_match = _IDO_RE.match(line)
            if ido_match:
                ido = ido_match.group(1).strip()
                continue

            eng_match = _ENG_RE.match(line)
            if eng_match:
                text = eng_match.group(1).strip()
                text = re.sub(r"\s*\[direct\]\s*$", "", text)
                english.append(text)
                continue

            license_match = _LICENSE_RE.match(line)
            if license_match:
                license = license_match.group(1).strip()

        finished = flush()
        if finished:
            yield finished


def load_tatoeba_sentences(path: Path | str | None = None) -> list[str]:
    """Return Ido sentences only."""
    return [entry.ido for entry in iter_tatoeba(path)]


def load_tatoeba_entries(path: Path | str | None = None) -> list[TatoebaEntry]:
    """Return full Tatoeba entries."""
    return list(iter_tatoeba(path))
