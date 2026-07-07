# Roadmap

Personal study tool for Ido. Each phase adds CLI scripts; no web interface.

## Phase 0 — Resources

- [x] `data/idan.txt` — full Ido–English dictionary
- [x] `data/quick_gramm.txt` — grammar notes
- [x] Text resources as reference for future AI work

## Phase 1 — Ido word lookup

- [x] Look up an Ido word → root + English gloss
- [x] List words by root
- [x] Show derived forms (`parent_id` links)
- [x] `scripts/dict_ido.py`, `scripts/dict_add.py`

## Phase 2 — English → Ido lookup

- [x] FTS search on English glosses
- [x] `scripts/dict_en.py`

## Phase 3 — Derivator

- [ ] `scripts/derive.py` — generate inflected/derived forms from a root
- [x] `ido/morphology.py` exists (rule-based analyzer); needs a thin script

## Phase 4 — Phrase database

- [x] Add Ido–English phrase pairs
- [x] Count and search stored phrases
- [x] `scripts/phrase_add.py`, `phrase_count.py`, `phrase_search.py`

## Phase 5 — Syntax checker

- [ ] Deterministic EBNF parser (Lark)
- [ ] `scripts/grammar_check.py` — validate a sentence
- [ ] Audit collected phrases and translations for syntactic validity
- [ ] Fix `ido/grammar.lark` (Ido pronouns, not Esperanto)

## Phase 6 — Corpus (later)

- [x] `scripts/fetch_tatoeba.py` — snapshot Tatoeba pairs into `data/tatoeba_ido_eng.txt`
- [ ] Define `corpus/` structure and scripts to build it from `data/`
- [ ] Export dictionary + phrases into unified training format

## Phase 7 — IDO-only language model

- [ ] Small LLM for Ido ↔ English translation
- [ ] Or conversational agent that thinks/speaks only Ido

## Explicitly out of scope

- Web UI / API
- Multi-language conlang framework
- Spanish translation layer

## Principles

Keep the codebase small and maintainable: **KISS**, **YAGNI**, **DRY**, fail fast on missing data, one responsibility per script.
