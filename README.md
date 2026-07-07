# Ido Study Tool

A personal command-line toolkit for studying and practicing [Ido](https://en.wikipedia.org/wiki/Ido). Look up words, collect phrase pairs, and build toward grammar checking and translation tools.

No web UI — just small, independent scripts and an optional `ido` CLI wrapper.

## Quick start

```bash
pip install -e .
```

The dictionary works immediately: `data/ido.db` is committed with ~14k entries imported from `data/idan.txt`.

```bash
python scripts/dict_ido.py homo
python scripts/dict_ido.py abad.o
python scripts/dict_en.py abbot
```

## Word forms

The dictionary stores words in **dotted** morphological notation (`hom.o`, `abad.ey.o`) as in `idan.txt`. You can look up and add words in **solid** everyday form (`homo`, `abadeyo`); the lexer converts between the two.

- **Lookup**: `dict_ido homo` finds `hom.o` and shows `homo  (hom.o)`
- **Add**: `dict_add.py testo test "witness"` stores `test.o` with root `test`

Rules are in `ido/lexer.py` (grammatical endings from `data/quick_gramm.txt`, conservative suffix splitting).

## Scripts

Each script is standalone and can be run directly.

| Script | Purpose |
|--------|---------|
| `scripts/dict_ido.py` | Look up an Ido word (root + English gloss, derived forms) |
| `scripts/dict_en.py` | Find Ido words from an English term |
| `scripts/dict_add.py` | Add or update a dictionary entry |
| `scripts/phrase_add.py` | Save an Ido–English phrase pair |
| `scripts/phrase_count.py` | Show how many phrases are stored |
| `scripts/phrase_search.py` | Search stored phrases |
| `scripts/import_idan.py` | Import `idan.txt` into the database (idempotent) |
| `scripts/fetch_tatoeba.py` | Download Tatoeba Ido–English pairs to `data/tatoeba_ido_eng.txt` |

### Examples

```bash
# Ido → English
python scripts/dict_ido.py homo
python scripts/dict_ido.py abad.o
python scripts/dict_ido.py --root abad

# English → Ido
python scripts/dict_en.py abandon

# Add a word (solid or dotted)
python scripts/dict_add.py testo test "witness"

# Phrase collection (for future training data)
python scripts/phrase_add.py "Ku vu amas min?" "Do you love me?"
python scripts/phrase_count.py
python scripts/phrase_search.py love

# Tatoeba sentence pairs (raw data, not in phrase DB)
python scripts/fetch_tatoeba.py -n 100
python scripts/fetch_tatoeba.py
```

## Optional CLI

After `pip install -e .`, the same operations are available via Click:

```bash
ido lookup abad.o
ido en abbot
ido add-word hom.o hom "man"
ido phrase-add "Ku vu amas min?" "Do you love me?"
ido phrase-count
ido phrase-search love
```

## Data files

| File | Role |
|------|------|
| `data/idan.txt` | Source dictionary (~14k Ido–English entries) |
| `data/dyer_dict.txt` | English–Ido dictionary (Brian E. Drake, CC BY-NC 4.0) |
| `data/tatoeba_ido_eng.txt` | Ido–English sentences from Tatoeba |
| `data/ido.db` | Working SQLite database (dictionary + phrases) |
| `data/schema.sql` | Database schema |
| `data/quick_gramm.txt` | Quick Ido grammar reference (James Chandler, 1997) |

See [data/README.md](data/README.md) for sources and licenses.

### Re-importing from idan.txt

Safe to re-run; existing entries are skipped and **user-added words are preserved**:

```bash
python scripts/import_idan.py
```

To rebuild from scratch (destroys all data):

```bash
python scripts/import_idan.py --force
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## License

MIT
