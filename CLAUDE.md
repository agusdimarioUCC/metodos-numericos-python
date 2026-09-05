# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

This repo holds numerical-methods implementations in Python, one per subdirectory (e.g. `gauss_seidel/`, `biseccion/`). It is a single `uv` **workspace**: the root `pyproject.toml` declares `[tool.uv.workspace] members = ["*"]` (excluding `.idea`), so there is one shared `.venv` and one shared `uv.lock` at the repo root — subprojects do **not** have their own `.venv`/`uv.lock`.

- `metodos_numericos_base/` is a shared library package (no console scripts) with code every method reuses: `NoConvergeError`/`EntradaInvalidaError`, the `Iteracion`/`ReportarIteracion` progress-reporting contract, `evaluar_funcion`/`compilar_funcion`/`leer_funcion_desde_terminal` for reading a user-supplied `f(x)` expression, the `DescriptorDeMetodo` contract a method declares itself through, and the `PanelDeMetodo`/`VentanaMetodosNumericos` Tkinter GUI toolkit. See "Architecture: metodos_numericos_base" below.
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
uv run metodos-numericos                     # opens the unified GUI: one window, one tab per method
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

cd gauss_seidel && uv run pytest             # gauss_seidel still has a test suite (legacy, see Testing policy)
```

There is no longer a per-method `<metodo>-gui` script (`biseccion-gui`, `punto-fijo-gui`, `newton-raphson-gui` were removed) — `uv run metodos-numericos` is the only GUI entry point, covering all five methods.

## Architecture: metodos_numericos_base

Shared library, `metodos_numericos_base/src/metodos_numericos_base/`:

- `errores.py` — `NoConvergeError`, raised by any iterative method that doesn't reach its tolerance within the iteration budget. `EntradaInvalidaError(ValueError)`, raised by `PanelDeMetodo` when a GUI field's text can't be converted (wrong subclass on purpose, so the panel's single `except ValueError` also catches it).
- `iteracion.py` — `Iteracion(numero, aproximacion, error)`, a generic one-row snapshot of an iterative method's progress. `aproximacion` is `float | tuple[float, ...]`: a float for the root-finding methods (bisection's midpoint, a fixed-point/Newton `x_n`), or a tuple for a method that iterates over a vector (Gauss-Seidel's partial solution — always `tuple(x)`, never the live array, so a reported row can't change after the fact). `formatear_aproximacion(aproximacion)` renders either shape as text without importing numpy (duck-typed: tries `float()`, falls back to formatting each component). `ReportarIteracion` is the `Callable[[Iteracion], None]` type every method's core function accepts as an optional `reportar_iteracion` parameter, called once per iteration instead of `print`-ing directly. `imprimir_iteracion` is the default text reporter the terminal layers pass in.
- `expresiones.py` — `evaluar_funcion(expresion, valor_x)` evaluates a user-typed `f(x)` string via a restricted `eval` (`__builtins__` cleared, only `x` and `math` module names available — blocks `import`, attribute-escape tricks, etc.). `compilar_funcion(expresion)` validates it (evaluating once at `x=0`) and wraps it into a `Callable[[float], float]` — the single place that "validate then wrap" pattern lives, instead of every `gui.py` repeating it.
- `terminal.py` — `leer_funcion_desde_terminal(*, etiqueta="f(x)", entrada=input)` reads and validates an expression from the terminal (retrying on a bad one), with a customizable prompt label so a method can ask for `"g(x)"` or `"f'(x)"` instead. `leer_valor_inicial_desde_terminal(*, etiqueta="Valor inicial", entrada=input)` reads a single float, retrying on a bad one.
- `descriptor.py` — the declarative contract a method exposes to the unified GUI, with **no tkinter import**: `TipoDeCampo` (an `Enum`: `EXPRESION_MATEMATICA`, `NUMERO`, `TEXTO_MULTILINEA`, `CASILLA_DE_VERIFICACION`, `SISTEMA_DE_ECUACIONES`), `CampoDeEntrada(nombre, etiqueta, tipo, valor_por_defecto, cantidad_de_lineas)` — one input field, `ResultadoDeMetodo(etiqueta_del_valor, valor_formateado, cantidad_de_iteraciones, lineas_de_verificacion, advertencias)` — what a successful run returns, and `DescriptorDeMetodo(nombre_para_mostrar, descripcion, campos, ejecutar, encabezado_de_aproximacion)` tying it together. `ejecutar` is a `Callable[[dict[str, object], ReportarIteracion], ResultadoDeMetodo]`: the dict maps each field's `nombre` to its already-converted value (an evaluable function for `EXPRESION_MATEMATICA`, a `float` for `NUMERO`, a `str` for `TEXTO_MULTILINEA`, a `bool` for `CASILLA_DE_VERIFICACION`, a `tuple[list[list[float]], list[float]]` — `(filas, terminos_independientes)` — for `SISTEMA_DE_ECUACIONES`).
- `sistemas.py` — `leer_sistema_desde_texto(texto)` parses a linear system written one equation per line (`"12 -1 3 | 8"`, `|`/`=` optional) into `(filas, terminos_independientes)`, raising a `ValueError` naming the offending row. Not specific to any method (despite currently only `gauss_seidel` using it) — `gui.py`'s `SISTEMA_DE_ECUACIONES` widget uses it once, to seed its input grid from a `CampoDeEntrada.valor_por_defecto` string and infer the grid's initial size.
- `gui.py` — the Tkinter toolkit, built entirely on `descriptor.py`. `elegir_fuente_matematica(tamano=11)` / `elegir_fuente_monoespaciada(tamano=11)` pick math-friendly (Cambria Math first) and monospaced (`TkFixedFont`) fonts, each falling back to the Tk default; both need a live `tk.Tk` root, so they're only called from inside `VentanaMetodosNumericos.__init__`, after `super().__init__()`. `PanelDeMetodo(ttk.Frame)` is one method's whole tab — built once from a `DescriptorDeMetodo` and never reconfigured afterward (its own `Treeview` with fixed `iteracion`/`aproximacion`/`error` columns, its own input widgets chosen per `TipoDeCampo`); public methods `registrar_iteracion` (matches `ReportarIteracion`; also calls `update_idletasks()` so the table fills live) and `limpiar_resultados`; the single `try/except` for the whole GUI lives in its private `_calcular` (`ValueError`/`ArithmeticError`/`NoConvergeError` show their raw message, anything else shows `"No se pudo calcular: ..."`). `VentanaMetodosNumericos(tk.Tk)` is the only window in the app: a `ttk.Notebook` with one `PanelDeMetodo` tab per descriptor it's given, in order. `_GrillaDeSistema(ttk.Frame)` is the widget behind `SISTEMA_DE_ECUACIONES`: a "Tamaño (n)" field + "Generar campos" button that rebuilds an n×(n+1) grid of plain `Entry` cells (capped at 8, matching `reordenar_para_dominancia_diagonal`'s own cap) — unlike `PanelDeMetodo`'s `Treeview`, destroying/recreating this grid on resize is safe because there are no column headings to lose, just simple `Entry` widgets. `_TecladoMatematico(ttk.Frame)` is a GeoGebra-style button pad (`x`, `π`, `x²`, `√`, `sen`/`cos`/`tg` and their inverses, `ln`/`log₁₀`/`log₂`, `|x|`, plus `⌫`/`←`/`→`) that `PanelDeMetodo.__init__` builds automatically whenever `_armar_panel_entradas` returns at least one `EXPRESION_MATEMATICA` field — no opt-in needed from a method's own `gui.py`, and it never appears on Gauss-Seidel's tab (zero expression fields there). Each button's *label* may be the Spanish notation a student learned (`sen`, `tg`) while the *text it inserts* is always the actual `math` name (`sin(`, `tan(`) — those two never need to match. It tracks which expression `Entry` to insert into via `<FocusIn>` bindings captured at construction time, not `focus_get()` at click time (Tkinter has already moved focus to the button itself by then); with more than one expression field (Newton-Raphson's `f(x)`/`f'(x)`) it also shows a small "Escribiendo en: ..." label. Its buttons are plain `tk.Button`, not `ttk.Button` — on Windows, `ttk.Button` renders via the native "vista" theme, which ignores `ttk.Style` padding overrides and imposes its own oversized minimum size, and separately, using the math font (Cambria Math) at button scale is a trap: math fonts reserve a lot of vertical line-height for stacked notation (integrals, extended radicals), so a 9pt Cambria Math button reports a ~65px line height — fine for the `f(x)` field, disastrous across 5 rows of buttons. The keypad's buttons use the plain UI font (`tkfont.nametofont("TkDefaultFont")`) at a small size instead, and get their size from plain `font`/`padx`/`pady` kwargs rather than any `ttk.Style`.

## Architecture: metodos_numericos_gui

`metodos_numericos_gui/src/metodos_numericos_gui/` is the app: the only package in the workspace that knows about all five methods.

- `registro.py` — imports each method's `DESCRIPTOR` from its `gui` module and lists them in `METODOS_DISPONIBLES: tuple[DescriptorDeMetodo, ...]`; the tuple's order is the tab order. Registration is explicit (plain imports), not automatic discovery (no `importlib.metadata` entry points) — deliberately, since this is a `uv` workspace and `uv sync`/`uv lock` run from a single member's directory can silently drop other members from the shared `.venv`, which would make entry-point discovery fail quietly.
- `__init__.py` — `iniciar_gui()`, the console-script target (`metodos-numericos = "metodos_numericos_gui:iniciar_gui"`): builds a `VentanaMetodosNumericos(METODOS_DISPONIBLES)` and calls `.ejecutar()`.
- `__main__.py` — a fallback so `uv run python -m metodos_numericos_gui` also works.

**To add a new method** (say, a hypothetical `regula_falsi/`): create the sibling directory the same way as `biseccion/` (own `pyproject.toml` depending on `metodos-numericos-base` via a workspace source — `members = ["*"]` picks it up automatically), write its solver taking `reportar_iteracion: ReportarIteracion | None = None` as its last parameter and calling it once per iteration with an `Iteracion`, then give it a `gui.py` with **only** an `ejecutar_regula_falsi(valores, reportar_iteracion) -> ResultadoDeMetodo` adapter and a module-level `DESCRIPTOR = DescriptorDeMetodo(...)` — no `tkinter` import needed there. Finally, add `"regula-falsi"` to `metodos_numericos_gui/pyproject.toml`'s `dependencies`/`[tool.uv.sources]`, and two lines in `registro.py` (the import, and the tuple entry). If the method needs a `TipoDeCampo` that doesn't exist yet (an integer field, a dropdown, etc.), that's the one place it's acceptable to touch `metodos_numericos_base/gui.py`: add the enum value and its branch in `PanelDeMetodo._armar_panel_entradas`/`_leer_valores`. `secante/` was built exactly this way — copy it.

## Architecture: gauss_seidel

`gauss_seidel/src/gauss_seidel/__init__.py` implements the iterative Gauss-Seidel method for solving `Ax = b`, plus the machinery needed to make it usable interactively:

- `gauss_seidel(matriz_coeficientes, terminos_independientes, aproximacion_inicial=None, tolerancia=1e-3, maximo_iteraciones=1000, reportar_iteracion=None)` — the solver itself. Raises `ValueError` for a non-square matrix, a shape mismatch between the matrix and the vector, or a zero on the diagonal (division by the pivot). Raises `NoConvergeError` (imported from `metodos_numericos_base`, re-exported here) if `tolerancia` isn't reached within `maximo_iteraciones`. Reports progress via the optional `reportar_iteracion` callback — each `Iteracion.aproximacion` is `tuple(x)` (never the live `x` array, since the solver keeps mutating it in place).
- `es_diagonalmente_dominante(matriz_coeficientes)` — checks row-wise diagonal dominance, a sufficient (not necessary) condition for guaranteed convergence.
- `reordenar_para_dominancia_diagonal(matriz_coeficientes, terminos_independientes=None)` — since reordering a system's equations doesn't change its solution, this brute-forces all row permutations (capped at 8x8 — factorial blowup beyond that) to find the one maximizing the minimum dominance margin, used to rescue systems that don't converge in their given order.
- `leer_matriz_desde_terminal(n=None, *, entrada=input)` / `resolver_desde_terminal(*, entrada=input)` — interactive terminal I/O layer. Both take an injectable `entrada` callable so tests can drive them with canned input instead of real stdin (see `tests/test_gauss_seidel.py` for the pattern: `entrada=lambda _: next(respuestas)`).
- `resolver_desde_terminal` is what runs under the module's `if __name__ == "__main__":` guard (reads a system, auto-reorders it if not diagonally dominant, solves, loops if the user wants another system) — but that guard only fires when the file is executed directly (`python src/gauss_seidel/__init__.py`), not via `python -m gauss_seidel` (no `__main__.py`) or the `gauss-seidel` script, which instead calls `main()` — a separate function that just runs one hardcoded example system.
- `gui.py` — no `tkinter` import. `ejecutar_gauss_seidel(valores, reportar_iteracion)` receives `valores["sistema"]` already as `(filas, terminos_independientes)` — parsed and validated by the GUI's own input grid, not by this method — conditionally reorders it (`valores["reordenar"]`, a `bool` from the GUI's checkbox) if it isn't dominant, runs the solver, and returns a `ResultadoDeMetodo` whose vector fields go through `formatear_aproximacion`. `DESCRIPTOR` uses a `SISTEMA_DE_ECUACIONES` field for the system and a `CASILLA_DE_VERIFICACION` for the reorder option, and overrides `encabezado_de_aproximacion` to `"Aproximación (x₁ … xₙ)"` since the table's middle column holds a whole vector, not a scalar.

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
