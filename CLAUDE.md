# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

This repo holds numerical-methods implementations in Python, one per subdirectory (e.g. `gauss_seidel/`). Each subdirectory is a fully independent `uv` project — its own `pyproject.toml`, `uv.lock`, `.venv`, and `src/<package>/` layout — not a shared package. When adding a new method, create a new sibling directory the same way (`uv init <method_name>` or copy the layout of `gauss_seidel/`), rather than adding it as a module inside an existing method's package.

Always use `uv` for dependency and environment management in these projects — never `pip` or `python -m venv` directly.

## Commands

Run all commands from inside the specific method's directory (e.g. `gauss_seidel/`), not the repo root — there is no root-level `pyproject.toml`.

```bash
cd gauss_seidel

uv sync                      # install deps + dev deps (pytest) into .venv
uv run pytest                # run the full test suite
uv run pytest -q             # quiet output
uv run pytest tests/test_gauss_seidel.py::test_resuelve_sistema_diagonalmente_dominante  # single test
uv run gauss-seidel                          # console-script entry point (pyproject.toml [project.scripts]) — runs one hardcoded example
uv run python -c "from gauss_seidel import resolver_desde_terminal; resolver_desde_terminal()"  # interactive terminal solver
```

## Architecture: gauss_seidel

`gauss_seidel/src/gauss_seidel/__init__.py` implements the iterative Gauss-Seidel method for solving `Ax = b`, plus the machinery needed to make it usable interactively:

- `gauss_seidel(a, b, x0=None, tol=1e-3, max_iter=1000)` — the solver itself. Raises `ValueError` for a non-square `A`, a shape mismatch between `A` and `b`, or a zero on the diagonal (division by the pivot). Raises `NoConvergeError` if `tol` isn't reached within `max_iter` iterations.
- `es_diagonalmente_dominante(a)` — checks row-wise diagonal dominance, a sufficient (not necessary) condition for guaranteed convergence.
- `reordenar_para_dominancia_diagonal(a, b=None)` — since reordering a system's equations doesn't change its solution, this brute-forces all row permutations (capped at 8x8 — factorial blowup beyond that) to find the one maximizing the minimum dominance margin, used to rescue systems that don't converge in their given order.
- `leer_matriz_desde_terminal(n=None, *, entrada=input)` / `resolver_desde_terminal(*, entrada=input)` — interactive terminal I/O layer. Both take an injectable `entrada` callable so tests can drive them with canned input instead of real stdin (see `tests/test_gauss_seidel.py` for the pattern: `entrada=lambda _: next(respuestas)`).
- `resolver_desde_terminal` is what runs under the module's `if __name__ == "__main__":` guard (reads a system, auto-reorders it if not diagonally dominant, solves, loops if the user wants another system) — but that guard only fires when the file is executed directly (`python src/gauss_seidel/__init__.py`), not via `python -m gauss_seidel` (no `__main__.py`) or the `gauss-seidel` script, which instead calls `main()` — a separate function that just runs one hardcoded example system.

Tests are black-box against this public API (no internal helpers are tested directly) and are written in Spanish, matching the source's naming and docstrings.
