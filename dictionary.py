"""Consulta y actualización del diccionario Ido–Inglés."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterable

from db import connect
from morphology import MorphologicalAnalysis, MorphologyAnalyzer
from paths import DB_PATH

_ANALYZER = MorphologyAnalyzer()
_VERB_ENDINGS = {"ar", "ir", "or", "as", "is", "os", "us", "ez"}
_PARTICIPLE_RE = re.compile(r"^(.+?)(ant|int|ont|at|it|ot)([aeoi])$")
_PERFECT_RE = re.compile(r"^(.+?)(abas|abis|abos|abus)$")


@dataclass
class WordEntry:
    id: int
    lemma: str
    segments: str | None
    root: str | None
    pos: str
    transitivity: str | None
    proper: int
    translation: str
    parent_id: int | None
    source: str
    notes: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "WordEntry":
        return cls(
            id=row["id"],
            lemma=row["lemma"],
            segments=row["segments"],
            root=row["root"],
            pos=row["pos"],
            transitivity=row["transitivity"],
            proper=row["proper"],
            translation=row["translation"],
            parent_id=row["parent_id"],
            source=row["source"],
            notes=row["notes"],
        )

    @property
    def word(self) -> str:
        """Alias de compatibilidad: la forma principal es el lema sólido."""
        return self.lemma


@dataclass
class Lookup:
    """Resultado de una consulta, con la forma encontrada y su explicación."""

    entry: WordEntry
    query: str
    note: str | None = None
    analysis: MorphologicalAnalysis | None = None


def _normalize(text: str) -> str:
    return text.strip().lower().replace("’", "'")


def _segments_for(solid: str) -> str:
    """Segmentación aproximada para palabras añadidas por el usuario."""
    analysis = _ANALYZER.analyze(solid)
    parts: list[str] = []
    parts.extend(analysis.prefixes)
    parts.append(analysis.root)
    parts.extend(analysis.suffixes)
    if analysis.ending:
        parts.append(analysis.ending)
    return ".".join(part for part in parts if part)


class Dictionary:
    """Acceso al diccionario con lemas sólidos y lematización regular."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(DB_PATH)
        self._conn = connect(self.db_path)

    def close(self) -> None:
        self._conn.close()

    def _rows_for(self, column: str, value: str) -> list[sqlite3.Row]:
        return self._conn.execute(
            f"SELECT * FROM words WHERE lower({column}) = lower(?)",
            (value,),
        ).fetchall()

    def _best(self, rows: Iterable[sqlite3.Row], query: str) -> WordEntry | None:
        entries = [WordEntry.from_row(row) for row in rows]
        if not entries:
            return None
        # Si el usuario escribe mayúscula, preferir el nombre propio.
        wants_proper = query[:1].isupper()
        entries.sort(
            key=lambda entry: (
                entry.proper != int(wants_proper),
                entry.source != "user",
                entry.pos == "affix",
                entry.lemma.lower(),
            )
        )
        return entries[0]

    def lookup_ido(self, word: str) -> WordEntry | None:
        """Compatibilidad: devuelve la entrada, sin metadatos de forma."""
        result = self.find(word)
        return result.entry if result else None

    def lookup_all(self, word: str) -> list[WordEntry]:
        """Todas las entradas que comparten el lema exacto."""
        query = _normalize(word)
        if "." in query:
            rows = self._rows_for("segments", query)
        else:
            rows = self._rows_for("lemma", query)
        return [WordEntry.from_row(row) for row in rows]

    def find(self, word: str) -> Lookup | None:
        """Busca una palabra en cualquier forma regular (manjar, manjas, homi...)."""
        original = word.strip()
        if not original:
            return None
        query = _normalize(original)

        exact = self._lookup_exact(query, original)
        if exact:
            return exact

        for candidate, note in self._candidate_forms(query):
            entry = self._best(self._rows_for("lemma", candidate), original)
            if entry is None:
                continue
            analysis = _ANALYZER.analyze(query)
            return Lookup(entry=entry, query=original, note=note, analysis=analysis)

        return None

    def _lookup_exact(self, query: str, original: str) -> Lookup | None:
        rows: list[sqlite3.Row] = []
        if "." in query:
            rows = self._rows_for("segments", query)
        if not rows:
            rows = self._rows_for("lemma", query)
        entry = self._best(rows, original)
        if entry is None:
            return None
        analysis = _ANALYZER.analyze(entry.segments or entry.lemma)
        return Lookup(entry=entry, query=original, analysis=analysis)

    def _candidate_forms(self, query: str) -> list[tuple[str, str]]:
        """Genera candidatos de lema y una nota para cada transformación."""
        candidates: list[tuple[str, str]] = []
        seen: set[str] = set()

        def add(candidate: str, note: str) -> None:
            if candidate and candidate not in seen:
                seen.add(candidate)
                candidates.append((candidate, note))

        # Formas con puntos o guiones de la fuente.
        if "." in query:
            add(query.replace(".", ""), "forma sólida")
        if "-" in query:
            add(query.replace("-", ""), "compuesto sin guion")

        # Acusativo -n y plural -i.
        if query.endswith("n") and len(query) > 2:
            base = query[:-1]
            add(base, "forma acusativa")
            if base.endswith("i"):
                add(base[:-1] + "o", "plural acusativo")

        if query.endswith("i") and len(query) > 2:
            add(query[:-1] + "o", "plural")

        # Adverbio derivado de adjetivo.
        if query.endswith("e") and len(query) > 2:
            add(query[:-1] + "a", "adverbio derivado")

        # Verbos: perfecto -ab-, tiempos simples e infinitivos.
        perfect = _PERFECT_RE.match(query)
        if perfect:
            root = perfect.group(1)
            for ending in ("ar", "ir", "or"):
                add(root + ending, f"forma perfecta de {root + ending}")
        elif query.endswith(("as", "is", "os", "us", "ez")) and len(query) > 3:
            root = query[:-2]
            tense = {
                "as": "presente",
                "is": "pasado",
                "os": "futuro",
                "us": "condicional",
                "ez": "imperativo",
            }[query[-2:]]
            for ending in ("ar", "ir", "or"):
                add(root + ending, f"{tense} de {root + ending}")

        # Participios: vid.ant.a, manj.it.a, etc.
        participle = _PARTICIPLE_RE.match(query)
        if participle:
            root, kind, ending = participle.groups()
            names = {
                "ant": "participio activo presente",
                "int": "participio activo pasado",
                "ont": "participio activo futuro",
                "at": "participio pasivo presente",
                "it": "participio pasivo pasado",
                "ot": "participio pasivo futuro",
            }
            roots = [root]
            for suffix in ("ig", "es", "ad", "iz", "if", "esk"):
                if root.endswith(suffix) and len(root) > len(suffix) + 2:
                    roots.append(root[: -len(suffix)])
            for candidate_root in roots:
                for verb in ("ar", "ir", "or"):
                    if candidate_root == root:
                        add(candidate_root + verb, f"{names[kind]} de {candidate_root + verb}")
                    else:
                        add(candidate_root + verb, f"{names[kind]} de la raíz {candidate_root}")

        # Descomposición morfológica: raíz + afijos.
        analysis = _ANALYZER.analyze(query)
        if analysis.root and len(analysis.root) >= 2:
            root_rows = self._conn.execute(
                "SELECT * FROM words WHERE lower(root) = lower(?) LIMIT 20",
                (analysis.root,),
            ).fetchall()
            for row in root_rows:
                entry = WordEntry.from_row(row)
                add(entry.lemma, f"derivado de la raíz {analysis.root}")

        return candidates

    def lookup_en(self, term: str, *, limit: int = 10) -> list[WordEntry]:
        """Busca Ido por glosa inglesa; prioriza coincidencias exactas."""
        query = term.strip()
        if not query:
            return []

        rows: list[sqlite3.Row] = []
        try:
            rows = self._conn.execute(
                """
                SELECT w.*
                FROM words_fts f
                JOIN words w ON w.id = f.rowid
                WHERE words_fts MATCH ?
                LIMIT 80
                """,
                (query,),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []

        if not rows:
            rows = self._conn.execute(
                """
                SELECT * FROM words
                WHERE translation LIKE ? COLLATE NOCASE
                ORDER BY length(translation), lemma
                LIMIT 80
                """,
                (f"%{query}%",),
            ).fetchall()

        normalized = _normalize(query)
        scored: list[tuple[int, WordEntry]] = []
        for row in rows:
            entry = WordEntry.from_row(row)
            scored.append((self._english_score(normalized, entry), entry))

        scored.sort(key=lambda item: (-item[0], item[1].lemma.lower()))
        result: list[WordEntry] = []
        seen: set[tuple[str, int]] = set()
        for score, entry in scored:
            key = (entry.lemma.lower(), entry.proper)
            if key in seen:
                continue
            seen.add(key)
            result.append(entry)
            if len(result) >= limit:
                break
        return result

    @staticmethod
    def _english_score(term: str, entry: WordEntry) -> int:
        gloss = _normalize(entry.translation)
        first = re.split(r"[;,(.]", gloss, maxsplit=1)[0].strip()
        if first == term:
            return 100
        if first == "to " + term or first == "a " + term or first == "the " + term:
            return 98
        if first.startswith(term + " "):
            return 90
        if gloss.startswith(term + " ") or gloss.startswith(term + ",") or gloss.startswith(term + ";"):
            return 95
        if gloss.startswith(("to " + term, "a " + term, "the " + term)):
            return 94
        if re.search(r"\b" + re.escape(term) + r"\b", gloss):
            return 85
        term_words = set(term.split())
        gloss_words = set(re.findall(r"[a-z']+", gloss))
        if term_words and term_words <= gloss_words:
            return 75
        if term in gloss:
            return 50
        return 0

    def by_root(self, root: str) -> list[WordEntry]:
        rows = self._conn.execute(
            "SELECT * FROM words WHERE lower(root) = lower(?) ORDER BY lemma",
            (root,),
        ).fetchall()
        return [WordEntry.from_row(row) for row in rows]

    def list_derived(self, word: str) -> list[WordEntry]:
        rows = self._conn.execute(
            """
            SELECT child.*
            FROM words parent
            JOIN words child ON child.parent_id = parent.id
            WHERE lower(parent.lemma) = lower(?)
            ORDER BY child.lemma
            """,
            (word,),
        ).fetchall()
        return [WordEntry.from_row(row) for row in rows]

    def iter_words(self) -> Iterable[WordEntry]:
        rows = self._conn.execute("SELECT * FROM words ORDER BY lemma")
        for row in rows:
            yield WordEntry.from_row(row)

    def add_word(
        self,
        word: str,
        translation: str,
        *,
        root: str | None = None,
        pos: str | None = None,
        notes: str | None = None,
        parent_id: int | None = None,
    ) -> WordEntry:
        """Añade o actualiza una entrada de usuario."""
        lemma = word.strip()
        if not lemma or not translation.strip():
            raise ValueError("La palabra y la traducción son obligatorias")

        analysis = _ANALYZER.analyze(lemma)
        if root is None:
            root = analysis.root or None
        if pos is None:
            category = analysis.category.lower()
            if category.startswith("verb"):
                pos = "verb"
            elif category.startswith("noun"):
                pos = "noun"
            elif category.startswith("adjective"):
                pos = "adj"
            elif category.startswith("adverb"):
                pos = "adv"
            else:
                pos = "other"
        proper = int(lemma[:1].isupper())
        segments = lemma.lower() if "." in lemma else _segments_for(lemma.lower())

        existing = self._conn.execute(
            """
            SELECT id FROM words
            WHERE lower(lemma) = lower(?) AND pos = ? AND proper = ?
            LIMIT 1
            """,
            (lemma, pos, proper),
        ).fetchone()
        if existing:
            self._conn.execute(
                """
                UPDATE words
                SET root = ?, segments = ?, translation = ?, notes = ?,
                    source = 'user'
                WHERE id = ?
                """,
                (root, segments, translation.strip(), notes, existing["id"]),
            )
            word_id = existing["id"]
        else:
            cursor = self._conn.execute(
                """
                INSERT INTO words
                    (lemma, segments, root, pos, proper, translation,
                     parent_id, source, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'user', ?)
                """,
                (lemma, segments, root, pos, proper, translation.strip(), parent_id, notes),
            )
            word_id = cursor.lastrowid
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        return WordEntry.from_row(row)
