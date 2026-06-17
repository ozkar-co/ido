"""Tests for dictionary and phrase storage."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ido.db import init_db, rebuild_fts
from ido.dictionary import Dictionary
from ido.paths import DB_PATH
from ido.phrases import PhraseStore


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    init_db(path)
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
    conn.commit()
    rebuild_fts(conn)
    conn.close()
    return path


def test_db_path_is_absolute():
    assert DB_PATH.is_absolute()
    assert DB_PATH.name == "ido.db"


def test_lookup_ido(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.lookup_ido("abad.o")
        assert entry is not None
        assert entry.root == "abad"
        assert "abbot" in entry.translation
    finally:
        db.close()


def test_lookup_en_fts(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entries = db.lookup_en("abbot")
        assert any(e.word == "abad.o" for e in entries)
    finally:
        db.close()


def test_add_word_user_source(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.add_word("test.o", "test", "trial word")
        assert entry.source == "user"
        again = db.lookup_ido("test.o")
        assert again is not None
        assert again.translation == "trial word"
    finally:
        db.close()


def test_list_derived(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        derived = db.list_derived("abad.o")
        assert any(d.word == "abad.ul.o" for d in derived)
    finally:
        db.close()


def test_phrase_round_trip(db_path: Path):
    store = PhraseStore(str(db_path))
    try:
        assert store.count() == 0
        phrase = store.add("Me amas?", "Do you love me?")
        assert phrase.id == 1
        assert store.count() == 1
        found = store.search("love")
        assert any(p.ido == "Me amas?" for p in found)
    finally:
        store.close()


def test_lookup_works_from_any_cwd(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir("/tmp")
    db = Dictionary(str(db_path))
    try:
        assert db.lookup_ido("abad.o") is not None
    finally:
        db.close()
