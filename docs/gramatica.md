# Gramática EBNF

Especificación formal de la gramática del idioma artificial.

## Notación

```ebnf
regla = definición ;              (* Regla básica *)
opcion = [ opcional ] ;           (* Opcional *)
repeticion = { elemento }* ;      (* Cero o más *)
alternativa = ( a | b | c ) ;     (* Alternativas *)
```

## Nivel Léxico

### Tokens Básicos

```ebnf
letter = "a".."z" | "A".."Z" ;
digit = "0".."9" ;
```

### Categorías Morfológicas

```ebnf
(* Terminaciones *)
noun_suffix = "o" ;
adjective_suffix = "a" ;
adverb_suffix = "e" ;
verb_suffix_infinitive = "i" ;
verb_suffix_present = "as" ;
verb_suffix_past = "is" ;
verb_suffix_future = "os" ;

(* Estructura *)
root = letter, { letter | digit } ;
noun = root, noun_suffix ;
adjective = root, adjective_suffix ;
adverb = root, adverb_suffix ;
verb = root, verb_suffix ;
```

### Partículas

```ebnf
article = "la" | "un" ;
preposition = "de" | "al" | "en" | "kun" | "por" ;
conjunction = "kaj" | "aŭ" | "sed" ;
pronoun = "mi" | "vi" | "li" | "ŝi" | "ĝi" | "ni" | "ili" ;
```

## Nivel Sintáctico

```ebnf
(* Frases *)
noun_phrase = [ article ], [ adjective ], noun ;
verb_phrase = verb, [ noun_phrase ], [ prepositional_phrase ] ;
prepositional_phrase = preposition, noun_phrase ;

(* Oraciones *)
simple_sentence = noun_phrase, verb_phrase, "." ;
compound_sentence = simple_sentence, conjunction, simple_sentence ;
question = noun_phrase, verb_phrase, "?" ;

sentence = simple_sentence | compound_sentence | question ;
```

## Reglas de Derivación

### Pluralización

```ebnf
plural_noun = root, noun_suffix, "j" ;
```

Ejemplo: `domo` → `domoj`

### Acusativo

```ebnf
accusative = noun, "n" ;
```

Ejemplo: `domo` → `domon`

### Derivación entre Categorías

Sustantivo → Adjetivo: `belo` → `bela`  
Adjetivo → Adverbio: `bela` → `bele`  
Raíz → Verbo: `labor-` → `labori`

## Ejemplos

**Frase simple**: `la bela domo`

```
noun_phrase
├── article: "la"
├── adjective: "bela"
└── noun: "domo"
```

**Oración completa**: `la hundo kuras rapide.`

```
simple_sentence
├── noun_phrase
│   ├── article: "la"
│   └── noun: "hundo"
├── verb_phrase
│   ├── verb: "kuras"
│   └── adverb: "rapide"
└── "."
```

## Implementación con Lark

```python
grammar = """
    start: sentence+
    sentence: noun_phrase verb_phrase "."
    noun_phrase: [ARTICLE] [adjective] noun
    verb_phrase: verb [noun_phrase]
    
    noun: ROOT NOUN_SUFFIX
    adjective: ROOT ADJ_SUFFIX
    verb: ROOT VERB_SUFFIX
    
    ARTICLE: "la" | "un"
    NOUN_SUFFIX: "o"
    ADJ_SUFFIX: "a"
    VERB_SUFFIX: "as" | "is" | "os" | "i"
    ROOT: /[a-z]+/
    
    %import common.WS
    %ignore WS
"""
```

## Expansiones Futuras

- Correlativos
- Palabras compuestas
- Participios (activos/pasivos)
- Modo imperativo y condicional
- Subordinadas
- Negación

Versión: 0.1.0
