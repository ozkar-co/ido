# Esquema del Diccionario

Base de datos SQLite para almacenamiento léxico.

## Tablas

### words

Palabras completas con traducción.

```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    translation TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'NOUN', 'ADJECTIVE', 'ADVERB', 'VERB', 
        'PREPOSITION', 'CONJUNCTION', 'PRONOUN', 
        'ARTICLE', 'INTERJECTION', 'PARTICLE'
    )),
    root_id INTEGER,
    definition TEXT,
    examples TEXT,  -- JSON array
    notes TEXT,
    frequency INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (root_id) REFERENCES roots(id) ON DELETE SET NULL
);

CREATE INDEX idx_words_word ON words(word);
CREATE INDEX idx_words_category ON words(category);
CREATE INDEX idx_words_root_id ON words(root_id);
```

### roots

Raíces morfológicas.

```sql
CREATE TABLE roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root TEXT NOT NULL UNIQUE,
    meaning TEXT NOT NULL,
    etymology TEXT,
    semantic_field TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roots_root ON roots(root);
```

### affixes

Prefijos y sufijos.

```sql
CREATE TABLE affixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affix TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('PREFIX', 'SUFFIX')),
    function TEXT NOT NULL,
    category_from TEXT,
    category_to TEXT,
    meaning TEXT,
    examples TEXT,
    productive BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### derivations

Relaciones de derivación.

```sql
CREATE TABLE derivations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_word_id INTEGER NOT NULL,
    derived_word_id INTEGER NOT NULL,
    affix_id INTEGER,
    derivation_type TEXT CHECK (derivation_type IN (
        'SUFFIXATION', 'PREFIXATION', 'COMPOSITION', 'OTHER'
    )),
    notes TEXT,
    FOREIGN KEY (base_word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (derived_word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (affix_id) REFERENCES affixes(id) ON DELETE SET NULL,
    UNIQUE(base_word_id, derived_word_id)
);
```

### exceptions

Irregularidades.

```sql
CREATE TABLE exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    exception_type TEXT NOT NULL,
    description TEXT NOT NULL,
    irregular_form TEXT,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);
```

### translations

Traducciones múltiples.

```sql
CREATE TABLE translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'es',
    translation TEXT NOT NULL,
    context TEXT,
    register TEXT,
    confidence INTEGER CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);
```

### corpus_occurrences

Apariciones en corpus.

```sql
CREATE TABLE corpus_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    context TEXT,
    position INTEGER,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);
```

## Consultas Comunes

### Buscar palabra

```sql
SELECT * FROM words WHERE word = 'domo';
```

### Buscar por raíz

```sql
SELECT w.* 
FROM words w
JOIN roots r ON w.root_id = r.id
WHERE r.root = 'dom';
```

### Palabras por categoría

```sql
SELECT word, translation 
FROM words 
WHERE category = 'VERB'
ORDER BY frequency DESC;
```

### Derivaciones

```sql
SELECT 
    base.word AS base,
    derived.word AS derivada,
    a.affix,
    d.derivation_type
FROM derivations d
JOIN words base ON d.base_word_id = base.id
JOIN words derived ON d.derived_word_id = derived.id
LEFT JOIN affixes a ON d.affix_id = a.id
WHERE base.word = 'belo';
```

## Población Inicial

```sql
-- Raíces
INSERT INTO roots (root, meaning, semantic_field) VALUES
    ('dom', 'casa, hogar', 'arquitectura'),
    ('bel', 'bello, hermoso', 'estética'),
    ('bon', 'bueno', 'cualidad'),
    ('labor', 'trabajo', 'actividad');

-- Afijos
INSERT INTO affixes (affix, type, function, category_to, productive) VALUES
    ('o', 'SUFFIX', 'Sustantivo', 'NOUN', 1),
    ('a', 'SUFFIX', 'Adjetivo', 'ADJECTIVE', 1),
    ('e', 'SUFFIX', 'Adverbio', 'ADVERB', 1),
    ('i', 'SUFFIX', 'Verbo infinitivo', 'VERB', 1),
    ('as', 'SUFFIX', 'Verbo presente', 'VERB', 1);

-- Palabras
INSERT INTO words (word, translation, category, root_id) VALUES
    ('domo', 'casa', 'NOUN', 1),
    ('bela', 'hermoso', 'ADJECTIVE', 2),
    ('bele', 'hermosamente', 'ADVERB', 2),
    ('bono', 'bondad', 'NOUN', 3),
    ('labori', 'trabajar', 'VERB', 4);
```

## Migraciones

Archivos numerados: `migrations/001_initial_schema.sql`, `002_add_field.sql`, etc.

## Backup

```bash
sqlite3 dictionary.db ".backup dictionary_backup.db"
sqlite3 dictionary.db .dump > dictionary_dump.sql
```
