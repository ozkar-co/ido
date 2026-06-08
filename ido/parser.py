"""Parser sintáctico para el idioma Ido usando Lark."""

from lark import Lark, Tree
from pathlib import Path


class IdoParser:
    """Parser sintáctico basado en gramática EBNF."""
    
    def __init__(self):
        """Inicializar el parser con la gramática Ido."""
        grammar_path = Path(__file__).parent / "grammar.lark"
        
        if grammar_path.exists():
            self.grammar = grammar_path.read_text()
        else:
            # Gramática por defecto si no existe el archivo
            self.grammar = self._default_grammar()
        
        self.parser = Lark(self.grammar, start='sentence', parser='lalr')
    
    def _default_grammar(self) -> str:
        """Gramática EBNF por defecto para Ido.
        
        Returns:
            String con la gramática Lark
        """
        return """
        start: sentence+
        
        sentence: noun_phrase verb_phrase "."
                | noun_phrase verb_phrase "?"
        
        noun_phrase: [ARTICLE] [adjective] noun
                   | [ARTICLE] [adjective] noun prepositional_phrase
        
        verb_phrase: verb
                   | verb noun_phrase
                   | verb prepositional_phrase
                   | verb noun_phrase prepositional_phrase
        
        prepositional_phrase: PREPOSITION noun_phrase
        
        noun: WORD "o"
            | WORD "i"
        
        adjective: WORD "a"
        
        adverb: WORD "e"
        
        verb: WORD ("ar" | "ir" | "or" | "as" | "is" | "os" | "us" | "ez")
        
        ARTICLE: "la" | "un"
        PREPOSITION: "de" | "al" | "en" | "kun" | "por"
        WORD: /[a-z]+/
        
        %import common.WS
        %ignore WS
        """
    
    def parse(self, text: str) -> Tree:
        """Parsear una frase y devolver el árbol sintáctico.
        
        Args:
            text: Texto a parsear
            
        Returns:
            Árbol de parseo (Lark Tree)
        """
        return self.parser.parse(text)
    
    def parse_to_dict(self, text: str) -> dict:
        """Parsear una frase y devolver estructura de diccionario.
        
        Args:
            text: Texto a parsear
            
        Returns:
            Diccionario con estructura del árbol
        """
        tree = self.parse(text)
        return self._tree_to_dict(tree)
    
    def _tree_to_dict(self, tree: Tree) -> dict:
        """Convertir árbol Lark a diccionario.
        
        Args:
            tree: Árbol de parseo
            
        Returns:
            Diccionario con estructura
        """
        result = {"type": tree.data}
        
        if tree.children:
            children = []
            for child in tree.children:
                if isinstance(child, Tree):
                    children.append(self._tree_to_dict(child))
                else:
                    children.append(str(child))
            result["children"] = children
        
        return result
