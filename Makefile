.PHONY: config fetch test clean dist

config: fetch
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt --no-index --find-links wheelhouse/

fetch:
	@if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
	@if .venv/bin/python -m pip download -r requirements.txt -d wheelhouse/ 2>/dev/null; then \
		echo "Wheelhouse actualizado."; \
	elif ls wheelhouse/*.whl >/dev/null 2>&1; then \
		echo "Sin red. Usando wheelhouse existente."; \
	else \
		echo "Error: sin red ni wheelhouse. Ejecutar con conexión primero." >&2; \
		exit 1; \
	fi

test:
	.venv/bin/python -m pytest -q

clean:
	rm -rf .venv build dist

# Distribución portable: Nuitka en modo standalone (onedir).
# No se usa onefile porque descomprime en cada arranque.
# Los datos se copian junto al ejecutable para que la app siga siendo offline.
dist:
	.venv/bin/python -m nuitka --mode=standalone --output-dir=dist \
		--follow-imports --include-data-dir=data=data \
		--include-data-files=grammar.lark=grammar.lark main.py
