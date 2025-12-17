# Scripts

Scripts de utilidad que se ejecutan una sola vez o esporádicamente.

## Esquema de Base de Datos

**001_create_schema.sql**: Crea el esquema completo de la base de datos SQLite.

Uso:
```bash
sqlite3 dictionary.db < scripts/001_create_schema.sql
```

## Importación de Datos

**import_idan.py**: Importa el diccionario Ido-Inglés (idan.txt) a la base de datos con análisis morfológico completo.

Uso:
```bash
python scripts/import_idan.py [--db dictionary.db] [--dict data/idan.txt]
```

El script:
- Crea el esquema automáticamente si no existe
- Parsea ~14,100 entradas del diccionario
- **Análisis morfológico**: separa cada palabra en raíz + afijos + terminación
  - Ejemplo: `abad.ey.o` → raíz=`abad`, afijos=`ey`, terminación=`o`
- Detecta palabras derivadas (8 espacios de indentación) y las vincula con parent_word_id
- Identifica palabras obsoletas con formato `[palabra (obs.) > nueva_palabra]`
- Extrae metadatos:
  - Tipo de palabra: `{tr}`, `{intr}`, `{adv.}`, etc.
  - Subcategoría: `(rel.)`, `(anat.)`, `(bot.)`, etc.
  - Info gramatical: `[de]`, `[ad]`, etc.
  - Antónimos: extrae de `Ant: palabra`
- Categoriza automáticamente: NOUN, VERB, ADJECTIVE, ADVERB, etc.
- Evita líneas de continuación (no crea entradas falsas)
- Importa 93 abreviaturas/categorías
- Muestra estadísticas detalladas al finalizar

Estadísticas típicas:
- 10,728 palabras principales
- 3,449 palabras derivadas
- 114 pares de antónimos
- 5,405 con subcategoría
- 2,531 verbos, 7,796 sustantivos, 1,543 adjetivos

## Consulta de Datos

**query_dict.py**: Herramienta de consulta del diccionario con soporte para búsqueda morfológica.

Uso:
```bash
# Buscar palabra exacta con derivadas
python scripts/query_dict.py abad.o

# Buscar todas las palabras de una raíz
python scripts/query_dict.py --root abad

# Buscar palabras con afijo específico (ej: -in- femenino)
python scripts/query_dict.py --affix in

# Especificar base de datos
python scripts/query_dict.py --db otra.db palabra
```

Muestra:
- Morfología completa (raíz, afijos, terminación)
- Categoría gramatical y tipo
- Traducción
- Información gramatical adicional
- Antónimos
- Palabras derivadas (si es palabra principal)
- Advertencia si es obsoleta

## Análisis Morfológico

**analyze_word.py**: Analizador morfológico para palabras en Ido.

Uso:
```bash
# Analizar una palabra
python scripts/analyze_word.py abad.in.o

# Analizar participio
python scripts/analyze_word.py vid.ant.a

# Derivar palabra
python scripts/analyze_word.py --derive bela adjective adverb

# Ver ejemplos
python scripts/analyze_word.py --examples

# Ver demostraciones
python scripts/analyze_word.py --demo-verbs
python scripts/analyze_word.py --demo-participles
python scripts/analyze_word.py --demo-derivations
python scripts/analyze_word.py --all-demos
```

El script:
- Descompone palabras en raíz + prefijos + sufijos + terminación
- Identifica 22 prefijos conocidos (ne-, des-, mis-, ri-, etc.)
- Identifica 32 sufijos conocidos (-in-, -ey-, -ig-, -es-, etc.)
- Reconoce participios (-ant-, -int-, -ont-, -at-, -it-, -ot-)
- Determina categoría gramatical (NOUN, VERB, ADJECTIVE, ADVERB, etc.)
- Genera formas verbales (infinitivos, tiempos, imperativo)
- Genera formas participiales (adjetivales, adverbiales, nominales)
- Aplica derivaciones directas (verb→noun, adj→adv, etc.)
- Muestra significado de cada componente morfológico
- Incluye ejemplos y demostraciones interactivas

Ver [documentación completa](../ido/README.md) para más detalles.

## Otros Scripts

(Por agregar según necesidades del proyecto)
