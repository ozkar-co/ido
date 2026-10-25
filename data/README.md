# Datos

| Archivo | Descripción |
|---------|-------------|
| `idan.txt` | Diccionario Ido–Inglés de origen (14k entradas, notación punteada) |
| `ido.db` | Diccionario SQLite con lemas sólidos, raíz, categoría y segmentación |
| `words.tsv` | Exportación de `ido.db` para `grep` y revisión manual |
| `tatoeba_ido_eng.txt` | ~13k pares Ido–Inglés de Tatoeba |
| `quick_gramm.txt` | Referencia gramatical de James Chandler |
| `grammar.txt` | Resumen gramatical en español |
| `gramm_book.txt` | Gramática extensa en español |
| `kurso_book.txt` | Corpus literario de apoyo |
| `dyer_dict.txt` | Diccionario Inglés–Ido de Dyer (reserva) |
| `vorti_book.txt` | Diccionario Español–Ido (no usado: alcance actual Ido–Inglés) |
| `schema.sql` | Esquema de `ido.db` |

## Base de datos

`ido.db` se reconstruye desde `idan.txt`:

```bash
.venv/bin/python main.py import --force
```

La forma canónica es el lema sólido (`manjar`); `segments` conserva la segmentación
de estudio (`manj.ar`) y `root` se calcula con la morfología, no con el primer punto.
`words.tsv` se regenera en la misma importación. Las entradas añadidas con
`main.py add` (`source='user'`) se conservan al reimportar con `--force`.
