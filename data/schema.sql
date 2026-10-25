-- Esquema del diccionario Ido. Las claves son formas sólidas (manjar);
-- la segmentación punteada (manj.ar) se conserva solo como metadato de estudio.

CREATE TABLE IF NOT EXISTS words (
    id           INTEGER PRIMARY KEY,
    lemma        TEXT NOT NULL,
    segments     TEXT,
    root         TEXT,
    pos          TEXT NOT NULL DEFAULT 'other',
    transitivity TEXT,
    proper       INTEGER NOT NULL DEFAULT 0,
    translation  TEXT NOT NULL,
    parent_id    INTEGER REFERENCES words(id),
    source       TEXT NOT NULL DEFAULT 'idan',
    notes        TEXT
);

CREATE INDEX IF NOT EXISTS words_lemma_idx ON words(lower(lemma));
CREATE INDEX IF NOT EXISTS words_root_idx ON words(lower(root));
CREATE INDEX IF NOT EXISTS words_pos_idx ON words(pos);

CREATE VIRTUAL TABLE IF NOT EXISTS words_fts USING fts5(
    lemma,
    root,
    translation,
    content='words',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS words_ai AFTER INSERT ON words BEGIN
    INSERT INTO words_fts(rowid, lemma, root, translation)
    VALUES (new.id, new.lemma, new.root, new.translation);
END;

CREATE TRIGGER IF NOT EXISTS words_ad AFTER DELETE ON words BEGIN
    INSERT INTO words_fts(words_fts, rowid, lemma, root, translation)
    VALUES ('delete', old.id, old.lemma, old.root, old.translation);
END;

CREATE TRIGGER IF NOT EXISTS words_au AFTER UPDATE ON words BEGIN
    INSERT INTO words_fts(words_fts, rowid, lemma, root, translation)
    VALUES ('delete', old.id, old.lemma, old.root, old.translation);
    INSERT INTO words_fts(rowid, lemma, root, translation)
    VALUES (new.id, new.lemma, new.root, new.translation);
END;
