# ido

Traductor y diccionario interactivo para un idioma artificial con morfología altamente regular.

## Descripción

Sistema de análisis lingüístico y traducción automática basado en reglas para idiomas artificiales. Combina un diccionario estructurado (SQLite), análisis morfológico mediante expresiones regulares, parser sintáctico (EBNF + Lark) y motor de traducción basado en reglas.

## Componentes

**Base de datos léxica (SQLite)**: Vocabulario, raíces, derivaciones y metadatos gramaticales.

**Analizador morfológico**: Descomposición de palabras en raíces y afijos mediante patrones regulares.

**Parser sintáctico (Lark)**: Análisis gramatical usando gramática EBNF formal con generación de AST.

**Motor de traducción**: Traducción composicional basada en reglas morfológicas y sintácticas.

**CLI**: Interfaz de línea de comandos para consultas, análisis y traducción.

## Documentación


- [Arquitectura del sistema](docs/arquitectura.md) - Diseño de componentes y flujo de datos
- [Gramática EBNF](docs/gramatica.md) - Especificación formal del idioma
- [Esquema del diccionario](docs/diccionario.md) - Estructura de base de datos
- [Metodología](docs/metodologia.md) - Proceso de desarrollo
- [Roadmap](docs/roadmap.md) - Plan de versiones futuras

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Configuración Inicial

Crear base de datos e importar diccionario:

```bash
# Importar diccionario Ido-Inglés (crea el esquema automáticamente)
python scripts/import_idan.py

# Resultado: ~14,100 palabras + 93 categorías
# - 10,700 palabras principales
# - 3,400 palabras derivadas
# - 114 pares de antónimos
# - Análisis morfológico completo (raíz + afijos + terminación)
```

Consultar diccionario:

```bash
# Buscar palabra exacta
python scripts/query_dict.py abad.o

# Buscar por raíz morfológica
python scripts/query_dict.py --root abad

# Buscar palabras con afijo específico
python scripts/query_dict.py --affix in
```

Verificar datos:

```bash
sqlite3 dictionary.db "SELECT COUNT(*) FROM words;"
sqlite3 dictionary.db "SELECT word, translation FROM words LIMIT 10;"
```

## Uso

### Analizador Morfológico

```bash
# Analizar morfología de una palabra
python scripts/analyze_word.py abad.in.o

# Ver ejemplos y demostraciones
python scripts/analyze_word.py --examples
python scripts/analyze_word.py --all-demos

# Derivar palabras
python scripts/analyze_word.py --derive bela adjective adverb
```

Ver [documentación completa del analizador morfológico](ido/README.md).

### CLI (próximamente)

```bash
ido lookup palabra        # Consultar diccionario
ido analyze palabra       # Análisis morfológico
ido parse "frase"        # Análisis sintáctico
ido translate "texto"    # Traducir
```

## Tests

```bash
# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=ido
```

## Licencia

MIT


