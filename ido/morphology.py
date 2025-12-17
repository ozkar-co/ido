"""
Analizador morfológico para Ido.

Descompone palabras en sus partes morfológicas siguiendo las reglas de Ido:
- Terminaciones verbales: -ar, -ir, -or (infinitivos), -as, -is, -os, -us, -ez
- Terminaciones gramaticales: -o (singular), -i (plural), -a (adj), -e (adv)
- Participios: -ant-, -int-, -ont-, -at-, -it-, -ot-
- Prefijos: arki-, bo-, centi-, des-, dis-, etc.
- Sufijos: -ach-, -ad-, -aj-, -al-, etc.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class MorphologicalAnalysis:
    """Resultado del análisis morfológico de una palabra."""
    
    original: str
    root: str
    prefixes: List[str]
    suffixes: List[str]
    ending: str
    category: str
    subcategories: List[str]
    
    def __str__(self) -> str:
        parts = []
        if self.prefixes:
            parts.append(f"Prefixes: {'-'.join(self.prefixes)}")
        parts.append(f"Root: {self.root}")
        if self.suffixes:
            parts.append(f"Suffixes: {'-'.join(self.suffixes)}")
        if self.ending:
            parts.append(f"Ending: {self.ending}")
        parts.append(f"Category: {self.category}")
        if self.subcategories:
            parts.append(f"Subcategories: {', '.join(self.subcategories)}")
        return f"{self.original} → {' | '.join(parts)}"


class MorphologyAnalyzer:
    """Analizador morfológico para Ido."""
    
    # Terminaciones verbales
    VERB_INFINITIVES = ['ar', 'ir', 'or']  # present, past, future
    VERB_TENSES = ['as', 'is', 'os', 'us']  # present, past, future, conditional
    VERB_IMPERATIVE = ['ez']
    
    # Terminaciones gramaticales
    NOUN_ENDINGS = ['o', 'i']  # singular, plural
    ADJECTIVE_ENDING = ['a']
    ADVERB_ENDING = ['e']
    
    # Participios (infijos)
    PARTICIPLES = {
        'ant': 'present active participle',
        'int': 'past active participle',
        'ont': 'future active participle',
        'at': 'present passive participle',
        'it': 'past passive participle',
        'ot': 'future passive participle',
    }
    
    # Prefijos
    PREFIXES = {
        'arki': 'pre-eminence',
        'bo': 'related by marriage',
        'centi': 'hundredth part',
        'des': 'contrary',
        'dis': 'separation',
        'equi': 'equality',
        'ex': 'former',
        'ge': 'both sexes together',
        'hiper': 'over-, excessively, hyper-',
        'hipo': 'under, insufficiently, hypo-',
        'ho': 'in which one is living',
        'mi': 'half',
        'mis': 'wrongly',
        'ne': 'negation',
        'par': 'completely',
        'para': 'warding off',
        'poli': 'many, poly-',
        'pre': 'before',
        'prim': 'primitive',
        'retro': 'back',
        'ri': 'again',
        'sen': 'without',
    }
    
    # Sufijos
    SUFFIXES = {
        'ach': 'pejorative',
        'ad': 'frequency, repetition',
        'aj': 'material substance',
        'al': 'relating to',
        'an': 'member of',
        'ar': 'collection',
        'ari': 'receiver',
        'atr': 'like',
        'e': 'coloured',
        'ebl': 'possibility',
        'ed': 'quantity held by',
        'eg': 'largeness',
        'em': 'inclined to',
        'end': 'something to be done',
        'er': 'amateur',
        'eri': 'establishment',
        'es': 'to be',
        'esk': 'to begin to',
        'estr': 'head, chief',
        'et': 'smallness',
        'ey': 'place for',
        'i': 'domain',
        'id': 'offspring',
        'ier': 'holder',
        'if': 'to produce',
        'ig': 'to cause to be or do',
        'ik': 'sick',
        'il': 'tool',
        'in': 'feminine',
        'ind': 'worthy of',
        'ism': 'system, doctrine',
        'ist': 'professional, adherent',
        'iv': 'that can',
        'ivor': 'indicates what something eats',
        'iz': 'to supply or cover with',
        'oid': 'having the form of',
        'oz': 'full of',
        'ul': 'masculine',
        'um': 'all-purpose suffix',
        'ur': 'result of action',
        'yun': 'young of',
        'uy': 'container',
        'ab': 'perfect tense marker',
    }
    
    # Sufijos numéricos
    NUMERAL_SUFFIXES = {
        'esm': 'ordinals',
        'im': 'fraction',
        'op': 'distributive',
        'opl': 'multiplying',
    }
    
    def __init__(self):
        """Inicializar el analizador morfológico."""
        # Compilar patrones para eficiencia
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compilar expresiones regulares para el análisis."""
        # Patrón para palabras con puntos (abad.ey.o)
        self.dotted_pattern = re.compile(r'^([a-z]+(?:\.[a-z]+)*\.?[a-z]*)$', re.IGNORECASE)
    
    def analyze(self, word: str) -> MorphologicalAnalysis:
        """
        Analizar morfológicamente una palabra.
        
        Args:
            word: Palabra a analizar
            
        Returns:
            MorphologicalAnalysis con los componentes identificados
        """
        word = word.strip().lower()
        
        # Si la palabra tiene puntos, usar análisis punto por punto
        if '.' in word:
            return self._analyze_dotted(word)
        else:
            return self._analyze_solid(word)
    
    def _analyze_dotted(self, word: str) -> MorphologicalAnalysis:
        """
        Analizar una palabra con puntos (ej: abad.ey.o).
        
        En Ido, los puntos separan morfemas:
        - raíz.sufijo.terminación (ej: abad.ey.o = abbey)
        - raíz.sufijo.sufijo.terminación (ej: bel.es.ant.a = being beautiful)
        - prefijo.raíz.sufijo.terminación (ej: ne.bel.a = not beautiful)
        
        La primera parte puede ser:
        - Una raíz
        - Un prefijo (si es conocido y hay más partes después)
        """
        parts = word.split('.')
        
        if len(parts) == 1:
            return self._analyze_solid(word)
        
        # Identificar si la primera parte es un prefijo conocido
        prefixes = []
        root_index = 0
        
        # Si la primera parte es un prefijo conocido y hay más de 2 partes
        if parts[0] in self.PREFIXES and len(parts) > 1:
            prefixes.append(parts[0])
            root_index = 1
        
        # La raíz es la siguiente parte después de los prefijos
        root = parts[root_index] if root_index < len(parts) else parts[0]
        
        # La terminación es la última parte (si es una terminación válida)
        ending = ''
        suffixes = []
        
        all_endings = (self.VERB_INFINITIVES + self.VERB_TENSES + 
                      self.VERB_IMPERATIVE + self.NOUN_ENDINGS + 
                      self.ADJECTIVE_ENDING + self.ADVERB_ENDING)
        
        last_part = parts[-1]
        
        if last_part in all_endings:
            ending = last_part
            # Los sufijos son todo entre la raíz y la terminación
            suffixes = parts[root_index + 1:-1]
        else:
            # No hay terminación clara, todo después de la raíz son sufijos
            suffixes = parts[root_index + 1:]
        
        # Determinar categoría
        category = self._determine_category(ending, suffixes)
        
        # Identificar subcategorías (participios, etc.)
        subcategories = []
        for suffix in suffixes:
            if suffix in self.PARTICIPLES:
                subcategories.append(self.PARTICIPLES[suffix])
            elif suffix in self.SUFFIXES:
                subcategories.append(self.SUFFIXES[suffix])
        
        return MorphologicalAnalysis(
            original=word,
            root=root,
            prefixes=prefixes,
            suffixes=suffixes,
            ending=ending,
            category=category,
            subcategories=subcategories
        )
    
    def _analyze_solid(self, word: str) -> MorphologicalAnalysis:
        """
        Analizar una palabra sin puntos.
        
        Intenta identificar prefijos, sufijos y terminaciones dentro de la palabra.
        """
        remaining = word
        prefixes = []
        
        # Buscar prefijos
        for prefix in sorted(self.PREFIXES.keys(), key=len, reverse=True):
            if remaining.startswith(prefix):
                prefixes.append(prefix)
                remaining = remaining[len(prefix):]
                break
        
        # Buscar terminación al final
        ending = ''
        all_endings = (self.VERB_INFINITIVES + self.VERB_TENSES + 
                      self.VERB_IMPERATIVE + self.NOUN_ENDINGS + 
                      self.ADJECTIVE_ENDING + self.ADVERB_ENDING)
        
        for end in sorted(all_endings, key=len, reverse=True):
            if remaining.endswith(end) and len(remaining) > len(end):
                ending = end
                remaining = remaining[:-len(end)]
                break
        
        # Buscar sufijos conocidos en lo que queda
        suffixes = []
        found_suffix = True
        while found_suffix and len(remaining) > 2:
            found_suffix = False
            for suffix in sorted(self.SUFFIXES.keys(), key=len, reverse=True):
                if remaining.endswith(suffix) and len(remaining) > len(suffix):
                    suffixes.insert(0, suffix)
                    remaining = remaining[:-len(suffix)]
                    found_suffix = True
                    break
        
        root = remaining if remaining else word
        category = self._determine_category(ending, suffixes)
        
        subcategories = []
        for suffix in suffixes:
            if suffix in self.PARTICIPLES:
                subcategories.append(self.PARTICIPLES[suffix])
            elif suffix in self.SUFFIXES:
                subcategories.append(self.SUFFIXES[suffix])
        
        return MorphologicalAnalysis(
            original=word,
            root=root,
            prefixes=prefixes,
            suffixes=suffixes,
            ending=ending,
            category=category,
            subcategories=subcategories
        )
    
    def _determine_category(self, ending: str, suffixes: List[str]) -> str:
        """Determinar la categoría gramatical basada en terminación y sufijos."""
        if ending in self.VERB_INFINITIVES:
            return 'VERB (infinitive)'
        elif ending in self.VERB_TENSES:
            tense_map = {'as': 'present', 'is': 'past', 'os': 'future', 'us': 'conditional'}
            return f'VERB ({tense_map.get(ending, "unknown")})'
        elif ending in self.VERB_IMPERATIVE:
            return 'VERB (imperative)'
        elif ending == 'o':
            return 'NOUN (singular)'
        elif ending == 'i':
            return 'NOUN (plural)'
        elif ending == 'a':
            # Podría ser adjetivo o participio
            if any(s in self.PARTICIPLES for s in suffixes):
                return 'PARTICIPLE (adjective form)'
            return 'ADJECTIVE'
        elif ending == 'e':
            if any(s in self.PARTICIPLES for s in suffixes):
                return 'PARTICIPLE (adverb form)'
            return 'ADVERB'
        else:
            return 'UNKNOWN'
    
    def apply_derivation(self, word: str, from_type: str, to_type: str) -> Optional[str]:
        """
        Aplicar regla de derivación directa.
        
        Reglas:
        - Verb to noun: -ar → -o (brosar → broso)
        - Adjective to noun: -a → -o (bona → bono)
        - Noun to adjective: -o → -a (oro → ora)
        - Adjective to adverb: -a → -e (bela → bele)
        
        Args:
            word: Palabra base
            from_type: Tipo de origen ('verb', 'adjective', 'noun', 'adverb')
            to_type: Tipo de destino
            
        Returns:
            Palabra derivada o None si la derivación no es válida
        """
        word = word.strip().lower()
        
        derivations = {
            ('verb', 'noun'): ('ar', 'o'),
            ('adjective', 'noun'): ('a', 'o'),
            ('noun', 'adjective'): ('o', 'a'),
            ('adjective', 'adverb'): ('a', 'e'),
        }
        
        key = (from_type.lower(), to_type.lower())
        if key not in derivations:
            return None
        
        from_ending, to_ending = derivations[key]
        
        # Si la palabra termina con la terminación esperada
        if word.endswith(from_ending):
            # Remover terminación antigua y agregar nueva
            base = word[:-len(from_ending)]
            return base + to_ending
        elif '.' in word:
            # Manejar forma con puntos
            parts = word.split('.')
            if parts[-1] == from_ending:
                parts[-1] = to_ending
                return '.'.join(parts)
        
        return None
    
    def get_verb_forms(self, root: str) -> Dict[str, str]:
        """
        Generar todas las formas verbales de una raíz.
        
        Args:
            root: Raíz verbal (sin terminación)
            
        Returns:
            Diccionario con todas las formas verbales
        """
        forms = {
            # Infinitivos
            'present_infinitive': f"{root}ar",
            'past_infinitive': f"{root}ir",
            'future_infinitive': f"{root}or",
            # Tiempos
            'present': f"{root}as",
            'past': f"{root}is",
            'future': f"{root}os",
            'conditional': f"{root}us",
            # Imperativo
            'imperative': f"{root}ez",
        }
        return forms
    
    def get_participle_forms(self, root: str, ending: str = 'a') -> Dict[str, str]:
        """
        Generar todas las formas participiales.
        
        Args:
            root: Raíz verbal
            ending: Terminación (a=adjective, e=adverb, o/i=noun)
            
        Returns:
            Diccionario con todas las formas participiales
        """
        forms = {
            'present_active': f"{root}.ant.{ending}",
            'past_active': f"{root}.int.{ending}",
            'future_active': f"{root}.ont.{ending}",
            'present_passive': f"{root}.at.{ending}",
            'past_passive': f"{root}.it.{ending}",
            'future_passive': f"{root}.ot.{ending}",
        }
        return forms
