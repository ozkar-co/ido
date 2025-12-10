# Roadmap

Plan de desarrollo del proyecto.

## v0.1.0 - Fundamentos

- Documentación del proyecto
- Arquitectura definida
- Configuración inicial
- Esquema de base de datos
- CLI básico (lookup)
- Diccionario con 200 palabras básicas

## v0.2.0 - Morfología

- Analizador morfológico completo
- Identificación de raíces
- Sistema de derivación
- Comando `ido analyze`
- 500 palabras en diccionario

## v0.3.0 - Sintaxis

- Parser gramatical con Lark
- Gramática EBNF básica
- Generación de AST
- Comando `ido parse`
- Validación sintáctica

## v0.4.0 - Traducción Básica

- Motor de traducción basado en reglas
- Comando `ido translate`
- Traducción de oraciones simples
- 1000 palabras en diccionario

**MVP Funcional**

## v0.5.0 - Corpus

- Procesamiento de textos completos
- Análisis de frecuencias
- Detección de palabras desconocidas
- Exportación de estadísticas
- Modo batch

## v1.0.0 - Release Estable

- Traducción robusta
- 2000+ palabras en diccionario
- Gramática completa (casos principales)
- Tests exhaustivos (>80% cobertura)
- Modo interactivo (REPL)
- Manejo de excepciones
- Precisión >90%

## Futuro

**v1.1**: Traducción bidireccional (español → idioma artificial)

**v1.2**: Web interface (FastAPI + frontend)

**v1.3**: Análisis semántico avanzado, desambiguación

**v1.4**: Integración con modelos de IA (traducción híbrida)

**v2.0**: Plataforma multiidioma (framework genérico para conlangs)

## Expansiones Posibles

- Módulo educativo (ejercicios, flashcards)
- Generación de contenido (conjugador, sintetizador)
- Herramientas de investigación (análisis estadístico, visualización)
- Aplicaciones móviles

## Stack Futuro

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| FastAPI | API web | v1.2 |
| React | Frontend | v1.2 |
| spaCy | NLP avanzado | v1.3 |
| Transformers | Modelos IA | v1.4 |
| Docker | Deployment | v1.0 |
