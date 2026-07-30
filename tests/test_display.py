"""Tests for user-facing dictionary display."""

from __future__ import annotations

from pathlib import Path

import pytest

from ido.db import init_db, rebuild_fts
from ido.dictionary import Dictionary
from ido.display import format_entry, format_search_results, format_word, format_grammar


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    init_db(path)
    import sqlite3

    conn = sqlite3.connect(path)
    conn.execute(
        """
        INSERT INTO words (word, root, translation, source)
        VALUES ('abad.o', 'abad', 'abbot; abbess', 'idan')
        """
    )
    conn.execute(
        """
        INSERT INTO words (word, root, translation, parent_id, source)
        VALUES ('abad.ul.o', 'abad', 'abbot', 1, 'idan')
        """
    )
    conn.execute(
        """
        INSERT INTO words (word, root, translation, source)
        VALUES ('abad.ey.o', 'abad', 'abbey', 'idan')
        """
    )
    conn.execute(
        """
        INSERT INTO words (word, root, translation, source)
        VALUES ('abad.in.o', 'abad', 'abbess', 'idan')
        """
    )
    conn.commit()
    rebuild_fts(conn)
    conn.close()
    return path


def test_format_word_solid_only():
    assert format_word("abad.o") == "abado"
    assert format_word("hom.o") == "homo"
    assert "." not in format_word("abad.ey.o")


def test_format_grammar_noun(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abado")
        assert entry is not None
        lines = format_grammar(entry)
        assert any("NOUN" in line for line in lines)
        assert any("Suffixes: —" in line for line in lines)
    finally:
        db.close()


def test_format_grammar_with_suffix(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abadulo")
        assert entry is not None
        lines = format_grammar(entry)
        text = "\n".join(lines)
        assert "ul" in text
        assert "masculine" in text
    finally:
        db.close()


def test_format_entry_no_dots(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abado")
        assert entry is not None
        output = format_entry(db, entry)
        assert "abado" in output
        assert "abad.o" not in output
        assert "English:" in output
        assert "Grammar:" in output
        assert "Root: abad" in output
    finally:
        db.close()


def test_format_entry_derived_and_same_root(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abado")
        assert entry is not None
        output = format_entry(db, entry)
        assert "Derived:" in output
        assert "abadulo" in output
        assert "Same root:" in output
        assert "abadeyo" in output
        assert "abadino" in output
    finally:
        db.close()


def test_format_search_results_full_entries(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entries = db.lookup_en("abbot")
        assert entries
        output = format_search_results(db, entries)
        assert "Grammar:" in output
        assert "abad.o" not in output
        assert "abado" in output or "abadulo" in output
    finally:
        db.close()
