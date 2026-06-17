"""Resolve project data paths relative to the package root."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
DB_PATH = DATA_DIR / "ido.db"
IDAN_PATH = DATA_DIR / "idan.txt"
SCHEMA_PATH = DATA_DIR / "schema.sql"
