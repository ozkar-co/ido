"""Módulo de acceso al diccionario Ido-Inglés."""

import sqlite3
from typing import Optional, Dict, List


class Dictionary:
    """Interfaz para consultar el diccionario SQLite."""
    
    def __init__(self, db_path: str = "dictionary.db"):
        """Inicializar conexión al diccionario.
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
    
    def _get_connection(self):
        """Obtener conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def search_word(self, word: str) -> Optional[Dict]:
        """Buscar una palabra exacta (en Ido).
        
        Args:
            word: Palabra Ido a buscar
            
        Returns:
            Diccionario con información de la palabra o None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM words 
            WHERE word = ?
        """, (word,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_ido_word(self, english: str) -> Optional[str]:
        """Buscar la palabra Ido correspondiente a un término en inglés.
        
        Args:
            english: Palabra en inglés a buscar
            
        Returns:
            Palabra Ido o None si no se encuentra
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT word FROM words 
            WHERE translation = ?
            LIMIT 1
        """, (english,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['word']
        return None
    
    def search_by_root(self, root: str) -> List[Dict]:
        """Buscar palabras por raíz.
        
        Args:
            root: Raíz morfológica a buscar
            
        Returns:
            Lista de palabras con esa raíz
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM words 
            WHERE root = ?
            ORDER BY word
        """, (root,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_by_affix(self, affix: str) -> List[Dict]:
        """Buscar palabras que usan un afijo.
        
        Args:
            affix: Afijo a buscar
            
        Returns:
            Lista de palabras con ese afijo
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM words 
            WHERE affixes LIKE ?
            ORDER BY word
            LIMIT 20
        """, (f'%{affix}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_translation(self, word: str) -> Optional[str]:
        """Obtener traducción al inglés de una palabra Ido.
        
        Args:
            word: Palabra Ido a traducir
            
        Returns:
            Traducción al inglés o None si no se encuentra
        """
        result = self.search_word(word)
        if result:
            return result.get('translation')
        return None
    
    def get_all_translations(self, words: List[str]) -> Dict[str, str]:
        """Obtener traducciones para múltiples palabras Ido.
        
        Args:
            words: Lista de palabras Ido
            
        Returns:
            Diccionario palabra Ido -> traducción inglés
        """
        translations = {}
        for word in words:
            translation = self.get_translation(word)
            if translation:
                translations[word] = translation
        return translations
