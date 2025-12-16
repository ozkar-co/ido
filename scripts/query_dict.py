#!/usr/bin/env python3
"""
Script de consulta del diccionario Ido-Inglés.

Uso:
    python scripts/query_dict.py palabra
    python scripts/query_dict.py --root raiz
    python scripts/query_dict.py --affix afijo
"""

import sqlite3
import sys
from typing import List, Dict


def format_word(word: Dict) -> str:
    """Formatear una palabra para mostrar."""
    parts = []
    
    # Palabra principal
    parts.append(f"\n{word['word']}")
    
    # Morfología
    if word['root']:
        morphology = f"  Morfología: raíz={word['root']}"
        if word['affixes']:
            morphology += f", afijos={word['affixes']}"
        if word['ending']:
            morphology += f", terminación={word['ending']}"
        parts.append(morphology)
    
    # Categoría
    cat_info = f"  Categoría: {word['category']}"
    if word['word_type']:
        cat_info += f" ({word['word_type']})"
    if word['subcategory']:
        cat_info += f" [{word['subcategory']}]"
    parts.append(cat_info)
    
    # Traducción
    parts.append(f"  Traducción: {word['translation']}")
    
    # Info adicional
    if word['grammatical_info']:
        parts.append(f"  Info gramatical: [{word['grammatical_info']}]")
    
    if word['antonym']:
        parts.append(f"  Antónimo: {word['antonym']}")
    
    if word['obsolete']:
        obsolete_info = "  ⚠️  OBSOLETA"
        if word['replaced_by']:
            obsolete_info += f" (usar: {word['replaced_by']})"
        parts.append(obsolete_info)
    
    return '\n'.join(parts)


def search_word(db_path: str, word: str):
    """Buscar una palabra exacta."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Buscar palabra principal
    cursor.execute("""
        SELECT * FROM words 
        WHERE word = ?
    """, (word,))
    
    main_word = cursor.fetchone()
    if not main_word:
        print(f"No se encontró la palabra: {word}")
        conn.close()
        return
    
    print(format_word(dict(main_word)))
    
    # Buscar derivadas
    cursor.execute("""
        SELECT * FROM words 
        WHERE parent_word_id = ?
        ORDER BY word
    """, (main_word['id'],))
    
    derived = cursor.fetchall()
    if derived:
        print("\n  Palabras derivadas:")
        for d in derived:
            print(f"    {d['word']} - {d['translation']}")
    
    conn.close()


def search_by_root(db_path: str, root: str):
    """Buscar palabras por raíz."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM words 
        WHERE root = ?
        ORDER BY word
    """, (root,))
    
    words = cursor.fetchall()
    if not words:
        print(f"No se encontraron palabras con raíz: {root}")
        conn.close()
        return
    
    print(f"\nPalabras con raíz '{root}': {len(words)}")
    for word in words:
        print(f"\n  {word['word']}")
        if word['affixes']:
            print(f"    Afijos: {word['affixes']}")
        if word['ending']:
            print(f"    Terminación: {word['ending']}")
        print(f"    Traducción: {word['translation'][:60]}...")
    
    conn.close()


def search_by_affix(db_path: str, affix: str):
    """Buscar palabras que usan un afijo."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM words 
        WHERE affixes LIKE ?
        ORDER BY word
        LIMIT 20
    """, (f'%{affix}%',))
    
    words = cursor.fetchall()
    if not words:
        print(f"No se encontraron palabras con afijo: {affix}")
        conn.close()
        return
    
    print(f"\nPrimeras 20 palabras con afijo '{affix}':")
    for word in words:
        print(f"  {word['word']:<20} {word['root']}.{word['affixes']}.{word['ending'] or '':<5} - {word['translation'][:40]}")
    
    conn.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Consultar diccionario Ido-Inglés')
    parser.add_argument('word', nargs='?', help='Palabra a buscar')
    parser.add_argument('--db', default='dictionary.db', help='Base de datos')
    parser.add_argument('--root', help='Buscar por raíz')
    parser.add_argument('--affix', help='Buscar por afijo')
    
    args = parser.parse_args()
    
    if args.root:
        search_by_root(args.db, args.root)
    elif args.affix:
        search_by_affix(args.db, args.affix)
    elif args.word:
        search_word(args.db, args.word)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
