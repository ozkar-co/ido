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
    """Motor de traducción Inglés → Ido."""

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
            # Buscar la palabra inglesa en la columna translation del diccionario
            # para encontrar la palabra Ido correspondiente
            ido_word = self.dictionary.get_ido_word(word)
            if ido_word:
                translated.append(ido_word)
                continue

            # Si no se encuentra, intentar análisis morfológico inverso
            # (buscar raíces inglesas conocidas - funcionalidad futura)
            translated.append(f"[{word}]")

        return " ".join(translated)

    # --------------------------------------------------------------------- #
    #  Traducción con análisis detallado
    # --------------------------------------------------------------------- #
    def translate_with_analysis(self, text: str) -> Dict:
        """Traduce texto del inglés al Ido y devuelve información detallada.

        El resultado tiene la siguiente estructura:
        {
            "original": "<texto original en inglés>",
            "words": [
                {
                    "english": "<palabra en inglés>",
                    "ido": "<palabra en Ido o None>",
                    "root": "<raíz morfológica Ido o None>",
                    "category": "<categoría Ido o None>",
                    "translation": "<traducción Ido encontrada o pista>"
                },
                ...
            ],
            "translation": "<texto traducido al Ido>"
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
            # Buscar palabra Ido correspondiente al inglés
            ido_word = self.dictionary.get_ido_word(word)

            # Si se encuentra, obtener información completa
            if ido_word:
                full_info = self.dictionary.search_word(ido_word)
                chosen = ido_word
                root = full_info.get('root') if full_info else None
                category = full_info.get('category') if full_info else None
            else:
                chosen = f"[{word}]"
                root = None
                category = None

            # Guardar información de la palabra
            result["words"].append({
                "english": word,
                "ido": ido_word,
                "root": root,
                "category": category,
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
