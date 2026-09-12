# Métodos Numéricos

Implementaciones en Python de métodos numéricos para el Taller de Métodos Numéricos, con una GUI unificada en Tkinter y una capa de solvers reutilizable en cada método.

## Métodos incluidos

- **Bisección** (`biseccion/`) — búsqueda de raíces de `f(x) = 0` por intervalos.
- **Punto fijo** (`punto_fijo/`) — iteración `x = g(x)`.
- **Newton-Raphson** (`newton_raphson/`) — `f(x)` y `f'(x)`, convergencia cuadrática.
- **Secante** (`secante/`) — Newton-Raphson sin derivada analítica.
- **Gauss-Seidel** (`gauss_seidel/`) — resolución iterativa de sistemas `Ax = b`, con detección/reordenamiento por dominancia diagonal.
- **Descomposición LU** (`descomposicion_lu/`) — resolución directa de `Ax = b`, cálculo de `A⁻¹` y número de condición.

## Estructura del repositorio

Es un **workspace de `uv`**: un solo `.venv` y un solo `uv.lock` en la raíz para todos los subproyectos (`[tool.uv.workspace] members = ["*"]`).

- `metodos_numericos_base/` — librería compartida: manejo de errores, formato numérico al estilo de la cátedra, lectura/validación de expresiones `f(x)` ingresadas por el usuario, el contrato declarativo `DescriptorDeMetodo` que cada método expone, y el toolkit de GUI en Tkinter (`metodos_numericos_base.gui`).
- `biseccion/`, `punto_fijo/`, `newton_raphson/`, `secante/`, `gauss_seidel/`, `descomposicion_lu/` — cada uno con su propio `src/<paquete>/`, su solver desacoplado de la interfaz, y un `gui.py` que solo describe sus campos/columnas/gráfico (ninguno importa `tkinter`).
- `metodos_numericos_gui/` — la app que une todo: es el único paquete que conoce los seis métodos (`registro.py`) e instancia la ventana principal.

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

Cada método también se puede correr de forma individual, ya sea con un ejemplo predefinido o de forma interactiva por terminal:

```bash
uv run biseccion                             # ejemplo hardcodeado
uv run python -c "from biseccion import resolver_desde_terminal; resolver_desde_terminal()"

uv run gauss-seidel
uv run python -c "from gauss_seidel import resolver_desde_terminal; resolver_desde_terminal()"
```

(reemplazar `biseccion`/`gauss-seidel` por `punto-fijo`, `newton-raphson`, `secante` o `descomposicion-lu` según el método).

## Licencia

MIT — ver [LICENSE](LICENSE).
