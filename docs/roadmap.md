# Roadmap

Personal study tool for Ido. Standalone CLI scripts; no web interface.

## Phase 1 — Word consultation tool

- [x] Ido ↔ English dictionary lookup with morphology
- [x] `scripts/dict_ido.py`, `dict_en.py`, `dict_add.py`

## Phase 2 — Sentence analyzer (current focus)

- [x] Lark grammar from `quick_gramm.txt` + `grammar.txt`
- [x] Tokenizer with Ido pronouns, particles, verb/noun endings
- [x] `scripts/grammar_check.py` — validate + show structure
- [x] `scripts/corpus_audit.py` — audit Tatoeba, report failures for manual review
- [ ] Expand grammar coverage (coordination, complex subordinates, literary forms)
- [ ] Tune against `data/audit_failures.txt`

## Phase 3 — Phrase generator

- [ ] Generate syntactically valid Ido from grammar templates + lexicon
- [ ] User supplies meaning; tool ensures valid structure

## Phase 4 — Phrase translation (optional)

- [ ] English → Ido sentence translation (dictionary + generator)
- [ ] Requires Phase 3

## Phase 5 — Corpus and language model

- [ ] Unified corpus export from dictionary + Tatoeba
- [ ] Small Ido ↔ English language model

Reference books (`gramm_book.txt`, `kurso_book.txt`, `vorti_book.txt`) reserved for future grammar/corpus work.

## Principles

**KISS**, **YAGNI**, **DRY**. Dotted word notation (`hom.o`) stays internal. Tatoeba failures may be parser gaps or source errors — review manually.
