# Ido Study Tool

CLI dictionary for [Ido](https://en.wikipedia.org/wiki/Ido): look up words in either direction with English glosses, grammar, and related forms.

~14k entries in `data/ido.db`, imported from `data/idan.txt`. No web UI — standalone scripts only.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

```bash
# Ido → English (translation, grammar, derivations)
python scripts/dict_ido.py homo
python scripts/dict_ido.py abado

# English → Ido
python scripts/dict_en.py abandon
python scripts/dict_en.py abbot
```

Example output:

```
abado
  English: abbot; abbess
  Grammar: NOUN (singular)
  Suffixes: —
  Ending: -o
  Root: abad
  Derived:
    abadeyo — abbey (NOUN, -ey- place for)
    abadulo — abbot (NOUN, -ul- masculine)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `dict_ido.py` | Look up an Ido word |
| `dict_en.py` | Find Ido words from English |
| `dict_add.py` | Add or update an entry |
| `import_idan.py` | Re-import `idan.txt` (preserves user entries) |
| `phrase_add.py` | Save an Ido–English phrase pair |
| `phrase_search.py` | Search stored phrases |
| `fetch_tatoeba.py` | Download Tatoeba sentence pairs |

## Development

```bash
pytest
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md). Long-term goal: Ido language model. Current focus: get the consultation tool right.

## License

MIT
