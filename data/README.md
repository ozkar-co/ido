# Data

Reference files for dictionary and syntax tooling.

## Files

| File | Description |
|------|-------------|
| `idan.txt` | Ido–English dictionary (~14,700 entries) → `ido.db` via `import_idan.py` |
| `ido.db` | SQLite dictionary |
| `tatoeba_ido_eng.txt` | ~13k Ido–English sentences from Tatoeba |
| `quick_gramm.txt` | Ido grammar reference (James Chandler, 1997) — source for parser rules |
| `grammar.txt` | Grammar cheatsheet (Spanish summary) |
| `audit_failures.txt` | Parser failures from `corpus_audit.py` (generated, optional) |
| `gramm_book.txt` | Full Ido grammar manual (Spanish, reserved) |
| `kurso_book.txt` | Literary corpus — The Time Machine in Ido (reserved) |
| `vorti_book.txt` | Spanish–Ido dictionary (reserved) |
| `dyer_dict.txt` | English–Ido dictionary (Brian E. Drake, CC BY-NC 4.0) |
| `schema.sql` | Database schema |

## Tatoeba

```bash
python scripts/fetch_tatoeba.py
python scripts/corpus_audit.py --failures -o data/audit_failures.txt
```

## Database

User word additions via `dict_add.py` have `source = 'user'` and survive re-import.

```bash
python scripts/import_idan.py --force   # rebuild dictionary only
```
