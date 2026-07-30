# Ido Study Tool

CLI tools for [Ido](https://en.wikipedia.org/wiki/Ido): word lookup and sentence analysis.

~14k dictionary entries in `data/ido.db`; ~13k Tatoeba sentences in `data/tatoeba_ido_eng.txt`. Standalone scripts only.

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Word lookup

```bash
python scripts/dict_ido.py abado
python scripts/dict_en.py abbot
```

### Sentence analysis

```bash
python scripts/grammar_check.py "Il sempre malodoras."
python scripts/grammar_check.py "Ka ilu vivas?" --tree
python scripts/corpus_audit.py -n 500
python scripts/corpus_audit.py --failures -o data/audit_failures.txt
```

## Scripts

| Script | Purpose |
|--------|---------|
| `dict_ido.py` | Ido → English (grammar, derivations) |
| `dict_en.py` | English → Ido |
| `dict_add.py` | Add or update a dictionary entry |
| `grammar_check.py` | Validate and analyze an Ido sentence |
| `corpus_audit.py` | Test parser against Tatoeba corpus |
| `import_idan.py` | Re-import `idan.txt` |
| `fetch_tatoeba.py` | Download Tatoeba sentence pairs |

## Development

```bash
pytest
```

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## License

MIT
