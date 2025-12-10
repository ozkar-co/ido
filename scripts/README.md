# Scripts

Scripts de utilidad que se ejecutan una sola vez o esporádicamente.

## Esquema de Base de Datos

**001_create_schema.sql**: Crea el esquema completo de la base de datos SQLite.

Uso:
```bash
sqlite3 dictionary.db < scripts/001_create_schema.sql
```

## Importación de Datos

**import_idan.py**: Importa el diccionario Ido-Inglés (idan.txt) a la base de datos.

Uso:
```bash
python scripts/import_idan.py --db dictionary.db --dict data/idan.txt
```

El script:
- Crea el esquema automáticamente si no existe
- Parsea ~14,000 entradas del diccionario
- Detecta palabras derivadas (con indentación)
- Identifica palabras obsoletas
- Extrae información gramatical, categorías, antónimos
- Importa abreviaturas y categorías
- Muestra estadísticas al finalizar

## Otros Scripts

(Por agregar según necesidades del proyecto)
