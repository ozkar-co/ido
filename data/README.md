# Data

## Files

| File | Description |
|------|-------------|
| `idan.txt` | Ido–English dictionary (~14,700 entries). Source for imports. |
| `ido.db` | SQLite database: dictionary + phrase collection. Committed to the repo. |
| `schema.sql` | Database schema (words, phrases, FTS indexes). |
| `quick_gramm.txt` | Quick Ido grammar guide (James Chandler, 1997). |

## Dictionary source

`idan.txt` is derived from the public Ido dictionary (Idan). Used for personal study and tooling.

## Database

- **Words** imported from `idan.txt` have `source = 'idan'`.
- **User additions** via `dict_add.py` have `source = 'user'` and are never overwritten by re-import.
- **Phrases** are always user-added (`source = 'user'`).

Rebuild from scratch:

```bash
python scripts/import_idan.py --force
```
