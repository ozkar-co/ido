#!/usr/bin/env python3
"""Herramienta personal y offline para estudiar Ido."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

from audit import audit_corpus
from db import DatabaseError, die_on_db_error
from dictionary import Dictionary
from display import format_entry, format_lookup, format_search_compact, format_search_results
from explain import explain
from importer import build_database
from paths import AUDIT_FAILURES_PATH
from report import format_analysis
from syntax import analyze_text


def _word(args: argparse.Namespace) -> int:
    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        if args.root:
            entries = db.by_root(args.root)
            if not entries:
                print(f"No hay palabras con la raíz: {args.root}", file=sys.stderr)
                return 1
            for entry in entries:
                print(format_entry(db, entry, include_family=False))
                print()
            return 0

        if not args.word:
            print("Error: indica una palabra o usa --root", file=sys.stderr)
            return 1

        if args.all:
            entries = db.lookup_all(args.word)
            if not entries:
                print(f"No encontrado: {args.word}", file=sys.stderr)
                return 1
            for entry in entries:
                print(format_entry(db, entry))
                print()
            return 0

        result = db.find(args.word)
        if result is None:
            print(f"No encontrado: {args.word}", file=sys.stderr)
            return 1
        print(
            format_lookup(
                db,
                result,
                include_family=not args.no_family,
                show_segments=args.segments,
            )
        )
        return 0
    finally:
        db.close()


def _en(args: argparse.Namespace) -> int:
    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)

    try:
        entries = db.lookup_en(args.term, limit=args.limit)
        if not entries:
            print(f"Sin resultados para: {args.term}", file=sys.stderr)
            return 1
        if args.compact:
            print(format_search_compact(entries))
        else:
            print(format_search_results(db, entries, show_segments=args.segments))
        return 0
    finally:
        db.close()


def _sentence_argument(parts: list[str]) -> str:
    return " ".join(parts).strip()


def _check(args: argparse.Namespace) -> int:
    text = _sentence_argument(args.sentence)
    results = analyze_text(text)
    for index, result in enumerate(results, start=1):
        if len(results) > 1:
            print(f"--- Oración {index} ---")
        print(format_analysis(result, show_tree=args.tree))
        if index != len(results):
            print()
    valid = all(result.valid for result in results)
    if args.strict and any(
        diagnostic.level in {"warning", "error"}
        for result in results
        for diagnostic in result.diagnostics
    ):
        valid = False
    return 0 if valid else 1


def _explain(args: argparse.Namespace) -> int:
    text = _sentence_argument(args.sentence)
    results = analyze_text(text)
    for index, result in enumerate(results, start=1):
        if len(results) > 1:
            print(f"--- Oración {index} ---")
        print(explain(result))
        if index != len(results):
            print()
    return 0 if all(result.valid for result in results) else 1


def _audit(args: argparse.Namespace) -> int:
    output = args.output if args.failures else None
    result = audit_corpus(limit=args.limit, every=args.every, output=output)
    pct = result.coverage
    print(f"Total:     {result.total}")
    print(f"Parseadas: {result.parsed}  ({pct:.1f}%)")
    print(f"Fallidas:  {result.failed}  ({100 - pct:.1f}%)")
    if result.clusters:
        print("Principales causas:")
        for message, count in result.clusters.most_common(8):
            print(f"  {count:4}  {message}")
    if output and result.failures:
        print(f"Fallos escritos en: {output}")
    if args.min is not None and pct < args.min:
        print(f"Error: cobertura {pct:.1f}% por debajo de {args.min:.1f}%", file=sys.stderr)
        return 1
    return 0


def _import(args: argparse.Namespace) -> int:
    try:
        stats = build_database(force=args.force)
    except (FileNotFoundError, sqlite3.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Importación completa")
    print(f"  Insertadas:     {stats['inserted']}")
    print(f"  Derivadas:      {stats['derived']}")
    print(f"  Nombres propios:{stats['proper']}")
    print(f"  Inválidas:      {stats['invalid']}")
    print(f"  Duplicadas:     {stats['duplicates']}")
    print(f"  Usuario:        {stats['users']}")
    print(f"  Total:          {stats['total']}")
    print(f"  TSV:            {stats['tsv']} filas")
    return 0


def _add(args: argparse.Namespace) -> int:
    try:
        db = Dictionary()
    except DatabaseError as exc:
        die_on_db_error(exc)
    try:
        entry = db.add_word(
            args.word,
            args.translation,
            root=args.root,
            pos=args.pos,
            notes=args.notes,
        )
        print("Guardada:")
        print(format_entry(db, entry))
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Herramienta offline para consultar y analizar Ido."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    word = sub.add_parser("word", help="Consultar una palabra Ido")
    word.add_argument("word", nargs="?", help="Palabra en cualquier forma (manjar, manjas...)")
    word.add_argument("--root", help="Listar las palabras de una raíz")
    word.add_argument("--all", action="store_true", help="Mostrar todas las entradas homónimas")
    word.add_argument("--no-family", action="store_true", help="No mostrar palabras de la misma raíz")
    word.add_argument("--segments", action="store_true", help="Mostrar la segmentación punteada (manj.ar)")
    word.set_defaults(func=_word)

    en = sub.add_parser("en", help="Buscar palabras Ido desde una glosa inglesa")
    en.add_argument("term", help="Palabra o expresión en inglés")
    en.add_argument("-n", "--limit", type=int, default=8, help="Máximo de resultados")
    en.add_argument("--compact", action="store_true", help="Una línea por resultado")
    en.add_argument("--segments", action="store_true", help="Mostrar segmentación punteada")
    en.set_defaults(func=_en)

    check = sub.add_parser("check", help="Verificar y analizar una frase")
    check.add_argument("sentence", nargs="+", help="Frase Ido")
    check.add_argument("--tree", action="store_true", help="Mostrar el árbol sintáctico")
    check.add_argument("--strict", action="store_true", help="Fallar también ante avisos")
    check.set_defaults(func=_check)

    explain_parser = sub.add_parser("explain", help="Explicar la gramática de una frase")
    explain_parser.add_argument("sentence", nargs="+", help="Frase Ido")
    explain_parser.set_defaults(func=_explain)

    audit = sub.add_parser("audit", help="Medir la cobertura del analizador sobre Tatoeba")
    audit.add_argument("-n", "--limit", type=int, default=None, help="Máximo de entradas")
    audit.add_argument("--every", type=int, default=1, help="Procesar una de cada N entradas")
    audit.add_argument("--failures", action="store_true", help="Guardar los fallos")
    audit.add_argument("-o", "--output", type=Path, default=AUDIT_FAILURES_PATH, help="Archivo de fallos")
    audit.add_argument("--min", type=float, default=None, help="Cobertura mínima exigida")
    audit.set_defaults(func=_audit)

    import_parser = sub.add_parser("import", help="Reconstruir el diccionario desde idan.txt")
    import_parser.add_argument("--force", action="store_true", help="Recrear la base")
    import_parser.set_defaults(func=_import)

    add = sub.add_parser("add", help="Añadir o actualizar una palabra")
    add.add_argument("word", help="Lema Ido")
    add.add_argument("translation", help="Glosa inglesa")
    add.add_argument("--root", help="Raíz morfológica")
    add.add_argument("--pos", help="noun, verb, adj, adv, other")
    add.add_argument("--notes", help="Nota opcional")
    add.set_defaults(func=_add)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        code = args.func(args)
    except KeyboardInterrupt:
        print("Interrumpido.", file=sys.stderr)
        code = 130
    sys.exit(code)


if __name__ == "__main__":
    main()
