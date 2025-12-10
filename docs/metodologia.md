# Metodología

Desarrollo iterativo e incremental.

## Fases

### Fase 1: Fundamentos

- Implementar esquema de BD
- Crear scripts de migración
- Setup testing framework

**Entregables**: Base de datos SQLite, suite de tests inicial.

### Fase 2: Diccionario Básico

- Repository pattern para acceso a datos
- API de consulta
- Importar vocabulario inicial (100-200 palabras)
- CLI básico (`ido lookup`)

**Entregables**: Módulo `ido.dictionary`, CLI funcional, tests.

### Fase 3: Analizador Morfológico

- Patrones regex para terminaciones
- Identificación de raíz
- Sistema de derivación
- Integración con diccionario

**Entregables**: Módulo `ido.morphology`, comando `ido analyze`, tests.

### Fase 4: Parser Gramatical

- Gramática EBNF en sintaxis Lark
- Parser básico
- Generación y recorrido de AST
- Validación con frases de ejemplo

**Entregables**: `grammar.lark`, módulo `ido.parser`, comando `ido parse`, tests.

### Fase 5: Motor de Traducción

- Representación intermedia
- Reglas de traducción morfológicas y sintácticas
- Integración de componentes
- Casos especiales

**Entregables**: Módulo `ido.translator`, comando `ido translate`, tests end-to-end.

### Fase 6: Análisis de Corpus

- Procesamiento por lotes
- Identificar palabras desconocidas
- Detectar patrones nuevos
- Estadísticas de frecuencia

**Entregables**: Script de análisis, reporte, expansión del diccionario.

### Fase 7: Refinamiento

- Optimizar consultas (índices, cache)
- Mejorar mensajes de error
- Documentación de usuario
- Refactoring

**Entregables**: Documentación completa, benchmarks.

## Principios

**TDD**: Test → Implementar → Refactorizar

**Documentación continua**: Docstrings, actualizar docs, README actualizado.

**Validación con ejemplos reales**: Casos básicos, complejos, límite, excepciones.

**Versionado semántico**: MAJOR.MINOR.PATCH

## Herramientas

```bash
# Entorno
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Linting
black ido/ tests/
ruff check ido/ tests/
mypy ido/

# Testing
pytest
pytest --cov=ido
```

## Métricas

**Cobertura**: >80%

**Diccionario**: 200 → 500 → 1000 → 2000+ palabras

**Precisión**: >90% traducciones correctas
