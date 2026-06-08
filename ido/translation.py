"""Motor de traducción para el idioma Ido."""

from ido.dictionary import Dictionary
from ido.morphology import MorphologyAnalyzer
from ido.parser import IdoParser
from typing import List, Dict


class Translator:
    """Motor de traducción Ido -> Español."""
    
    def __init__(self, db_path: str = "dictionary.db"):
        """Inicializar el traductor.
        
        Args:
            db_path: Ruta al diccionario
        """
        self.dictionary = Dictionary(db_path)
        self.analyzer = MorphologyAnalyzer()
        self.parser = IdoParser()
    
    def translate(self, text: str) -> str:
        """Traducir texto del Ido al español.
        
        Args:
            text: Texto en Ido
            
        Returns:
            Texto traducido al español
        """
        # Tokenizar y limpiar
        words = self._tokenize(text)
        
        # Obtener traducciones
        translations = []
        for word in words:
            # Primero intentar búsqueda directa
            translation = self.dictionary.get_translation(word)
            
            if not translation:
                # Si no se encuentra, intentar análisis morfológico
                analysis = self.analyzer.analyze(word)
                # Usar la raíz como fallback
                if analysis.root:
                    translation = f"[{analysis.root}]"
                else:
                    translation = f"[{word}]"
            
            translations.append(translation)
        
        return " ".join(translations)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenizar texto en palabras.
        
        Args:
            text: Texto a tokenizar
            
        Returns:
            Lista de palabras
        """
        # Eliminar puntuación y dividir
        import re
        # Mantener palabras con puntos (morfemas)
        tokens = re.findall(r'[a-z.]+', text.lower())
        return tokens
    
    def translate_with_analysis(self, text: str) -> Dict:
        """Traducir con análisis morfológico detallado.
        
        Args:
            text: Texto en Ido
            
        Returns:
            Diccionario con traducción y análisis
        """
        words = self._tokenize(text)
        
        result = {
            "original": text,
            "words": [],
            "translation": ""
        }
        
        translations = []
        for word in words:
            analysis = self.analyzer.analyze(word)
            translation = self.dictionary.get_translation(word) or f"[{analysis.root}]"
            
            result["words"].append({
                "word": word,
                "root": analysis.root,
                "category": analysis.category,
                "translation": translation
            })
            translations.append(translation)
        
        result["translation"] = " ".join(translations)
        return result
