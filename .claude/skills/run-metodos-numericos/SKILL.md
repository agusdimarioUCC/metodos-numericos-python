---
name: run-metodos-numericos
description: Run, launch, start, screenshot or drive the Tkinter GUI of metodos-numericos (bisección, Newton, secante, LU, etc.) and run its tests. Use to see a UI change working or capture a method's result.
---

Paths are relative to `metodos-numericos-python/`. App de escritorio Tkinter (Windows, `uv`, Python ≥ 3.15). Se maneja con `driver.py`: abre la ventana real, elige un método, carga campos, calcula, imprime el texto del resultado y guarda una captura.

## Setup
```bash
uv sync
```

## Run (agent path)
```bash
PYTHONIOENCODING=utf-8 uv run python .claude/skills/run-metodos-numericos/driver.py --listar
PYTHONIOENCODING=utf-8 uv run python .claude/skills/run-metodos-numericos/driver.py "Bisec" --salida captura.png
PYTHONIOENCODING=utf-8 uv run python .claude/skills/run-metodos-numericos/driver.py "Newton-R" funcion="x**2-2" derivada="2*x" valor_inicial=1 --salida captura.png
```
- El primer argumento es parte del nombre del método; `nombre=valor` pisa un campo (nombres con `--listar`; además `tolerancia` y `maximo_iteraciones`). Sin campos usa los valores por defecto.
- Imprime `RESULTADO: ...` (o el mensaje de error del panel) y `CAPTURA: <ruta>`. Abrir la PNG con Read para verla.
- Campos de sistema/puntos (`sistema`, `puntos`, selectores) no son `ttk.Entry`: el driver solo pisa entradas de texto; esos usan su valor por defecto.

## Run (human path)
```bash
uv run python -m metodos_numericos
```
Abre la ventana y bloquea hasta cerrarla. `uv run metodos-numericos` es lo mismo pero sin consola (gui-script).

## Test
```bash
uv run python -m pytest -q
```
Solo hay tests de Gauss-Seidel (legado).

## Gotchas
- La captura usa `PIL.ImageGrab` (pantalla real): el driver pone la ventana `-topmost`; sin eso salió el escritorio/otra app tapando.
- `uv run pytest` falla por la tilde en la ruta; usar `python -m pytest`.
- Sin `PYTHONIOENCODING=utf-8` la consola de Windows rompe los acentos en la salida.
- Necesita pantalla interactiva: no sirve sin sesión de escritorio.
- El driver toca `panel._entradas` y `panel._calcular` (privados); si se renombran, actualizarlo.
