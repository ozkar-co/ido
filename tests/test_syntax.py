"""Tests del analizador sintáctico."""

from pathlib import Path

import pytest

from syntax import analyze, analyze_text

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
    roles = {item.role for item in result.constituents}
    assert "Sujeto" in roles
    assert "Predicado" in roles
    assert result.mood == "declarative"


def test_ka_question():
    result = analyze("Ka ilu vivas?")
    assert result.valid
    assert result.mood == "interrogative"
    assert any(item.role == "Marcador interrogativo" for item in result.constituents)


def test_question_marker_extracted():
    result = analyze("Quon tu imaginas?")
    assert result.valid
    assert any(item.role == "Marcador interrogativo" for item in result.constituents)


def test_subordinate_ke():
    result = analyze("Me kredas, ke Tom kredas to.")
    assert result.valid
    assert any(item.role == "Subordinada" for item in result.constituents)


def test_copula_adjective():
    result = analyze("La homo esas bona.")
    assert result.valid
    assert any(item.role == "Predicado" for item in result.constituents)


def test_perfect_tense():
    result = analyze("Me vidabas ol.")
    assert result.valid
    pred = next(item for item in result.constituents if item.role == "Predicado")
    assert "vidabas" in pred.text


def test_common_sentence_with_kato():
    result = analyze("La hundo mordas la kato.")
    assert result.valid


def test_accusative_sentence():
    result = analyze("La hundo mordas la katon.")
    assert result.valid
    assert any("katon" in item.text for item in result.constituents)


def test_unknown_proper_noun_is_allowed_with_warning():
    result = analyze("Flurbo manjas glopon.")
    assert result.valid
    assert any(d.level == "warning" and "glopon" in d.message for d in result.diagnostics)


def test_nonstandard_copula_warning():
    result = analyze("Me es feliz.")
    assert result.valid
    assert any("es" in d.message and d.level == "warning" for d in result.diagnostics)


def test_invalid_sentence_without_predicate():
    result = analyze("Me la homo.")
    assert not result.valid


def test_invalid_noun_sequence():
    result = analyze("Kato hundo.")
    assert not result.valid


def test_fragment_is_valid_with_info():
    result = analyze("Bona matino!")
    assert result.valid
    assert any(d.level == "info" and "elíptica" in d.message for d in result.diagnostics)


def test_multiple_sentences():
    results = analyze_text("Me manjas. Me dormas.")
    assert len(results) == 2
    assert all(result.valid for result in results)


def test_tag_question():
    result = analyze("El esas talentoza piktistino, ka ne?")
    assert result.valid


def test_relative_clause():
    result = analyze("La homo, quan me vidis, esas mea patro.")
    assert result.valid
