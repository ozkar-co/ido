# Arquitectura

Sistema modular de análisis lingüístico y traducción para idiomas artificiales regulares.

## Componentes

### 1. Base de Datos (SQLite)

Almacenamiento de vocabulario y metadatos.

**Tablas principales**:
- `words`: Palabras completas con traducción y categoría
- `roots`: Raíces morfológicas
- `affixes`: Prefijos y sufijos
- `derivations`: Relaciones morfológicas
- `exceptions`: Irregularidades

### 2. Analizador Morfológico

Descompone palabras en raíz + afijos usando expresiones regulares.

**Funciones**: Identificar raíz, reconocer terminaciones, aplicar derivaciones, detectar compuestos.

**Salida**: `{raíz, afijos, categoría}`

### 3. Parser Sintáctico (Lark)

Análisis gramatical mediante gramática EBNF.

**Proceso**: Gramática EBNF → Parser automático (Lark) → AST

### 4. Motor de Traducción

Traducción basada en reglas lingüísticas.

**Pipeline**: Análisis morfológico → Análisis sintáctico → Representación intermedia → Reglas de traducción → Texto traducido

**Reglas**: Morfológicas, sintácticas, semánticas, excepciones.

### 5. Dictionary Manager

Interfaz con la base de datos: búsqueda, inserción, exportación, estadísticas.

### 6. CLI

Comandos: `translate`, `lookup`, `analyze`, `parse`

## Flujo de Datos

**Traducción**: Texto → Tokenización → Morfología → Sintaxis (AST) → Reglas → Salida

**Consulta**: Palabra → Búsqueda exacta → (fallback) Morfología → Búsqueda por raíz

## Stack

Python 3.11+, SQLite, Lark, Click, pytest

## Patrones

Repository, Strategy, Factory, Chain of Responsibility
