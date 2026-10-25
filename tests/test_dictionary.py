"""Tests del diccionario sólido y de la lematización."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from db import init_db, rebuild_fts
from dictionary import Dictionary
from paths import DB_PATH


def _insert(conn: sqlite3.Connection, lemma: str, translation: str, **fields) -> None:
    values = {
        "lemma": lemma,
        "segments": fields.get("segments", lemma),
        "root": fields.get("root"),
        "pos": fields.get("pos", "other"),
        "transitivity": fields.get("transitivity"),
        "proper": fields.get("proper", 0),
        "translation": translation,
        "parent_id": fields.get("parent_id"),
        "source": fields.get("source", "idan"),
    }
    conn.execute(
        """
        INSERT INTO words
            (lemma, segments, root, pos, transitivity, proper,
             translation, parent_id, source)
        VALUES (:lemma, :segments, :root, :pos, :transitivity, :proper,
                :translation, :parent_id, :source)
        """,
        values,
    )


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    init_db(path)
    conn = sqlite3.connect(path)
    _insert(conn, "abado", "abbot; abbess", segments="abad.o", root="abad", pos="noun")
    _insert(conn, "abadulo", "abbot", segments="abad.ul.o", root="abad", pos="noun", parent_id=1)
    _insert(conn, "abadeyo", "abbey", segments="abad.ey.o", root="abad", pos="noun")
    _insert(conn, "abadino", "abbess", segments="abad.in.o", root="abad", pos="noun")
    _insert(conn, "manjar", "to eat, consume", segments="manj.ar", root="manj", pos="verb", transitivity="tr")
    _insert(conn, "devorar", "to devour; eat greedily", segments="devor.ar", root="devor", pos="verb", transitivity="tr")
    _insert(conn, "homo", "human, man", segments="hom.o", root="hom", pos="noun")
    _insert(conn, "kato", "cat", segments="kat.o", root="kat", pos="noun")
    _insert(conn, "bona", "good. Ant: mala", segments="bon.a", root="bon", pos="adj")
    _insert(conn, "bonajo", "good thing", segments="bon.aj.o", root="bon", pos="noun")
    _insert(conn, "goto", "gout", segments="got.o", root="got", pos="noun", proper=0)
    _insert(conn, "goto", "Goth", segments="got.o", root="got", pos="noun", proper=1)
    conn.commit()
    rebuild_fts(conn)
    conn.close()
    return path


def test_db_path_is_absolute():
    assert DB_PATH.is_absolute()
    assert DB_PATH.name == "ido.db"


def test_lookup_solid_and_dotted(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        assert db.lookup_ido("abado").lemma == "abado"
        assert db.lookup_ido("abad.o").lemma == "abado"
        assert db.lookup_ido("abado").root == "abad"
    finally:
        db.close()


def test_lemmatizes_verb_forms(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        for form in ("manjas", "manjis", "manjos", "manjus", "manjabas"):
            result = db.find(form)
            assert result is not None, form
            assert result.entry.lemma == "manjar"
            assert result.note
        assert db.find("manjante").entry.lemma == "manjar"
    finally:
        db.close()


def test_lemmatizes_plural_and_accusative(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        assert db.find("homi").entry.lemma == "homo"
        assert db.find("homin").entry.lemma == "homo"
        assert db.find("katon").entry.lemma == "kato"
    finally:
        db.close()


def test_english_search_prefers_exact_gloss(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entries = db.lookup_en("to eat", limit=5)
        assert entries[0].lemma == "manjar"
        assert any(entry.lemma == "devorar" for entry in entries)
    finally:
        db.close()


def test_english_search_prefers_exact_adjective(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entries = db.lookup_en("good", limit=3)
        assert entries[0].lemma == "bona"
    finally:
        db.close()


def test_proper_noun_preference(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        assert db.find("goto").entry.proper == 0
        assert db.find("Goto").entry.proper == 1
    finally:
        db.close()


def test_add_word_user_source(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        entry = db.add_word("testo", "trial word", root="test", pos="noun")
        assert entry.source == "user"
        again = db.find("testo")
        assert again is not None
        assert again.entry.translation == "trial word"
    finally:
        db.close()


def test_list_derived(db_path: Path):
    db = Dictionary(str(db_path))
    try:
        derived = db.list_derived("abado")
        assert any(item.lemma == "abadulo" for item in derived)
    finally:
        db.close()


def test_lookup_works_from_any_cwd(db_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir("/tmp")
    db = Dictionary(str(db_path))
    try:
        assert db.lookup_ido("abado") is not None
    finally:
        db.close()
