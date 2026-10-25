"""Importa data/idan.txt a una base SQLite con lemas sólidos."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from db import init_db, rebuild_fts
from morphology import MorphologyAnalyzer
from paths import DB_PATH, IDAN_PATH, WORDS_TSV_PATH

WORD_RE = re.compile(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' .-]*$")
TAG_RE = re.compile(r"\s*[\[{(][^\]})]*[\]})]")
TRANSITIVITY_RE = re.compile(r"\{(tr/intr|tr|intr|imp)\}")
ANALYZER = MorphologyAnalyzer()


def _clean_word_field(value: str) -> str:
    value = TAG_RE.sub("", value)
    value = value.strip().strip(",")
    return value


def _pos_for(segments: str) -> str:
    """Deduce la categoría a partir de la última terminación de la fuente."""
    word = segments.lower().rstrip(".")
    if not word:
        return "other"
    if word.startswith("-") or word.endswith("-"):
        return "affix"
    tail = word.rsplit(".", 1)[-1] if "." in word else word
    if tail.endswith(("ar", "ir", "or", "as", "is", "os", "us", "ez")):
        return "verb"
    if tail.endswith(("ant", "int", "ont", "at", "it", "ot")):
        return "participle"
    if tail[-1:] in {"o", "i"}:
        return "noun"
    if tail[-1:] == "a":
        return "adj"
    if tail[-1:] == "e":
        return "adv"
    return "other"


def _root_for(segments: str) -> str | None:
    """Calcula la raíz real, respetando prefijos (ne-, des-, ri-...)."""
    if not segments or segments.startswith("-") or segments.endswith("-"):
        return None
    analysis = ANALYZER.analyze(segments)
    root = analysis.root.strip().lower()
    if len(root) < 2:
        return None
    return root


def _is_letter_header(line: str) -> bool:
    return bool(re.match(r"^\s*[A-Z]\s*$", line))


def _is_entry_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("---"):
        return False
    if line.startswith("        "):
        return True
    if not (stripped[0].isalpha() or stripped[0] in "-["):
        return False
    return bool(re.search(r"\s\s+|\t", line))


def _parse_entry(line: str) -> dict | None:
    """Convierte una línea de idan.txt en un registro.

    Descarta encabezados y entradas cuyo campo de palabra no parece una
    palabra (traducciones partidas, notas, etc.).
    """
    is_derived = line.startswith("        ")
    clean = line.strip()
    if clean.startswith("["):
        clean = clean.lstrip("[")

    parts = re.split(r"\s\s+|\t", clean, maxsplit=1)
    if len(parts) < 2:
        return None

    word_field = _clean_word_field(parts[0])
    translation = TAG_RE.sub("", parts[1]).strip()
    if not word_field or not translation:
        return None
    if not WORD_RE.fullmatch(word_field):
        return None
    if len(word_field) > 40:
        return None
    if word_field.lower() in {"a", "i", "o"} and " " in word_field:
        return None

    segments = word_field.lower()
    lemma = segments.replace(".", "")
    if not lemma:
        return None

    pos = "phrase" if " " in word_field else _pos_for(segments)
    proper = int(word_field[0].isupper())
    transitivity_match = TRANSITIVITY_RE.search(line)
    transitivity = transitivity_match.group(1) if transitivity_match else None
    if transitivity is None and "{tr/intr}" in line:
        transitivity = "tr/intr"

    return {
        "lemma": lemma,
        "segments": segments,
        "root": _root_for(segments),
        "pos": pos,
        "transitivity": transitivity,
        "proper": proper,
        "translation": " ".join(translation.split()),
        "is_derived": is_derived,
    }


def _find_abbr_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if "Abreviuri en Ido" in line or "Abbreviations in Ido" in line:
            return i
    return len(lines)


def import_idan(
    conn: sqlite3.Connection,
    lines: list[str],
    *,
    end_line: int,
) -> Counter:
    """Inserta las entradas; devuelve estadísticas de importación."""
    stats: Counter = Counter()
    current_parent_id: int | None = None
    pending: dict | None = None
    seen: set[tuple[str, str, int, str]] = set()

    def flush() -> None:
        nonlocal pending, current_parent_id
        if pending is None:
            return
        key = (
            pending["lemma"],
            pending["pos"],
            pending["proper"],
            pending["translation"].lower(),
        )
        if key in seen:
            stats["duplicates"] += 1
            pending = None
            return
        seen.add(key)

        cursor = conn.execute(
            """
            INSERT INTO words
                (lemma, segments, root, pos, transitivity, proper,
                 translation, parent_id, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'idan')
            """,
            (
                pending["lemma"],
                pending["segments"],
                pending["root"],
                pending["pos"],
                pending["transitivity"],
                pending["proper"],
                pending["translation"],
                current_parent_id if pending["is_derived"] else None,
            ),
        )
        row_id = cursor.lastrowid
        stats["inserted"] += 1
        if pending["is_derived"]:
            stats["derived"] += 1
        else:
            current_parent_id = row_id
        if pending["proper"]:
            stats["proper"] += 1
        if pending["pos"] == "phrase":
            stats["phrases"] += 1
        pending = None

    for line_num, line in enumerate(lines[:end_line], start=1):
        if line_num < 47 or _is_letter_header(line):
            continue

        if not _is_entry_line(line):
            if pending is not None and line.strip():
                pending["translation"] += " " + line.strip()
            continue

        entry = _parse_entry(line)
        if entry is None:
            stats["invalid"] += 1
            continue

        flush()
        pending = entry

    flush()
    conn.commit()
    return stats


def write_words_tsv(conn: sqlite3.Connection, path: Path = WORDS_TSV_PATH) -> int:
    """Exporta una vista de texto plano para grep y revisión manual."""
    rows = conn.execute(
        """
        SELECT lemma, COALESCE(segments, ''), pos,
               COALESCE(transitivity, ''), translation,
               COALESCE(root, ''), source
        FROM words
        WHERE pos != 'affix'
        ORDER BY lower(lemma), lemma
        """
    ).fetchall()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write("\t".join(str(value) for value in row) + "\n")
    return len(rows)


def build_database(
    db_path: Path = DB_PATH,
    source_path: Path = IDAN_PATH,
    *,
    force: bool = False,
) -> Counter:
    """Reconstruye la base desde idan.txt conservando las entradas de usuario."""
    if not source_path.exists():
        raise FileNotFoundError(f"No existe el diccionario: {source_path}")

    user_rows: list[sqlite3.Row] = []
    if force and db_path.exists():
        old = sqlite3.connect(db_path)
        old.row_factory = sqlite3.Row
        try:
            user_rows = old.execute(
                "SELECT * FROM words WHERE source = 'user'"
            ).fetchall()
        except sqlite3.Error:
            user_rows = []
        finally:
            old.close()

    if force or not db_path.exists():
        init_db(db_path, force=True)
    else:
        init_db(db_path)
    lines = source_path.read_text(encoding="utf-8").splitlines(keepends=True)
    end_line = max(0, _find_abbr_start(lines) - 10)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        stats = import_idan(conn, lines, end_line=end_line)
        for row in user_rows:
            conn.execute(
                """
                INSERT INTO words
                    (lemma, segments, root, pos, transitivity, proper,
                     translation, parent_id, source, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 'user', ?)
                """,
                (
                    row["lemma"], row["segments"], row["root"], row["pos"],
                    row["transitivity"], row["proper"], row["translation"],
                    row["notes"],
                ),
            )
            stats["users"] += 1
        conn.commit()
        rebuild_fts(conn)
        total = conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
        stats["total"] = total
        stats["tsv"] = write_words_tsv(conn)
    finally:
        conn.close()
    return stats


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Importar idan.txt a data/ido.db")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--dict", type=Path, default=IDAN_PATH)
    parser.add_argument("--force", action="store_true", help="Recrear la base")
    args = parser.parse_args(argv)

    try:
        stats = build_database(args.db, args.dict, force=args.force)
    except (FileNotFoundError, sqlite3.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Importación completa")
    print(f"  Insertadas: {stats['inserted']}")
    print(f"  Derivadas:  {stats['derived']}")
    print(f"  Nombres propios: {stats['proper']}")
    print(f"  Inválidas:  {stats['invalid']}")
    print(f"  Duplicadas: {stats['duplicates']}")
    print(f"  Total:      {stats['total']}")
    print(f"  TSV:        {stats['tsv']} filas")


if __name__ == "__main__":
    main()
