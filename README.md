# Ido Study Tool
Herramienta personal y offline para consultar palabras Ido, analizar frases y explicar su gramática.
Diccionario sólido en `data/ido.db`; corpus local en `data/tatoeba_ido_eng.txt`.

## Configuración
```bash
make config          # crea .venv e instala desde wheelhouse/ sin red
```

## Uso
```bash
.venv/bin/python main.py word manjar
.venv/bin/python main.py word manjas
.venv/bin/python main.py word manjar --segments
.venv/bin/python main.py en "to eat"
.venv/bin/python main.py check "La hundo mordas la katon."
.venv/bin/python main.py check "Me la homo."
.venv/bin/python main.py explain "Me pensas ke tu esas bela."
.venv/bin/python main.py audit -n 500
```

## Mantenimiento
```bash
.venv/bin/python main.py import --force   # reconstruye data/ido.db
.venv/bin/python -m pytest                # tests
make dist                                 # portable con Nuitka
```

La ejecución no usa red ni IA.
