"""Tests for the Ido solid/dotted word lexer."""

from ido.lexer import (
    dotted_to_solid,
    format_word_display,
    lex,
    query_variants,
    solid_to_dotted,
)


def test_dotted_to_solid():
    assert dotted_to_solid("abad.o") == "abado"
    assert dotted_to_solid("abad.ey.o") == "abadeyo"
    assert dotted_to_solid("hom.o") == "homo"


def test_solid_to_dotted_simple_noun():
    assert solid_to_dotted("homo") == "hom.o"
    assert solid_to_dotted("abado") == "abad.o"


def test_solid_to_dotted_with_suffix():
    assert solid_to_dotted("abadeyo") == "abad.ey.o"


def test_solid_to_dotted_verb():
    assert solid_to_dotted("abandonas") == "abandon.as"


def test_solid_passthrough_dotted():
    assert solid_to_dotted("abad.in.o") == "abad.in.o"


def test_query_variants():
    assert "hom.o" in query_variants("homo")
    assert "homo" in query_variants("hom.o")


def test_format_word_display():
    assert format_word_display("abad.o") == "abado  (abad.o)"
    assert format_word_display("x") == "x"


def test_lex_solid():
    result = lex("homo")
    assert result.dotted == "hom.o"
    assert result.solid == "homo"
    assert result.root == "hom"
