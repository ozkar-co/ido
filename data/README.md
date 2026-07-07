# Data

Raw reference files for study and future tooling. Formats vary by source; nothing here is loaded into `ido.db` automatically except via explicit import scripts.

## Files

| File | Description |
|------|-------------|
| `idan.txt` | Ido–English dictionary (~14,700 entries). Imported into `ido.db` via `import_idan.py`. |
| `dyer_dict.txt` | English–Ido dictionary by Brian E. Drake (updated 2024). See [license](#dyer-dictionary) below. |
| `tatoeba_ido_eng.txt` | Ido–English sentence pairs from [Tatoeba](https://tatoeba.org). Fetched with `fetch_tatoeba.py`. |
| `quick_gramm.txt` | Quick Ido grammar guide (James Chandler, 1997). |
| `ido.db` | Working SQLite database (dictionary + user phrases). |
| `schema.sql` | Database schema. |

## Dyer dictionary

**Author:** Brian E. Drake  
**License:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Attribution-NonCommercial 4.0 International)

Based on the dictionaries by L.H. Dyer, updated and expanded 2024. English headwords with Ido equivalents; proposed words marked with `*`. Not imported into `ido.db` yet.

## Tatoeba sentences

Fetched from the Tatoeba API (`lang=ido`, English translations). Each entry includes sentence id, license, and one or more English glosses.

```bash
python scripts/fetch_tatoeba.py              # full dump (~15k sentences)
python scripts/fetch_tatoeba.py -n 100       # first 100 only
python scripts/fetch_tatoeba.py --direct-only
```

Output: `data/tatoeba_ido_eng.txt`

```
=== 13936469 ===
license: CC BY 2.0 FR
ido: Il sempre malodoras.
eng: He always stinks. [direct]
```

## Database (`ido.db`)

- Words from `idan.txt` have `source = 'idan'`.
- User additions via `dict_add.py` have `source = 'user'` and are not overwritten on re-import.
- Phrases are user-added only (`source = 'user'`).

Rebuild from scratch:

```bash
python scripts/import_idan.py --force
```
