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
            
    def parse_word_line(self, line: str) -> Optional[Dict]:
        """
        Parsear una línea del diccionario.
        
        Formato:
        palabra.tipo {tipo_palabra}  traducción; más info
        
        Palabras derivadas tienen espacios al inicio (normalmente 8).
        Obsoletas tienen bracket: [palabra (obs.) > nueva_palabra
        """
        # Saltar líneas vacías o separadores
        if not line.strip() or line.strip().startswith('---'):
            return None
            
        # Detectar si es derivada (comienza con 8 espacios)
        is_derived = line.startswith('        ')  # 8 espacios exactos
        clean_line = line.strip()
        
        if not clean_line:
            return None
            
        # Detectar obsoletas: [palabra (obs.)
        obsolete = False
        replaced_by = None
        if clean_line.startswith('['):
            obsolete = True
            # Buscar la palabra de reemplazo después de >
            if '>' in clean_line:
                parts = clean_line.split('>')
                replaced_by = parts[1].strip() if len(parts) > 1 else None
            clean_line = clean_line.lstrip('[')
            
        # Patrón: palabra.sufijo {tipo} (categoria) traducción
        # Usar doble espacio o tab como separador
        parts = re.split(r'\s\s+|\t', clean_line, 1)
        if len(parts) < 2:
            # Intentar con espacio simple si no hay doble
            parts = clean_line.split(' ', 1)
            if len(parts) < 2:
                return None
            
        word = parts[0].strip()
        rest = parts[1].strip()
        
        # Extraer tipo de palabra entre llaves: {tr}, {intr}, {adv.}, etc.
        word_type = None
        type_match = re.search(r'\{([^}]+)\}', rest)
        if type_match:
            word_type = type_match.group(1)
            rest = rest.replace(type_match.group(0), '').strip()
            
        # Extraer subcategoría entre paréntesis: (rel.), (anat.), etc.
        subcategory = None
        subcat_match = re.search(r'\(([^)]+)\)', rest)
        if subcat_match:
            potential_subcat = subcat_match.group(1)
            # Solo si parece abreviatura (termina en . o es una sola palabra)
            if '.' in potential_subcat or len(potential_subcat.split()) == 1:
                subcategory = potential_subcat
                rest = rest.replace(subcat_match.group(0), '').strip()
                
        # Extraer información gramatical entre corchetes: [de], [ad], etc.
        grammatical_info = None
        gram_match = re.search(r'\[([^\]]+)\]', rest)
        if gram_match:
            grammatical_info = gram_match.group(1)
            # No eliminar de rest, puede ser parte de la definición
            
        # Buscar antónimo: Ant: palabra
        antonym = None
        ant_match = re.search(r'Ant:\s*(\S+)', rest)
        if ant_match:
            antonym = ant_match.group(1)
            
        # El resto es la traducción/definición
        translation = rest.strip()
        
        # Categorizar palabra
        category = self._determine_category(word, word_type, subcategory)
        
        return {
            'word': word,
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
                           subcategory: Optional[str]) -> str:
        """Determinar categoría gramatical de la palabra."""
        
        # Basado en tipo de palabra
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
        if word.endswith('.o'):
            return 'NOUN'
        elif word.endswith('.a'):
            return 'ADJECTIVE'
        elif word.endswith('.e'):
            return 'ADVERB'
        elif word.endswith('.ar'):
            return 'VERB'
        elif word.startswith('-') or word.endswith('-'):
            if '{pref.}' in str(subcategory) or word.startswith('-'):
                return 'PREFIX'
            elif '{suf.}' in str(subcategory) or word.endswith('-'):
                return 'SUFFIX'
            return 'GRAMMAR'
            
        # Si tiene marcador gramatical
        if subcategory == 'gram.':
            return 'GRAMMAR'
            
        return 'PARTICLE'
        
    def import_abbreviations(self, lines: List[str], start_line: int):
        """Importar la sección de abreviaturas."""
        print(f"\nImportando abreviaturas desde línea {start_line}...")
        
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
                    self.stats['categories'] += 1
                except sqlite3.Error as e:
                    print(f"Error insertando categoría {abbr}: {e}")
                    
    def import_words(self, lines: List[str], end_line: int):
        """Importar palabras del diccionario."""
        print(f"\nImportando palabras (líneas 1-{end_line})...")
        
        current_parent_id = None
        line_num = 0
        
        for line in lines[:end_line]:
            line_num += 1
            
            # Saltar header y secciones especiales
            if line_num < 47:
                continue
                
            # Saltar títulos de letras
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
                    (word, word_type, translation, category, subcategory, 
                     grammatical_info, antonym, obsolete, replaced_by, 
                     parent_word_id, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    word_data['word'],
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
        
        # Buscar inicio de abreviaturas (línea ~14666)
        abbr_start = None
        for i, line in enumerate(lines):
            if 'Abreviuri en Ido' in line or 'Abbreviations in Ido' in line:
                abbr_start = i + 2  # Saltar título
                break
                
        if not abbr_start:
            print("No se encontró sección de abreviaturas, usando línea 14668")
            abbr_start = 14668
            
        # Importar
        self.import_words(lines, abbr_start - 10)  # Antes de abreviaturas
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
