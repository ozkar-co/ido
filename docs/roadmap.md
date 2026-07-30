# Roadmap

Personal study tool for Ido. Standalone CLI scripts; no web interface.

## Phase 1 — Consultation tool (current focus)

- [x] Ido word → English translation
- [x] English → Ido lookup (FTS)
- [x] Grammar analysis in lookup output (category, suffixes, endings)
- [x] Derived forms and same-root family
- [x] Solid-form display (dotted notation stays internal only)
- [x] `scripts/dict_ido.py`, `scripts/dict_en.py`, `scripts/dict_add.py`

## Phase 2 — Derivator

- [ ] `scripts/derive.py` — generate inflected/derived forms from a root
- [x] `ido/morphology.py` exists (rule-based analyzer); needs a thin script

## Phase 3 — Phrase database

- [x] Add Ido–English phrase pairs
- [x] Count and search stored phrases
- [x] `scripts/phrase_add.py`, `phrase_count.py`, `phrase_search.py`

## Phase 4 — Syntax checker

- [ ] Deterministic EBNF parser (Lark)
- [ ] `scripts/grammar_check.py` — validate a sentence
- [ ] Audit collected phrases and translations for syntactic validity
- [ ] Fix `ido/grammar.lark` (Ido pronouns, not Esperanto)

## Phase 5 — Corpus

- [x] `scripts/fetch_tatoeba.py` — snapshot Tatoeba pairs into `data/tatoeba_ido_eng.txt`
- [ ] Define `corpus/` structure and scripts to build it from `data/`
- [ ] Export dictionary + phrases into unified training format

## Phase 6 — IDO-only language model

- [ ] Small LLM for Ido ↔ English translation
- [ ] Or conversational agent that thinks/speaks only Ido

## Explicitly out of scope

- Web UI / API
- Multi-language conlang framework
- Spanish translation layer

## Principles

Keep the codebase small: **KISS**, **YAGNI**, **DRY**. Dotted word notation (`hom.o`) is an internal representation for morphology and derivations; users always see solid forms (`homo`).
