"""Tests de la explicación procedural."""

from explain import explain
from syntax import analyze


def test_explains_subject_predicate_and_morphology():
    text = explain(analyze("Me manjas pano."))
    assert "Sujeto" in text
    assert "Predicado" in text
    assert "manj-" in text
    assert "-as" in text
    assert "no se juzga" in text


def test_explains_subordinate_clause():
    text = explain(analyze("Me pensas ke tu esas bela."))
    assert "Subordinada" in text
    assert "ke tu esas bela" in text


def test_explains_invalid_sentence():
    text = explain(analyze("Me la homo."))
    assert "No se puede analizar" in text
    assert "predicado" in text
