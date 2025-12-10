#!/usr/bin/env python3
"""
Script para importar el diccionario Ido-Inglés (idan.txt) a la base de datos SQLite.

Uso:
    python scripts/import_idan.py [--db database.db] [--dict data/idan.txt]
"""

import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple


def parse_word_parts(word: str) -> Dict[str, str]:
    """
    Parsear una palabra en sus partes: raíz, afijos, terminación.
    
    Ejemplo: abad.in.o -> raíz='abad', afijos=['in'], terminación='o'
    """
    parts = word.split('.')
    
    if len(parts) == 1:
        # Palabra sin puntos (puede ser partícula, conjunción, etc.)
        return {'root': word, 'affixes': [], 'ending': ''}
    
    # La raíz es la primera parte
    root = parts[0]
    
    # La terminación es la última parte (si es una sola letra generalmente)
    ending = ''
    affixes = []
    
    if len(parts[-1]) <= 2 and parts[-1] in ['o', 'a', 'e', 'i', 'ar', 'ir', 'as', 'is', 'os', 'us']:
        ending = parts[-1]
        affixes = parts[1:-1]
    else:
        # Toda la palabra excepto la raíz son afijos
        affixes = parts[1:]
    
    return {
        'root': root,
        'affixes': affixes,
        'ending': ending
    }


class IdanImporter:
    """Importador del diccionario Ido-Inglés."""
    
    def __init__(self, db_path: str = "dictionary.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.stats = {
            'words': 0,
            'derived': 0,
            'categories': 0,
            'obsolete': 0,
            'skipped': 0,
            'errors': 0
        }
        
    def connect(self):
        """Conectar a la base de datos."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Cerrar conexión."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            
    def is_valid_word_line(self, line: str) -> bool:
        """
        Verificar si una línea es una palabra válida.
        
        Una línea válida debe:
        - Empezar con una palabra (o con espacios para derivadas)
        - Tener al menos un espacio/tab seguido de definición
        - No ser una continuación de línea anterior (que no empieza con palabra)
        """
        stripped = line.strip()
        
        # Líneas vacías o separadores
        if not stripped or stripped.startswith('---'):
            return False
        
        # Si empieza con espacios, es derivada - válida
        if line.startswith('        '):
            return True
            
        # Verificar que empiece con una palabra válida
        # Palabras válidas: pueden empezar con letra, -, [, o mayúscula
        if not (stripped[0].isalpha() or stripped[0] in ['-', '[']):
            return False
            
        # Debe tener al menos 2 espacios o un tab como separador
        if not re.search(r'\s\s+|\t', line):
            return False
            
        return True
            
    def parse_word_line(self, line: str) -> Optional[Dict]:
        """Parsear una línea del diccionario."""
        
        if not self.is_valid_word_line(line):
            return None
            
        # Detectar si es derivada (8 espacios exactos al inicio)
        is_derived = line.startswith('        ')
        clean_line = line.strip()
        
        # Detectar obsoletas: [palabra (obs.) > nueva_palabra
        obsolete = False
        replaced_by = None
        if clean_line.startswith('['):
            obsolete = True
            if '>' in clean_line:
                parts = clean_line.split('>')
                replaced_by = parts[1].strip() if len(parts) > 1 else None
            clean_line = clean_line.lstrip('[')
            
        # Separar palabra de definición usando doble espacio o tab
        parts = re.split(r'\s\s+|\t', clean_line, 1)
        if len(parts) < 2:
            return None
            
        word_part = parts[0].strip()
        rest = parts[1].strip()
        
        # PRIMERO: extraer metadatos que vienen después de la palabra
        # Extraer información gramatical: "palabra [info]"
        grammatical_info = None
        word_gram_match = re.search(r'\s*\[([^\]]+)\]', word_part)
        if word_gram_match:
            grammatical_info = word_gram_match.group(1)
            word_part = word_part.replace(word_gram_match.group(0), '').strip()
        
        # Extraer tipo de palabra: "palabra {tipo}"
        word_type = None
        word_type_match = re.search(r'\s*\{([^}]+)\}', word_part)
        if word_type_match:
            word_type = word_type_match.group(1)
            word_part = word_part.replace(word_type_match.group(0), '').strip()
        
        # Extraer subcategoría si está en la palabra: "palabra (cat.)"
        subcategory = None
        word_subcat_match = re.search(r'\s*\(([^)]+?\.)\)', word_part)
        if word_subcat_match:
            subcategory = word_subcat_match.group(1)
            word_part = word_part.replace(word_subcat_match.group(0), '').strip()
        
        # Ahora word_part debe ser solo la palabra limpia
        word = word_part
        
        # Extraer tipo de palabra de rest si no se encontró antes
        if not word_type:
            type_match = re.search(r'\{([^}]+)\}', rest)
            if type_match:
                word_type = type_match.group(1)
                rest = rest.replace(type_match.group(0), '').strip()
            
        # Extraer subcategoría entre paréntesis si no se encontró antes: (rel.), (anat.), etc.
        # Solo la primera aparición
        if not subcategory:
            subcat_match = re.search(r'\(([^)]+?\.)\)', rest)
            if subcat_match:
                subcategory = subcat_match.group(1)
                rest = rest.replace(subcat_match.group(0), '', 1).strip()
        
        # Extraer información gramatical entre corchetes si no se encontró antes: [de], [ad], etc.
        if not grammatical_info:
            gram_match = re.search(r'\[([^\]]+)\]', rest)
            if gram_match:
                # Solo si es corto (probablemente gramatical, no parte de definición)
                if len(gram_match.group(1)) <= 20:
                    grammatical_info = gram_match.group(1)
                    rest = rest.replace(gram_match.group(0), '').strip()
                    
        # Buscar antónimo: "Ant: palabra" al final de la línea
        antonym = None
        ant_match = re.search(r'\.\s+Ant:\s*(\S+)\s*$', rest)
        if ant_match:
            antonym = ant_match.group(1)
            rest = rest[:ant_match.start()] + '.'  # Remover el antónimo de la definición
            
        # El resto es la traducción/definición
        translation = rest.strip()
        
        # Parsear partes de la palabra
        word_parts = parse_word_parts(word)
        
        # Categorizar palabra
        category = self._determine_category(word, word_type, word_parts['ending'])
        
        return {
            'word': word,
            'root': word_parts['root'],
            'affixes': '.'.join(word_parts['affixes']) if word_parts['affixes'] else None,
            'ending': word_parts['ending'] if word_parts['ending'] else None,
            'word_type': word_type,
            'translation': translation,
            'category': category,
            'subcategory': subcategory,
            'grammatical_info': grammatical_info,
            'antonym': antonym,
            'obsolete': obsolete,
            'replaced_by': replaced_by,
            'is_derived': is_derived
        }
        
    def _determine_category(self, word: str, word_type: Optional[str], 
                           ending: Optional[str]) -> str:
        """Determinar categoría gramatical de la palabra."""
        
        # Basado en tipo de palabra explícito
        if word_type:
            if word_type in ['tr', 'intr', 'tr/intr', 'imp']:
                return 'VERB'
            elif word_type == 'adv.':
                return 'ADVERB'
            elif word_type == 'prep.':
                return 'PREPOSITION'
            elif word_type == 'konj.':
                return 'CONJUNCTION'
            elif word_type == 'interj.':
                return 'INTERJECTION'
            elif word_type == 'pref.':
                return 'PREFIX'
            elif word_type == 'suf.':
                return 'SUFFIX'
                
        # Basado en terminación
        if ending:
            if ending == 'o':
                return 'NOUN'
            elif ending == 'a':
                return 'ADJECTIVE'
            elif ending == 'e':
                return 'ADVERB'
            elif ending in ['ar', 'ir']:
                return 'VERB'
        
        # Basado en estructura
        if word.startswith('-') and word.endswith('-'):
            return 'GRAMMAR'
        elif word.startswith('-'):
            return 'SUFFIX'
        elif word.endswith('-'):
            return 'PREFIX'
            
        return 'PARTICLE'
        
    def import_abbreviations(self, lines: List[str], start_line: int):
        """Importar la sección de abreviaturas."""
        print(f"\nImportando abreviaturas desde línea {start_line}...")
        
        count = 0
        for line in lines[start_line:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Formato: abbr. - nombre_ido - nombre_ingles
            parts = line.split(' - ')
            if len(parts) >= 3:
                abbr = parts[0].strip()
                ido_name = parts[1].strip()
                english_name = parts[2].strip()
                
                # Determinar tipo
                cat_type = 'FIELD'
                if abbr in ['tr', 'intr', 'imp', 'adv.', 'prep.', 'konj.', 
                           'interj.', 'pref.', 'suf.', 'gram.']:
                    cat_type = 'GRAMMAR'
                    
                try:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO categories 
                        (abbreviation, ido_name, english_name, category_type)
                        VALUES (?, ?, ?, ?)
                    """, (abbr, ido_name, english_name, cat_type))
                    count += 1
                except sqlite3.Error as e:
                    print(f"Error insertando categoría {abbr}: {e}")
                    
        self.stats['categories'] = count
        print(f"  Importadas {count} categorías")
                    
    def import_words(self, lines: List[str], end_line: int):
        """Importar palabras del diccionario."""
        print(f"\nImportando palabras (líneas 1-{end_line})...")
        
        current_parent_id = None
        line_num = 0
        
        for line in lines[:end_line]:
            line_num += 1
            
            # Saltar header
            if line_num < 47:
                continue
                
            # Saltar títulos de letras (líneas que solo tienen una letra)
            if re.match(r'^\s*[A-Z]\s*$', line):
                continue
                
            word_data = self.parse_word_line(line)
            if not word_data:
                continue
                
            # Si es derivada, usar el parent_id del último registro principal
            parent_id = current_parent_id if word_data['is_derived'] else None
            
            try:
                self.cursor.execute("""
                    INSERT OR REPLACE INTO words 
                    (word, root, affixes, ending, word_type, translation, category, 
                     subcategory, grammatical_info, antonym, obsolete, replaced_by, 
                     parent_word_id, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    word_data['word'],
                    word_data['root'],
                    word_data['affixes'],
                    word_data['ending'],
                    word_data['word_type'],
                    word_data['translation'],
                    word_data['category'],
                    word_data['subcategory'],
                    word_data['grammatical_info'],
                    word_data['antonym'],
                    1 if word_data['obsolete'] else 0,
                    word_data['replaced_by'],
                    parent_id,
                    'idan.txt'
                ))
                
                # Si no es derivada, guardar su ID como posible parent
                if not word_data['is_derived']:
                    current_parent_id = self.cursor.lastrowid
                    self.stats['words'] += 1
                else:
                    self.stats['derived'] += 1
                    
                if word_data['obsolete']:
                    self.stats['obsolete'] += 1
                    
            except sqlite3.Error as e:
                print(f"Error en línea {line_num} ({word_data['word']}): {e}")
                self.stats['errors'] += 1
                
            # Commit cada 1000 palabras
            if (self.stats['words'] + self.stats['derived']) % 1000 == 0:
                self.conn.commit()
                print(f"  Procesadas {self.stats['words'] + self.stats['derived']} palabras...")
                
    def run(self, dict_file: str):
        """Ejecutar importación completa."""
        print(f"Importando diccionario desde {dict_file}...")
        print(f"Base de datos: {self.db_path}")
        
        # Detectar encoding del archivo
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        lines = None
        
        for encoding in encodings:
            try:
                with open(dict_file, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                print(f"Archivo leído con encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
                
        if lines is None:
            raise ValueError(f"No se pudo leer el archivo con ningún encoding conocido")
            
        print(f"Total de líneas: {len(lines)}")
        
        # Buscar inicio de abreviaturas
        abbr_start = None
        for i, line in enumerate(lines):
            if 'Abreviuri en Ido' in line or 'Abbreviations in Ido' in line:
                abbr_start = i + 2
                break
                
        if not abbr_start:
            abbr_start = 14668
            
        # Importar
        self.import_words(lines, abbr_start - 10)
        self.import_abbreviations(lines, abbr_start)
        
        self.conn.commit()
        
        # Estadísticas
        print("\n" + "="*50)
        print("IMPORTACIÓN COMPLETADA")
        print("="*50)
        print(f"Palabras principales: {self.stats['words']}")
        print(f"Palabras derivadas: {self.stats['derived']}")
        print(f"Categorías: {self.stats['categories']}")
        print(f"Obsoletas: {self.stats['obsolete']}")
        print(f"Errores: {self.stats['errors']}")
        print(f"Total: {self.stats['words'] + self.stats['derived']}")
        

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importar diccionario Ido-Inglés')
    parser.add_argument('--db', default='dictionary.db', 
                       help='Ruta a la base de datos SQLite')
    parser.add_argument('--dict', default='data/idan.txt',
                       help='Ruta al archivo del diccionario')
    
    args = parser.parse_args()
    
    # Verificar que existe el archivo
    if not Path(args.dict).exists():
        print(f"Error: No se encuentra el archivo {args.dict}")
        sys.exit(1)
        
    # Crear esquema si no existe
    schema_file = Path('scripts/001_create_schema.sql')
    if schema_file.exists():
        print(f"Creando esquema desde {schema_file}...")
        conn = sqlite3.connect(args.db)
        with open(schema_file, 'r') as f:
            conn.executescript(f.read())
        conn.close()
        print("Esquema creado.")
    
    # Importar
    importer = IdanImporter(args.db)
    importer.connect()
    
    try:
        importer.run(args.dict)
    finally:
        importer.close()
        
    print(f"\nBase de datos guardada en: {args.db}")


if __name__ == '__main__':
    main()
