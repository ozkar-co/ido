# Analizador Morfológico para Ido

Implementación del analizador morfológico según las reglas de gramática de Ido descritas en `data/quick_gramm.txt`.

## Características

El analizador morfológico implementa:

### 1. Terminaciones Verbales

- **Infinitivos**: -ar (presente), -ir (pasado), -or (futuro)
- **Tiempos**: -as (presente), -is (pasado), -os (futuro), -us (condicional)
- **Imperativo**: -ez

### 2. Terminaciones Gramaticales

- **Sustantivos**: -o (singular), -i (plural)
- **Adjetivos**: -a
- **Adverbios**: -e

### 3. Participios

Infijos que se combinan con terminaciones gramaticales:

- **-ant-**: presente activo (seeing)
- **-int-**: pasado activo (having seen)
- **-ont-**: futuro activo (going to see)
- **-at-**: presente pasivo (being seen)
- **-it-**: pasado pasivo (having been seen)
- **-ot-**: futuro pasivo (going to be seen)

### 4. Prefijos (22 prefijos)

- **ne-**: negación (nebela = not beautiful)
- **des-**: contrario (desfacila = difficult)
- **mis-**: incorrectamente (miskomprenar = misunderstand)
- **ri-**: otra vez (ridicar = say again)
- **ex-**: ex, anterior (exoficiro = ex-officer)
- Y 17 más...

### 5. Sufijos (32 sufijos)

- **-in-**: femenino (abadino = abbess)
- **-ey-**: lugar para (abadeyo = abbey)
- **-ig-**: causar que sea/haga (beligar = beautify)
- **-es-**: ser (belesar = to be beautiful)
- **-et-**: pequeñez (rivereto = stream)
- **-eg-**: grandeza (pluvego = downpour)
- Y 26 más...

### 6. Derivaciones Directas

- **Verbo → Sustantivo**: -ar → -o (brosar → broso)
- **Adjetivo → Sustantivo**: -a → -o (bona → bono)
- **Sustantivo → Adjetivo**: -o → -a (oro → ora)
- **Adjetivo → Adverbio**: -a → -e (bela → bele)

## Uso

### Como módulo Python

```python
from ido.morphology import MorphologyAnalyzer

analyzer = MorphologyAnalyzer()

# Analizar una palabra
result = analyzer.analyze("abad.in.o")
print(f"Raíz: {result.root}")           # abad
print(f"Sufijos: {result.suffixes}")    # ['in']
print(f"Terminación: {result.ending}")  # o
print(f"Categoría: {result.category}")  # NOUN (singular)

# Generar formas verbales
forms = analyzer.get_verb_forms("vid")
print(forms['present'])      # vidas
print(forms['past'])         # vidis
print(forms['imperative'])   # videz

# Generar participios
participles = analyzer.get_participle_forms("vid", "a")
print(participles['present_active'])  # vid.ant.a
print(participles['past_passive'])    # vid.it.a

# Aplicar derivación
derived = analyzer.apply_derivation("bela", "adjective", "adverb")
print(derived)  # bele
```

### Script de línea de comandos

```bash
# Analizar una palabra
python scripts/analyze_word.py abad.o

# Analizar palabra con sufijo
python scripts/analyze_word.py abad.in.o

# Analizar participio
python scripts/analyze_word.py vid.ant.a

# Derivar una palabra
python scripts/analyze_word.py --derive bela adjective adverb

# Ver ejemplos
python scripts/analyze_word.py --examples

# Ver demostraciones
python scripts/analyze_word.py --demo-verbs
python scripts/analyze_word.py --demo-participles
python scripts/analyze_word.py --demo-derivations

# Ver todas las demostraciones
python scripts/analyze_word.py --all-demos
```

## Ejemplos

### Análisis de palabras

```bash
$ python scripts/analyze_word.py abad.in.o

============================================================
Analizando: abad.in.o
============================================================

Palabra original: abad.in.o
Raíz: abad
Sufijos: in
  - in: feminine
Terminación: o

Categoría: NOUN (singular)
Subcategorías: feminine
```

```bash
$ python scripts/analyze_word.py bel.es.ar

============================================================
Analizando: bel.es.ar
============================================================

Palabra original: bel.es.ar
Raíz: bel
Sufijos: es
  - es: to be
Terminación: ar

Categoría: VERB (infinitive)
Subcategorías: to be
```

### Palabras con prefijos

```bash
$ python scripts/analyze_word.py ne.bel.a

============================================================
Analizando: ne.bel.a
============================================================

Palabra original: ne.bel.a
Raíz: bel
Prefijos: ne
  - ne: negation
Terminación: a

Categoría: ADJECTIVE
```

### Participios

```bash
$ python scripts/analyze_word.py vid.ant.a

============================================================
Analizando: vid.ant.a
============================================================

Palabra original: vid.ant.a
Raíz: vid
Sufijos: ant
  - ant: present active participle
Terminación: a

Categoría: PARTICIPLE (adjective form)
Subcategorías: present active participle
```

## Arquitectura

El analizador utiliza dos estrategias según el formato de la palabra:

### 1. Palabras con puntos (dotted)

En Ido, los puntos separan morfemas claramente:

- **raíz.terminación**: `abad.o`
- **raíz.sufijo.terminación**: `abad.ey.o`
- **prefijo.raíz.terminación**: `ne.bel.a`
- **raíz.sufijo.sufijo.terminación**: `bel.es.ant.a`

### 2. Palabras sin puntos (solid)

Para palabras escritas sin separadores, el analizador busca patrones conocidos:

- Identifica prefijos al inicio
- Identifica terminaciones al final
- Identifica sufijos conocidos en el medio

## Tests

El módulo incluye 29 tests unitarios que cubren:

- Análisis de sustantivos, adjetivos, adverbios, verbos
- Prefijos y sufijos
- Participios
- Derivaciones directas
- Generación de formas verbales
- Generación de participios

```bash
# Ejecutar tests
pytest tests/test_morphology.py -v

# Con cobertura
pytest tests/test_morphology.py --cov=ido.morphology
```

Cobertura actual: **85%**

## Extensibilidad

El diseño modular permite fácil extensión:

1. **Agregar prefijos/sufijos**: Modificar diccionarios `PREFIXES` y `SUFFIXES`
2. **Agregar reglas de derivación**: Extender método `apply_derivation()`
3. **Mejorar análisis**: Refinar métodos `_analyze_dotted()` y `_analyze_solid()`
4. **Integrar diccionario**: Conectar con la base de datos SQLite para validar raíces

## Limitaciones Actuales

- No valida si una raíz existe en el diccionario
- No maneja compuestos (palabras formadas por múltiples raíces)
- No analiza el sufijo perfecto `-ab-` en formas verbales
- No implementa sufijos numéricos (-esm, -im, -op, -opl)

Estas características pueden añadirse en versiones futuras manteniendo la compatibilidad con la API actual.

## Referencias

- Gramática de Ido: `data/quick_gramm.txt`
- Roadmap del proyecto: `docs/roadmap.md` (v0.2.0 - Morfología)
- Arquitectura: `docs/arquitectura.md`
