"""Resolve project data paths relative to the package root."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
CORPUS_DIR = PACKAGE_ROOT / "corpus"  # generated later from data/
DB_PATH = DATA_DIR / "ido.db"
IDAN_PATH = DATA_DIR / "idan.txt"
DYER_DICT_PATH = DATA_DIR / "dyer_dict.txt"
TATOEBA_PATH = DATA_DIR / "tatoeba_ido_eng.txt"
SCHEMA_PATH = DATA_DIR / "schema.sql"
