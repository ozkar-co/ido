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

CREATE TABLE IF NOT EXISTS phrases (
    id         INTEGER PRIMARY KEY,
    ido        TEXT NOT NULL,
    english    TEXT NOT NULL,
    source     TEXT NOT NULL DEFAULT 'user',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS phrases_fts USING fts5(
    ido,
    english,
    content='phrases',
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

-- Keep phrases FTS in sync.
CREATE TRIGGER IF NOT EXISTS phrases_ai AFTER INSERT ON phrases BEGIN
    INSERT INTO phrases_fts(rowid, ido, english)
    VALUES (new.id, new.ido, new.english);
END;

CREATE TRIGGER IF NOT EXISTS phrases_ad AFTER DELETE ON phrases BEGIN
    INSERT INTO phrases_fts(phrases_fts, rowid, ido, english)
    VALUES ('delete', old.id, old.ido, old.english);
END;

CREATE TRIGGER IF NOT EXISTS phrases_au AFTER UPDATE ON phrases BEGIN
    INSERT INTO phrases_fts(phrases_fts, rowid, ido, english)
    VALUES ('delete', old.id, old.ido, old.english);
    INSERT INTO phrases_fts(rowid, ido, english)
    VALUES (new.id, new.ido, new.english);
END;
