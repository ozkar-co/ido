# Scripts

Standalone CLI tools. Run from the repository root:

```bash
python scripts/dict_ido.py abado
python scripts/dict_en.py abbot
```

See the main [README](../README.md) for setup and the full command reference.

| Script | Description |
|--------|-------------|
| `dict_ido.py` | Ido → English lookup (grammar, derivations) |
| `dict_en.py` | English → Ido lookup |
| `dict_add.py` | Add or update a word |
| `import_idan.py` | Import `data/idan.txt` into `data/ido.db` |
| `phrase_add.py` | Add a phrase pair |
| `phrase_count.py` | Count stored phrases |
| `phrase_search.py` | Search phrases |
| `fetch_tatoeba.py` | Download Tatoeba pairs to `data/tatoeba_ido_eng.txt` |
