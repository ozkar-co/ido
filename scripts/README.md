# Scripts

Run from the repository root:

```bash
python scripts/dict_ido.py abado
python scripts/grammar_check.py "Il sempre malodoras."
python scripts/corpus_audit.py -n 100
```

| Script | Description |
|--------|-------------|
| `dict_ido.py` | Ido → English lookup |
| `dict_en.py` | English → Ido lookup |
| `dict_add.py` | Add or update a word |
| `grammar_check.py` | Analyze / validate a sentence |
| `corpus_audit.py` | Audit Tatoeba against the parser |
| `import_idan.py` | Import `idan.txt` into `ido.db` |
| `fetch_tatoeba.py` | Download Tatoeba pairs |

See [README](../README.md) for setup.
