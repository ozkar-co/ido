-- Schema para la base de datos del diccionario Ido
-- Versión: 1.0.0
-- Fecha: 2025-12-09

-- Tabla principal de palabras
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    word_type TEXT,  -- adv., konj., interj., prep., pref., suf., tr, intr, tr/intr, imp
    translation TEXT NOT NULL,
    definition TEXT,  -- Definición completa
    category TEXT CHECK (category IN (
        'NOUN', 'ADJECTIVE', 'ADVERB', 'VERB', 
        'PREPOSITION', 'CONJUNCTION', 'PRONOUN', 
        'ARTICLE', 'INTERJECTION', 'PARTICLE',
        'PREFIX', 'SUFFIX', 'GRAMMAR'
    )),
    subcategory TEXT,  -- anat., bot., kem., etc.
    grammatical_info TEXT,  -- [de], {tr}, {intr}, etc.
    antonym TEXT,  -- Palabra antónima
    obsolete BOOLEAN DEFAULT 0,
    replaced_by TEXT,  -- Si es obsoleta, palabra que la reemplazó
    parent_word_id INTEGER,  -- Para palabras derivadas
    root_id INTEGER,
    examples TEXT,  -- JSON array
    notes TEXT,
    frequency INTEGER DEFAULT 0,
    source TEXT DEFAULT 'idan.txt',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (root_id) REFERENCES roots(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Raíces morfológicas
CREATE TABLE IF NOT EXISTS roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root TEXT NOT NULL UNIQUE,
    meaning TEXT NOT NULL,
    etymology TEXT,
    semantic_field TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prefijos y sufijos
CREATE TABLE IF NOT EXISTS affixes (
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

-- Relaciones de derivación
CREATE TABLE IF NOT EXISTS derivations (
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

-- Excepciones e irregularidades
CREATE TABLE IF NOT EXISTS exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    exception_type TEXT NOT NULL,
    description TEXT NOT NULL,
    irregular_form TEXT,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Traducciones múltiples
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    translation TEXT NOT NULL,
    context TEXT,
    register TEXT,
    confidence INTEGER CHECK (confidence >= 1 AND confidence <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Categorías y abreviaturas
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    abbreviation TEXT NOT NULL UNIQUE,
    ido_name TEXT,
    english_name TEXT NOT NULL,
    category_type TEXT CHECK (category_type IN ('FIELD', 'GRAMMAR', 'OTHER')),
    description TEXT
);

-- Apariciones en corpus
CREATE TABLE IF NOT EXISTS corpus_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    context TEXT,
    position INTEGER,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_words_word ON words(word);
CREATE INDEX IF NOT EXISTS idx_words_category ON words(category);
CREATE INDEX IF NOT EXISTS idx_words_subcategory ON words(subcategory);
CREATE INDEX IF NOT EXISTS idx_words_root_id ON words(root_id);
CREATE INDEX IF NOT EXISTS idx_words_parent ON words(parent_word_id);
CREATE INDEX IF NOT EXISTS idx_words_obsolete ON words(obsolete);
CREATE INDEX IF NOT EXISTS idx_roots_root ON roots(root);
CREATE INDEX IF NOT EXISTS idx_categories_abbr ON categories(abbreviation);
CREATE INDEX IF NOT EXISTS idx_derivations_base ON derivations(base_word_id);
CREATE INDEX IF NOT EXISTS idx_derivations_derived ON derivations(derived_word_id);
CREATE INDEX IF NOT EXISTS idx_corpus_word ON corpus_occurrences(word_id);
CREATE INDEX IF NOT EXISTS idx_corpus_source ON corpus_occurrences(source);
CREATE INDEX IF NOT EXISTS idx_translations_word ON translations(word_id);
CREATE INDEX IF NOT EXISTS idx_translations_lang ON translations(language);
