"""Tests for Ido sentence syntax analysis."""

from pathlib import Path

import pytest

from ido.syntax import analyze

FIXTURES = Path(__file__).parent / "fixtures" / "sentences.txt"


def _load_valid_sentences() -> list[str]:
    lines = FIXTURES.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


@pytest.mark.parametrize("sentence", _load_valid_sentences())
def test_golden_sentences_parse(sentence: str):
    result = analyze(sentence)
    assert result.valid, result.error


def test_il_sempre_malodoras():
    result = analyze("Il sempre malodoras.")
    assert result.valid
    roles = {c.role for c in result.constituents}
    assert "Subject" in roles
    assert "Predicate" in roles
    assert result.mood == "declarative"


def test_ka_question():
    result = analyze("Ka ilu vivas?")
    assert result.valid
    assert result.mood == "interrogative"
    assert any(c.role == "Question marker" for c in result.constituents)


def test_subordinate_ke():
    result = analyze("Me kredas, ke Tom kredas to.")
    assert result.valid
    assert sum(1 for c in result.constituents if c.role == "Subject") >= 1


def test_copula_adjective():
    result = analyze("La homo esas bona.")
    assert result.valid
    assert any(c.role == "Copula" for c in result.constituents)


def test_perfect_tense():
    result = analyze("Me vidabas ol.")
    assert result.valid
    pred = next(c for c in result.constituents if c.role == "Predicate")
    assert pred.text == "vidabas"


def test_invalid_sentence():
    result = analyze("Me la homo.")
    assert not result.valid
