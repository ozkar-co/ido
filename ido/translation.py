"""Motor de traducción para Ido.

Este módulo provee dos formas de traducir:
1. ``translate``: devuelve solo la cadena traducida (útil para scripts simples).
2. ``translate_with_analysis``: devuelve un diccionario con información detallada
   de cada palabra (raíz, categoría, traducción, etc.), similar a la salida del
   comando ``lookup`` del CLI.
"""

from typing import List, Dict, Optional
from ido.dictionary import Dictionary
from ido.morphology import MorphologyAnalyzer


class Translator:
    """Motor de traducción Ido ↔ Español."""

    def __init__(self, db_path: str = "dictionary.db"):
        """Inicializa el traductor con acceso al diccionario y al analizador morfológico."""
        self.dictionary = Dictionary(db_path)
        self.analyzer = MorphologyAnalyzer()

    # --------------------------------------------------------------------- #
    #  Traducción simple (solo texto)
    # --------------------------------------------------------------------- #
    def translate(self, text: str) -> str:
        """Traduce texto del inglés al Ido (versión simple).

        Args:
            text: Texto en inglés.

        Returns:
            Texto traducido al Ido.
        """
        words = self._tokenize(text)
        translated: List[str] = []

        for word in words:
            # Intentar búsqueda directa en el diccionario
            translation = self.dictionary.get_translation(word)
            if translation:
                translated.append(translation)
                continue

            # Si no hay traducción directa, intentar análisis morfológico
            analysis = self.analyzer.analyze(word)
            if analysis and analysis.root:
                # Usar la raíz como pista de traducción (entre corchetes)
                translated.append(f"[{analysis.root}]")
            else:
                # Fallback: devolver la palabra original entre corchetes
                translated.append(f"[{word}]")

        return " ".join(translated)

    # --------------------------------------------------------------------- #
    #  Traducción con análisis detallado
    # --------------------------------------------------------------------- #
    def translate_with_analysis(self, text: str) -> Dict:
        """Traduce texto del inglés al Ido y devuelve información detallada.

        El resultado tiene la siguiente estructura:
        {
            "original": "<texto original>",
            "words": [
                {
                    "word": "<palabra original>",
                    "root": "<raíz morfológica o None>",
                    "category": "<categoría o None>",
                    "translation": "<traducción encontrada o pista>"
                },
                ...
            ],
            "translation": "<texto traducido>"
        }

        Args:
            text: Texto en inglés.

        Returns:
            Diccionario con la traducción y el análisis de cada palabra.
        """
        words = self._tokenize(text)

        result: Dict = {
            "original": text,
            "words": [],
            "translation": ""
        }

        translated_parts: List[str] = []

        for word in words:
            # Búsqueda directa en el diccionario
            translation = self.dictionary.get_translation(word)

            # Análisis morfológico (si es necesario)
            analysis = self.analyzer.analyze(word)

            # Determinar la traducción a usar
            if translation:
                chosen = translation
            elif analysis and analysis.root:
                chosen = f"[{analysis.root}]"
            else:
                chosen = f"[{word}]"

            # Guardar información de la palabra
            result["words"].append({
                "word": word,
                "root": analysis.root if analysis else None,
                "category": analysis.category if analysis else None,
                "translation": chosen
            })

            translated_parts.append(chosen)

        result["translation"] = " ".join(translated_parts)
        return result

    # --------------------------------------------------------------------- #
    #  Utilidades internas
    # --------------------------------------------------------------------- #
    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza el texto en palabras minúsculas, eliminando puntuación."""
        import re
        # Mantener solo letras y apóstrofes (si aparecen)
        return re.findall(r"[a-zA-Z]+", text.lower())
