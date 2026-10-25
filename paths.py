"""Rutas del proyecto, resueltas desde la raíz del repositorio."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "ido.db"
IDAN_PATH = DATA_DIR / "idan.txt"
TATOEBA_PATH = DATA_DIR / "tatoeba_ido_eng.txt"
SCHEMA_PATH = DATA_DIR / "schema.sql"
WORDS_TSV_PATH = DATA_DIR / "words.tsv"
AUDIT_FAILURES_PATH = DATA_DIR / "audit_failures.txt"
