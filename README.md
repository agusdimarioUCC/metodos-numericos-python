# Métodos Numéricos

Implementaciones en Python de métodos numéricos para el Taller de Métodos Numéricos, con una GUI unificada en Tkinter y una capa de solvers reutilizable en cada método.

## Métodos incluidos

- **Bisección** (`biseccion/`) — búsqueda de raíces de `f(x) = 0` por intervalos.
- **Punto fijo** (`punto_fijo/`) — iteración `x = g(x)`.
- **Newton-Raphson** (`newton_raphson/`) — `f(x)` y `f'(x)`, convergencia cuadrática.
- **Secante** (`secante/`) — Newton-Raphson sin derivada analítica.
- **Gauss-Seidel** (`gauss_seidel/`) — resolución iterativa de sistemas `Ax = b`, con detección/reordenamiento por dominancia diagonal.
- **Descomposición LU** (`descomposicion_lu/`) — resolución directa de `Ax = b`, cálculo de `A⁻¹` y número de condición.
- **Regresión lineal** (`regresion_lineal/`) — mínimos cuadrados, con linealización para modelos exponencial, potencial y de crecimiento.
- **Interpolación de Newton** (`interpolacion_newton/`) — polinomio por diferencias divididas.
- **Interpolación de Lagrange** (`interpolacion_lagrange/`) — polinomio como suma de Lᵢ(x)·yᵢ, sin diferencias divididas.
- **Trazadoras cúbicas** (`trazadoras_cubicas/`) — natural y condicionada, un polinomio cúbico por tramo.

## Estructura del repositorio

Es un solo proyecto de `uv` (un `pyproject.toml`, un `uv.lock`, un `.venv`) con un único paquete, `src/metodos_numericos/`:

- La raíz del paquete es el código compartido: manejo de errores, formato numérico al estilo de la cátedra, lectura/validación de expresiones `f(x)` ingresadas por el usuario, el contrato declarativo `DescriptorDeMetodo` que cada método expone, y el toolkit de GUI en Tkinter (`metodos_numericos.gui`).
- Cada método es un subpaquete (`metodos_numericos/biseccion/`, `metodos_numericos/secante/`, …) con su solver desacoplado de la interfaz en `__init__.py` y un `gui.py` que solo describe sus campos/columnas/gráfico (ninguno importa `tkinter`).
- `registro.py` y `app.py` son la app que une todo: `registro.py` es el único módulo que conoce todos los métodos y `app.py` instancia la ventana principal.

Para más detalle sobre la arquitectura interna, ver `CLAUDE.md`.

## Requisitos

- [`uv`](https://docs.astral.sh/uv/) para manejo de dependencias y entornos (no se usa `pip` ni `venv` directamente).
- Python ≥ 3.14 (`uv` lo instala solo si hace falta).

## Uso

Instalar/sincronizar el entorno compartido desde la raíz del repo:

```bash
uv sync
```

Abrir la GUI unificada (todos los métodos, con barra lateral):

```bash
uv run metodos-numericos
```

Para abrirla con doble clic, sin terminal, instalala una vez como herramienta de uv (con `--editable`, los cambios al código se ven al volver a abrirla):

```bash
uv tool install --editable .
```

Eso deja `metodos-numericos` en el PATH: se abre desde Win+R, el buscador de Windows o un acceso directo, sin consola.

Si el script llegara a fallar (o para ver un error al arrancar, que sin consola no se muestra), hay una alternativa equivalente:

```bash
uv run python -m metodos_numericos
```

Correr los tests (los de Gauss-Seidel). Se usa `python -m pytest` porque `uv run pytest` falla cuando la ruta del repo tiene tildes:

```bash
uv run python -m pytest
```

## Licencia

MIT — ver [LICENSE](LICENSE).
