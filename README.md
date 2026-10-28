# Métodos Numéricos

Implementaciones en Python de los métodos numéricos del Taller de Métodos Numéricos. Todos se usan desde una misma GUI en Tkinter, y cada método tiene su solver separado de la interfaz.

## Uso

Requiere [`uv`](https://docs.astral.sh/uv/) para manejar dependencias y entornos (no se usa `pip` ni `venv` directamente) y Python ≥ 3.15 (`uv` lo instala solo si hace falta).

Si no tenés `uv`, se instala con un solo comando. En Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

En macOS y Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cerrá y volvé a abrir la terminal para que `uv` quede en el PATH.

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

### En macOS

Se usa igual que en Windows: instalá `uv` con el comando de arriba, bajá el repo y, desde su carpeta, abrí la GUI con `uv run metodos-numericos`. Hace falta internet solo la primera vez, para bajar Python y las dependencias.

```bash
git clone https://github.com/agusdimarioUCC/metodos-numericos-python.git
cd metodos-numericos-python
uv run metodos-numericos
```

Si no tenés `git`, también podés bajar el repo desde GitHub con Code › Download ZIP.

Diferencias con Windows:

- La interfaz usa la fuente del sistema, porque Bahnschrift no existe en macOS, y las fórmulas usan STIX Two Text o Georgia en lugar de Cambria. Se ve algo distinto, pero las tablas y los resultados son los mismos.
- La primera vez que uses «Guardar como JPG», macOS te va a pedir permiso de grabación de pantalla para la terminal desde la que abriste el programa (Ajustes del Sistema › Privacidad y seguridad › Grabación de pantalla), porque el botón saca una captura del panel.
- `uv tool install --editable .` deja el comando `metodos-numericos` disponible en la terminal, pero no crea un ícono para abrirlo con doble clic.

Todavía no se probó en una Mac. Si algo falla al arrancar, `uv run python -m metodos_numericos` muestra el error.

## Métodos

Bisección, punto fijo, Newton-Raphson, secante, Gauss-Seidel, descomposición LU, regresión lineal, interpolación (Newton y Lagrange) y trazadoras cúbicas. Cada uno está en su propio subpaquete de `src/metodos_numericos/`.

## Estructura del repositorio

Es un solo proyecto de `uv` (un `pyproject.toml`, un `uv.lock` y un `.venv`) con un paquete, `src/metodos_numericos/`:

- La raíz del paquete tiene el código compartido: manejo de errores, formato numérico al estilo de la cátedra, lectura y validación de las expresiones `f(x)` que escribe el usuario, el contrato declarativo `DescriptorDeMetodo` que expone cada método y el toolkit de GUI en Tkinter (`metodos_numericos.gui`).
- Cada método es un subpaquete (`metodos_numericos/biseccion/`, `metodos_numericos/secante/`, etc.). Su solver vive en `__init__.py` y no depende de la interfaz. Su `gui.py` solo describe campos, columnas y gráfico, y ninguno importa `tkinter`.
- `registro.py` y `app.py` forman la app. `registro.py` es el único módulo que conoce todos los métodos, y `app.py` crea la ventana principal.

La arquitectura interna está detallada en `AGENTS.md`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
