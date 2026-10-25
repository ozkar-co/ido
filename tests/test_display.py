"""Tests de la salida del diccionario."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from db import init_db, rebuild_fts
from dictionary import Dictionary
from display import format_entry, format_morphology, format_search_compact, format_word


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    init_db(path)
    conn = sqlite3.connect(path)
    rows = [
        ("abado", "abad.o", "abad", "noun", "abbot; abbess", None),
        ("abadulo", "abad.ul.o", "abad", "noun", "abbot", 1),
        ("abadeyo", "abad.ey.o", "abad", "noun", "abbey", None),
        ("abadino", "abad.in.o", "abad", "noun", "abbess", None),
        ("manjar", "manj.ar", "manj", "verb", "to eat, consume", None),
    ]
    for lemma, segments, root, pos, translation, parent_id in rows:
        conn.execute(
            """
            INSERT INTO words
                (lemma, segments, root, pos, translation, parent_id, source)
            VALUES (?, ?, ?, ?, ?, ?, 'idan')
            """,
            (lemma, segments, root, pos, translation, parent_id),
        )
    conn.commit()
    rebuild_fts(conn)
    conn.close()
    return path


def test_format_word_is_solid():
    assert format_word("abad.o") == "abad.o"
    assert format_word("abado") == "abado"
    assert format_word("abadeyo") == "abadeyo"


def test_format_entry_is_solid(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abado")
        output = format_entry(db, entry)
        assert output.splitlines()[0] == "abado"
        assert "English: abbot" in output
        assert "Segmentación" not in output
        assert "Raíz: abad" in output
    finally:
        db.close()


def test_format_entry_family(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abado")
        output = format_entry(db, entry)
        assert "Derivadas:" in output
        assert "abadulo" in output
        assert "Misma raíz:" in output
        assert "abadeyo" in output
        assert "abadino" in output
    finally:
        db.close()


def test_format_morphology_verb(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("manjar")
        lines = format_morphology(entry, show_segments=True)
        text = "\n".join(lines)
        assert "verbo" in text
        assert "manj.ar" in text
        assert "manj" in text
        assert "-ar" in text
    finally:
        db.close()


def test_format_search_compact(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entries = db.lookup_en("eat", limit=3)
        output = format_search_compact(entries)
        assert "manjar" in output
        assert "to eat" in output
    finally:
        db.close()
