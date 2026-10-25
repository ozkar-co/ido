"""Auditoría del analizador contra el corpus local de Tatoeba."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from corpus import iter_tatoeba
from syntax import analyze
from tokens import split_sentences


@dataclass
class AuditResult:
    total: int = 0
    parsed: int = 0
    failures: list[str] = field(default_factory=list)
    clusters: Counter = field(default_factory=Counter)

    @property
    def failed(self) -> int:
        return self.total - self.parsed

    @property
    def coverage(self) -> float:
        return (self.parsed / self.total * 100) if self.total else 0.0


def audit_corpus(
    *,
    limit: int | None = None,
    every: int = 1,
    output: Path | None = None,
) -> AuditResult:
    """Procesa el corpus y devuelve métricas; opcionalmente guarda fallos."""
    if every < 1:
        raise ValueError("--every debe ser mayor que cero")

    result = AuditResult()
    for index, entry in enumerate(iter_tatoeba(), start=1):
        if every > 1 and (index - 1) % every != 0:
            continue
        if limit is not None and result.total >= limit:
            break

        result.total += 1
        parts = split_sentences(entry.ido)
        analyses = [analyze(part) for part in parts]
        bad = [analysis for analysis in analyses if not analysis.valid]
        if not bad:
            result.parsed += 1
            continue

        error = bad[0].error or "error desconocido"
        result.failures.append(
            f"{entry.id} | {entry.ido}\n         | {error}"
        )
        cluster = error.split(":", 1)[0][:100]
        result.clusters[cluster] += 1

    if output and result.failures:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n\n".join(result.failures) + "\n", encoding="utf-8")

    return result
