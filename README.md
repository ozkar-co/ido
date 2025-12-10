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

## Uso

```bash
ido lookup palabra        # Consultar diccionario
ido analyze palabra       # Análisis morfológico
ido parse "frase"        # Análisis sintáctico
ido translate "texto"    # Traducir
```

## Licencia

MIT

