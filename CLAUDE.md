# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

This repo holds numerical-methods implementations in Python, one per subdirectory (e.g. `gauss_seidel/`, `biseccion/`). It is a single `uv` **workspace**: the root `pyproject.toml` declares `[tool.uv.workspace] members = ["*"]` (excluding `.idea`), so there is one shared `.venv` and one shared `uv.lock` at the repo root — subprojects do **not** have their own `.venv`/`uv.lock`.

- `metodos_numericos_base/` is a shared library package (no console scripts; depends on `matplotlib` for the GUI plots) with code every method reuses: `NoConvergeError`/`EntradaInvalidaError`, the `Iteracion`/`ReportarIteracion` progress-reporting contract, `evaluar_funcion`/`compilar_funcion`/`leer_funcion_desde_terminal` for reading a user-supplied `f(x)` expression, the `DescriptorDeMetodo` contract a method declares itself through, and the `PanelDeMetodo`/`VentanaMetodosNumericos` Tkinter GUI toolkit. See "Architecture: metodos_numericos_base" below.
- `biseccion/`, `punto_fijo/`, `newton_raphson/`, `secante/` and `gauss_seidel/` are each their own `src/<package>/` layout with their own `pyproject.toml`, depending on `metodos-numericos-base` as a workspace dependency (`[tool.uv.sources] metodos-numericos-base = { workspace = true }`). Each one's `gui.py` declares a module-level `DESCRIPTOR` (a `DescriptorDeMetodo`) plus an `ejecutar_<metodo>(valores, reportar_iteracion)` adapter that calls the method's own solver — **none of these five `gui.py` files import `tkinter`**; they only describe their method's inputs/outputs declaratively.
- `metodos_numericos_gui/` is the single app that ties everything together: it's the only package that imports all five methods' `DESCRIPTOR`s (in `registro.py`), and it's the only place `VentanaMetodosNumericos` gets instantiated. See "Architecture: metodos_numericos_gui" below — that section has the exact recipe for adding a new method.

Always use `uv` for dependency and environment management in these projects — never `pip` or `python -m venv` directly.

## Versioning policy

- Always target the newest stable Python release. `requires-python` in each subproject's `pyproject.toml` should have its lower bound raised to match (currently `>=3.14`); don't add an upper bound.
- Always run with the newest resolvable versions of every dependency. Keep dependency specifiers as lower bounds only (`>=`), never pin exact versions or add upper bounds, and periodically re-run `uv lock --upgrade` (then `uv sync`) from the repo root to pull the shared lockfile forward.

## Formatting policy

- Indent with tabs, not spaces, in all Python source and test files. This applies to actual code indentation; whitespace used for alignment inside multi-line strings is unaffected.
- Variable and function names are in Spanish and fully spelled out — no bare single letters (`a`, `b`, `c`, `f`) and no abbreviations (`tol`, `max_iter`). The one deliberate exception is the literal `x` used as the eval namespace key in `evaluar_funcion`/`leer_funcion_desde_terminal`, because it's the mathematical variable the user themselves types into an expression (e.g. `"x**2 - 2"`), not an internal identifier. `gauss_seidel`'s parameters used to violate this (`a, b, x0, tol, max_iter`) but have since been renamed to match; there's no remaining exception to document.

## Testing policy

New methods do **not** get automated tests (no `tests/` folder, no `pytest` dev-dependency) — this is coursework, not code that needs regression protection. `gauss_seidel/tests/` predates this policy and is left as-is (its keyword arguments were updated when `gauss_seidel`'s parameters were renamed, but no new tests were added); it is not a pattern to keep extending. Do not apply TDD when building a new method here.

## Commands

The workspace has one shared environment, synced from the repo root:

```bash
uv sync                      # install/update the shared .venv from the root, for the whole workspace
```

The whole app, one command, from the repo root:

```bash
uv run metodos-numericos                     # opens the unified GUI: one window, a sidebar with every method
uv run python -m metodos_numericos_gui       # equivalent fallback (__main__.py), in case the script entry point ever breaks
```

Each method's other console scripts and modules are still run the same way, either from the repo root or from inside that method's directory (`uv run` finds the workspace root automatically either way):

```bash
uv run gauss-seidel                          # gauss_seidel: hardcoded example
uv run python -c "from gauss_seidel import resolver_desde_terminal; resolver_desde_terminal()"  # gauss_seidel: interactive terminal solver

uv run biseccion                             # biseccion: hardcoded example
uv run python -c "from biseccion import resolver_desde_terminal; resolver_desde_terminal()"  # biseccion: interactive terminal solver

uv run punto-fijo                            # punto_fijo: hardcoded example
uv run python -c "from punto_fijo import resolver_desde_terminal; resolver_desde_terminal()"  # punto_fijo: interactive terminal solver

uv run newton-raphson                        # newton_raphson: hardcoded example
uv run python -c "from newton_raphson import resolver_desde_terminal; resolver_desde_terminal()"  # newton_raphson: interactive terminal solver

uv run secante                               # secante: hardcoded example
uv run python -c "from secante import resolver_desde_terminal; resolver_desde_terminal()"  # secante: interactive terminal solver

cd gauss_seidel && uv run python -m pytest   # gauss_seidel still has a test suite (legacy, see Testing policy); `uv run pytest` fails here because the repo path has an accent (uv's trampoline can't canonicalize it)
```

There is no longer a per-method `<metodo>-gui` script (`biseccion-gui`, `punto-fijo-gui`, `newton-raphson-gui` were removed) — `uv run metodos-numericos` is the only GUI entry point, covering all five methods.

## Architecture: metodos_numericos_base

Shared library, `metodos_numericos_base/src/metodos_numericos_base/`:

- `errores.py` — `NoConvergeError`, raised by any iterative method that doesn't reach its tolerance within the iteration budget. `EntradaInvalidaError(ValueError)`, raised by `PanelDeMetodo` when a GUI field's text can't be converted (wrong subclass on purpose, so the panel's single `except ValueError` also catches it).
- `iteracion.py` — `Iteracion(numero, aproximacion, error, detalle)`, one row of an iterative method's progress **in the course's table layout** (the handouts `2 - Raices de funciones.pdf` / `3 - Sistema de ecuaciones lineales.pdf` one folder up). `aproximacion` is a float for root-finding methods or a `tuple` for vector methods (never a live array). `error` is `None` on rows that have no previous approximation yet (row 0 of every course table shows "-"). `detalle` carries the method's own columns (bisection's a, b, f(a), f(c); fixed point's g(xᵢ); Newton's f(xᵢ), f′(xᵢ); Gauss-Seidel's `componente_j`/`error_j`), keyed by names the method's `ColumnaDeTabla`s refer to. `formatear_aproximacion`/`imprimir_iteracion` are the terminal-side formatters (`imprimir_iteracion` prints `-` for `error=None`).
- Row conventions per solver (match the handouts): bisection rows 1..n, `error=None` on row 1, stops on |cₖ − cₖ₋₁| < ε; fixed point rows 0..n with `detalle["valor_g"]`; Newton rows 0..n with `valor_funcion`/`valor_derivada`, last (root) row without `detalle`; secant rows 0 and 1 are the two seeds (`error=None`), then one row per new xᵢ with `valor_funcion`; Gauss-Seidel row 0 is the initial vector. The returned iteration count is unchanged (e.g. Newton still returns 3 for the handout example even though the table has rows 0–3).
- `formato.py` — number formatting in the course's style: `formatear_numero(valor, decimales)` (comma decimal, typographic minus, never `−0,0000`), `formatear_numero_legible` (switches to `1,23 × 10⁻⁹` when fixed decimals would hide the value), `formatear_valor_corto` (`0,001`, `10⁻⁶` — used for ε and in solver error messages), `formatear_signo` (`< 0`/`> 0`), `leer_numero` (accepts `0,4` and `0.4`), `subindice`. No tkinter.
- `expresiones.py` — `evaluar_funcion(expresion, valor_x)` evaluates a user-typed `f(x)` string via a restricted `eval` (`__builtins__` cleared, only `x` and `math` module names available — blocks `import`, attribute-escape tricks, etc.). `compilar_funcion(expresion)` validates it **without evaluating** (compiles it and checks every name in `co_names` is `x` or a `math` name — evaluating at x=0 used to reject valid expressions like `log(x)` or `1/x`) and wraps it into a `Callable[[float], float]` — the single place that "validate then wrap" pattern lives, instead of every `gui.py` repeating it.
- `terminal.py` — `leer_funcion_desde_terminal(*, etiqueta="f(x)", entrada=input)` reads and validates an expression from the terminal (retrying on a bad one), with a customizable prompt label so a method can ask for `"g(x)"` or `"f'(x)"` instead. `leer_valor_inicial_desde_terminal(*, etiqueta="Valor inicial", entrada=input)` reads a single float, retrying on a bad one.
- `descriptor.py` — the declarative contract a method exposes to the GUI, with **no tkinter/matplotlib import**: `TipoDeCampo`, `CampoDeEntrada(nombre, etiqueta, tipo, valor_por_defecto, cantidad_de_lineas)` (labels use the course's notation: `"a ="`, `"x₀ ="`); `ColumnaDeTabla(clave, encabezado, formato, es_raiz, es_error)` + `FormatoDeColumna` (`NUMERO`/`SIGNO`/`ENTERO`) + `COLUMNA_DE_NUMERO_DE_FILA` — `clave` is `"numero"`/`"aproximacion"`/`"error"` or a `detalle` key, `es_raiz` paints the last row's cell amber, `es_error` paints the first cell below ε green; `TipoDeGrafico` (`INTERVALOS`, `TELARANA`, `TANGENTES`, `SECANTES`, `CONVERGENCIA`) + `GraficoDeMetodo(tipo, campo_de_la_funcion)`; `ResultadoDeMetodo(etiqueta_del_valor, valor, cantidad_de_iteraciones, verificaciones, advertencias, matrices)` — everything raw (floats), the GUI formats; `Verificacion(etiqueta, valor, esperado)`; `MatrizDeResultado(nombre, filas, es_resultado)`; and `DescriptorDeMetodo(nombre_para_mostrar, capitulo, formula, descripcion, campos, ejecutar, columnas, grafico, usa_criterio_de_parada)`. `columnas` is a callable `valores -> columns` (so Gauss-Seidel can have one Xⱼ/|Eⱼ| pair per unknown; use `columnas_fijas(...)` otherwise) or `None` for no table. When `usa_criterio_de_parada` is true the GUI adds its own ε / "Máx. iteraciones" group and passes `valores["tolerancia"]` (float) and `valores["maximo_iteraciones"]` (int) — every iterative adapter must forward them to its solver. `errores.py`'s `NoConvergeError.despues_de(maximo, ultimo_error)` builds the standard message; `EntradaInvalidaError(mensaje, nombre_del_campo)` lets the GUI mark the offending field.
- `sistemas.py` — `leer_sistema_desde_texto(texto)` parses a linear system written one equation per line (`"12 -1 3 | 8"`, `|`/`=` optional) into `(filas, terminos_independientes)`, raising a `ValueError` naming the offending row. Not specific to any method (despite currently only `gauss_seidel` using it) — `gui.py`'s `SISTEMA_DE_ECUACIONES` widget uses it once, to seed its input grid from a `CampoDeEntrada.valor_por_defecto` string and infer the grid's initial size.
- `gui/` — the Tkinter toolkit (a package; same import path `metodos_numericos_base.gui`), visual identity "apunte de cátedra": colors from the handouts (f(x) red, g(x) green, y = x blue, **amber only for the answer** — root cell, result band, root point — and light green for "|E| < ε" cells), Bahnschrift for UI text and Cambria for everything mathematical (numbers, formulas, fields; its digits are tabular, Bahnschrift's are not). Never use Cambria Math in widgets (its linespace is ~5× normal). The base package's `__init__` loads the GUI **lazily** (`__getattr__`), so terminal scripts never import tkinter or matplotlib.
  - `tema.py` — color tokens, `crear_tema(raiz)` → `Tema` (fonts + `px()` DPI scaling), ttk `clam` styles, `activar_nitidez_en_pantallas_escaladas()` (Windows DPI awareness, called before `tk.Tk()`), `mostrar_barra_solo_si_hace_falta(barra)` (auto-hiding scrollbars; the bar must be `grid`-managed).
  - `ventana.py` — `VentanaMetodosNumericos(tk.Tk)`: `BarraLateral` + one `PanelDeMetodo` per descriptor stacked in one grid cell (`mostrar_metodo(i)` just `tkraise`s; Ctrl+Tab cycles). `vincular_grillas_de_sistema` links every `GrillaDeSistema` across panels (Gauss-Seidel ↔ LU) via `al_cambiar` → `_propagar_sistema` → `establecer_sistema` (which suppresses `al_cambiar` to avoid ping-pong); `mostrar_metodo` also fires the leaving panel's grids' `al_cambiar`, because switching panels doesn't fire `<FocusOut>`.
  - `barra_lateral.py` — methods grouped by `DescriptorDeMetodo.capitulo`, keyboard-navigable.
  - `panel.py` — `PanelDeMetodo`: header (name, formula, description), scrollable data column (fields, `TecladoMatematico`, stopping criterion, Calcular, result block), and a white "sheet" with a `Panedwindow` (plot above, table below) — or `VistaDeMatrices` when the descriptor has neither plot nor table (LU). Keeps raw `valores`/iterations so the "Decimales" spinbox reformats without recomputing (ε = 10⁻ⁿ auto-raises decimals to n+1). The GUI's single `try/except` is `_calcular`: input errors mark the field red; solver errors are translated (`NoConvergeError`, `OverflowError` → "diverge", math domain errors); partial tables/plots are kept on failure. Editing a field after a result shows a "Cambiaste los datos" note and a debounced plot preview.
  - `campos.py` — `TecladoMatematico` (labels in Spanish notation — `sen`, `tg` — insert the `math` names; tracks the target entry via `<FocusIn>`; keys have `takefocus=False`) and `GrillaDeSistema` (extended matrix [A | b] with b in red, "Ecuaciones" spinbox up to `TAMANO_MAXIMO_SISTEMA = 5`, resizing keeps overlapping values).
  - `tabla.py` — `TablaDeIteraciones`, drawn on a `Canvas` (a `Treeview` can't color single cells): incremental rows while the solver runs, amber/green cells, row selection (click, ↑/↓) → `al_seleccionar`, numbers ≥ 10⁷ in scientific notation.
  - `grafico.py` — `LienzoDelGrafico` (matplotlib `FigureCanvasTkAgg`, no toolbar): one drawer per `TipoDeGrafico` (bisection draws the fig. 8 stacked interval arrows in a second axes), resamples the curve over the current view, wheel zoom / drag pan / double-click reset, auto-zooms onto a selected step that looks too small. Matplotlib can't read the regular Cambria on Windows (it's inside a `.ttc` and renders only some glyphs), so plot numbers use the UI font and math labels use Cambria **italic** (a separate `.ttf`), with DejaVu as fallback.
  - `matrices.py` — `VistaDeMatrices`: bracketed matrices (L, U, y, x, A⁻¹), the `es_resultado` one on amber.

## Architecture: metodos_numericos_gui

`metodos_numericos_gui/src/metodos_numericos_gui/` is the app: the only package in the workspace that knows about all five methods.

- `registro.py` — imports each method's `DESCRIPTOR` from its `gui` module and lists them in `METODOS_DISPONIBLES: tuple[DescriptorDeMetodo, ...]`; the tuple's order is the tab order. Registration is explicit (plain imports), not automatic discovery (no `importlib.metadata` entry points) — deliberately, since this is a `uv` workspace and `uv sync`/`uv lock` run from a single member's directory can silently drop other members from the shared `.venv`, which would make entry-point discovery fail quietly.
- `__init__.py` — `iniciar_gui()`, the console-script target (`metodos-numericos = "metodos_numericos_gui:iniciar_gui"`): builds a `VentanaMetodosNumericos(METODOS_DISPONIBLES)` and calls `.ejecutar()`.
- `__main__.py` — a fallback so `uv run python -m metodos_numericos_gui` also works.

**To add a new method** (say, a hypothetical `regula_falsi/`): create the sibling directory the same way as `biseccion/` (own `pyproject.toml` depending on `metodos-numericos-base` via a workspace source — `members = ["*"]` picks it up automatically), write its solver taking `reportar_iteracion: ReportarIteracion | None = None` as its last parameter and calling it once per iteration with an `Iteracion`, then give it a `gui.py` with **only** an `ejecutar_regula_falsi(valores, reportar_iteracion) -> ResultadoDeMetodo` adapter (forwarding `valores["tolerancia"]`/`valores["maximo_iteraciones"]`) and a module-level `DESCRIPTOR = DescriptorDeMetodo(...)` declaring its `capitulo`, `formula`, `columnas` (matching the `detalle` keys its solver reports, in the handout's column order) and `grafico` — no `tkinter`/`matplotlib` import needed there. A new kind of plot means a new `TipoDeGrafico` plus its drawer in `gui/grafico.py`. Finally, add `"regula-falsi"` to `metodos_numericos_gui/pyproject.toml`'s `dependencies`/`[tool.uv.sources]`, and two lines in `registro.py` (the import, and the tuple entry). If the method needs a `TipoDeCampo` that doesn't exist yet (an integer field, a dropdown, etc.), add the enum value and its branch in `PanelDeMetodo._armar_columna_de_datos`/`_leer_valores` (`metodos_numericos_base/gui/panel.py`). `secante/` was built exactly this way — copy it.

## Architecture: gauss_seidel

`gauss_seidel/src/gauss_seidel/__init__.py` implements the iterative Gauss-Seidel method for solving `Ax = b`, plus the machinery needed to make it usable interactively:

- `gauss_seidel(matriz_coeficientes, terminos_independientes, aproximacion_inicial=None, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver itself. Raises `ValueError` for a non-square matrix, a shape mismatch between the matrix and the vector, or a zero on the diagonal (division by the pivot). Raises `NoConvergeError` (imported from `metodos_numericos_base`, re-exported here) if `tolerancia` isn't reached within `maximo_iteraciones`. Reports progress via the optional `reportar_iteracion` callback — each `Iteracion.aproximacion` is `tuple(x)` (never the live `x` array, since the solver keeps mutating it in place).
- `es_diagonalmente_dominante(matriz_coeficientes)` — checks row-wise diagonal dominance, a sufficient (not necessary) condition for guaranteed convergence.
- `reordenar_para_dominancia_diagonal(matriz_coeficientes, terminos_independientes=None)` — since reordering a system's equations doesn't change its solution, this brute-forces all row permutations (capped at 8x8 — factorial blowup beyond that) to find the one maximizing the minimum dominance margin, used to rescue systems that don't converge in their given order.
- `leer_matriz_desde_terminal(n=None, *, entrada=input)` / `resolver_desde_terminal(*, entrada=input)` — interactive terminal I/O layer. Both take an injectable `entrada` callable so tests can drive them with canned input instead of real stdin (see `tests/test_gauss_seidel.py` for the pattern: `entrada=lambda _: next(respuestas)`).
- `resolver_desde_terminal` is what runs under the module's `if __name__ == "__main__":` guard (reads a system, auto-reorders it if not diagonally dominant, solves, loops if the user wants another system) — but that guard only fires when the file is executed directly (`python src/gauss_seidel/__init__.py`), not via `python -m gauss_seidel` (no `__main__.py`) or the `gauss-seidel` script, which instead calls `main()` — a separate function that just runs one hardcoded example system.
- `gui.py` — no `tkinter` import. `ejecutar_gauss_seidel(valores, reportar_iteracion)` receives `valores["sistema"]` already as `(filas, terminos_independientes)` — parsed and validated by the GUI's own input grid, not by this method — conditionally reorders it (`valores["reordenar"]`, a `bool` from the GUI's checkbox) if it isn't dominant, runs the solver, and returns a `ResultadoDeMetodo` with the raw solution vector and one `Verificacion` per equation (A·x against the *original* b, even if rows were reordered). `DESCRIPTOR` uses a `SISTEMA_DE_ECUACIONES` field for the system, a `CASILLA_DE_VERIFICACION` for the reorder option, and `armar_columnas(valores)` to build the handout's i, X₁, |E₁|, X₂, |E₂|, … columns for whatever n the grid has.

Tests are black-box against this public API (no internal helpers are tested directly) and are written in Spanish, matching the source's naming and docstrings. This is legacy from before the no-tests policy above; don't add new tests here either.

## Architecture: biseccion

`biseccion/src/biseccion/__init__.py` implements the bisection method for finding a root of `f(x) = 0` in `[extremo_inferior, extremo_superior]`, and is the reference layout new root-finding methods should copy:

- `biseccion(funcion, extremo_inferior, extremo_superior, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver. Raises `ValueError` if the interval is backwards or `funcion` doesn't change sign across it; raises `NoConvergeError` if `tolerancia` isn't reached within `maximo_iteraciones`. Purely computational — no I/O — it only reports progress through the optional `reportar_iteracion` callback (see `metodos_numericos_base.iteracion`).
- `leer_intervalo_desde_terminal(*, entrada=input)` — biseccion-specific terminal input (an interval, unlike fixed-point/Newton which use a single starting guess); `leer_funcion_desde_terminal` and `evaluar_funcion` are imported from `metodos_numericos_base` rather than defined here.
- `resolver_desde_terminal(*, entrada=input)` / `main()` — same shape as `gauss_seidel`'s terminal layer, passing `imprimir_iteracion` as the reporter so progress still prints during a terminal run.
- `gui.py` — no `tkinter` import, just `ejecutar_biseccion(valores, reportar_iteracion)` (calls `biseccion(...)` and returns a `ResultadoDeMetodo`) and the module-level `DESCRIPTOR`.

## Architecture: punto_fijo

`punto_fijo/src/punto_fijo/__init__.py` implements the fixed-point iteration method: given `x = g(x)` (the user's own rearrangement of `f(x) = 0`), it iterates `x_(n+1) = g(x_n)` from a starting guess.

- `punto_fijo(funcion_g, valor_inicial, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver. No sign-change precondition (unlike bisection); error is the absolute difference between successive approximations. Raises `NoConvergeError` if `tolerancia` isn't reached within `maximo_iteraciones`.
- `resolver_desde_terminal(*, entrada=input)` — asks for `g(x)` (`leer_funcion_desde_terminal(etiqueta="g(x)")`) and a starting value (`leer_valor_inicial_desde_terminal`), same loop-and-ask-to-repeat shape as the other methods.
- `funcion_ejemplo_g` / `main()` — the hardcoded example is `g(x) = sqrt(x + 2)` (from `f(x) = x^2 - x - 2 = 0`), converging to `x = 2` from `x0 = 1.5`.
- `gui.py` — no `tkinter` import, `ejecutar_punto_fijo(valores, reportar_iteracion)` plus `DESCRIPTOR` with two fields: `funcion_g` and `valor_inicial`.

## Architecture: newton_raphson

`newton_raphson/src/newton_raphson/__init__.py` implements Newton-Raphson: given `f(x)` and its derivative `f'(x)` (both typed in by the user — no symbolic differentiation), it iterates `x_(n+1) = x_n - f(x_n)/f'(x_n)`.

- `newton_raphson(funcion, derivada, valor_inicial, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver. Raises `ValueError` if `derivada` evaluates to zero at some approximation (can't divide by it); raises `NoConvergeError` if `tolerancia` isn't reached within `maximo_iteraciones`. Converges quadratically, so it typically needs far fewer iterations than bisection for the same root.
- `resolver_desde_terminal(*, entrada=input)` — asks for `f(x)`, then `f'(x)` (both via `leer_funcion_desde_terminal` with different `etiqueta`s), then a starting value.
- `funcion_ejemplo` / `derivada_ejemplo` / `main()` — the hardcoded example is `f(x) = x^2 - 2`, `f'(x) = 2x`, matching bisection's example so their iteration counts are directly comparable.
- `gui.py` — no `tkinter` import, `ejecutar_newton_raphson(valores, reportar_iteracion)` plus `DESCRIPTOR` with three fields: `funcion`, `derivada`, `valor_inicial`.

## Architecture: secante

`secante/src/secante/__init__.py` implements the secant method: Newton-Raphson without an analytic derivative — it approximates `f'(x_n)` by the slope of the line through the last two iterates, so it needs two starting approximations `x0`, `x1` (but, unlike bisection, no sign change across them). It iterates `x_(n+1) = x_n - f(x_n)·(x_n - x_(n-1)) / (f(x_n) - f(x_(n-1)))`.

- `secante(funcion, primera_aproximacion, segunda_aproximacion, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver. Raises `ValueError` if the two seeds are equal, or if `funcion` takes the same value at two consecutive approximations (the secant line is horizontal — can't divide by its slope); raises `NoConvergeError` if `tolerancia` isn't reached within `maximo_iteraciones`. Error is the absolute difference between successive approximations, like `punto_fijo`/`newton_raphson`. It caches `valor_funcion_anterior`/`valor_funcion_actual` so `funcion` is evaluated once per new iterate.
- `resolver_desde_terminal(*, entrada=input)` — asks for `f(x)`, then two starting values via `leer_valor_inicial_desde_terminal` (`etiqueta="Primera aproximación (x0)"` / `"Segunda aproximación (x1)"`), same loop-and-ask-to-repeat shape as the other methods.
- `funcion_ejemplo` / `main()` — the hardcoded example is `f(x) = x^2 - 2` from `x0 = 1`, `x1 = 2`, matching bisection's interval so their iteration counts are directly comparable (the secant converges in ~4 iterations, bisection in ~10).
- `gui.py` — no `tkinter` import, `ejecutar_secante(valores, reportar_iteracion)` plus `DESCRIPTOR` with three fields: `funcion`, `primera_aproximacion`, `segunda_aproximacion`.
