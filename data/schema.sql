-- Minimal schema for the Ido study tool.

CREATE TABLE IF NOT EXISTS words (
    id          INTEGER PRIMARY KEY,
    word        TEXT NOT NULL UNIQUE,
    root        TEXT,
    translation TEXT NOT NULL,
    parent_id   INTEGER REFERENCES words(id),
    source      TEXT NOT NULL DEFAULT 'idan',
    notes       TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS words_fts USING fts5(
    word,
    root,
    translation,
    content='words',
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Keep words FTS in sync.
CREATE TRIGGER IF NOT EXISTS words_ai AFTER INSERT ON words BEGIN
    INSERT INTO words_fts(rowid, word, root, translation)
    VALUES (new.id, new.word, new.root, new.translation);
END;

CREATE TRIGGER IF NOT EXISTS words_ad AFTER DELETE ON words BEGIN
    INSERT INTO words_fts(words_fts, rowid, word, root, translation)
    VALUES ('delete', old.id, old.word, old.root, old.translation);
END;

CREATE TRIGGER IF NOT EXISTS words_au AFTER UPDATE ON words BEGIN
    INSERT INTO words_fts(words_fts, rowid, word, root, translation)
    VALUES ('delete', old.id, old.word, old.root, old.translation);
    INSERT INTO words_fts(rowid, word, root, translation)
    VALUES (new.id, new.word, new.root, new.translation);
END;
