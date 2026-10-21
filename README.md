# Métodos Numéricos

Implementaciones en Python de los métodos numéricos del Taller de Métodos Numéricos. Todos se usan desde una misma GUI en Tkinter, y cada método tiene su solver separado de la interfaz.

## Uso

Requiere [`uv`](https://docs.astral.sh/uv/) para manejar dependencias y entornos (no se usa `pip` ni `venv` directamente) y Python ≥ 3.15 (`uv` lo instala solo si hace falta).

Instalá o sincronizá el entorno desde la raíz del repo:

```bash
uv sync
```

Abrí la GUI con todos los métodos y su barra lateral:

```bash
uv run metodos-numericos
```

Para abrirla con doble clic, sin terminal, instalala una vez como herramienta de uv. Con `--editable`, los cambios en el código se ven al volver a abrirla:

```bash
uv tool install --editable .
```

Eso deja `metodos-numericos` en el PATH, así que se abre desde Win+R, el buscador de Windows o un acceso directo, sin consola.

Si el script falla, o si querés ver un error de arranque (sin consola no se muestra), usá esta alternativa equivalente:

```bash
uv run python -m metodos_numericos
```

Para correr los tests (los de Gauss-Seidel) se usa `python -m pytest`, porque `uv run pytest` falla cuando la ruta del repo tiene tildes:

```bash
uv run python -m pytest
```

## Métodos

Bisección, punto fijo, Newton-Raphson, secante, Gauss-Seidel, descomposición LU, regresión lineal, interpolación (Newton y Lagrange) y trazadoras cúbicas. Cada uno está en su propio subpaquete de `src/metodos_numericos/`.

## Estructura del repositorio

Es un solo proyecto de `uv` (un `pyproject.toml`, un `uv.lock` y un `.venv`) con un paquete, `src/metodos_numericos/`:

- La raíz del paquete tiene el código compartido: manejo de errores, formato numérico al estilo de la cátedra, lectura y validación de las expresiones `f(x)` que escribe el usuario, el contrato declarativo `DescriptorDeMetodo` que expone cada método y el toolkit de GUI en Tkinter (`metodos_numericos.gui`).
- Cada método es un subpaquete (`metodos_numericos/biseccion/`, `metodos_numericos/secante/`, etc.). Su solver vive en `__init__.py` y no depende de la interfaz. Su `gui.py` solo describe campos, columnas y gráfico, y ninguno importa `tkinter`.
- `registro.py` y `app.py` forman la app. `registro.py` es el único módulo que conoce todos los métodos, y `app.py` crea la ventana principal.

La arquitectura interna está detallada en `CLAUDE.md`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
