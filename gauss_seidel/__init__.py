"""Método de Gauss-Seidel para resolver sistemas de ecuaciones lineales Ax = b."""

from __future__ import annotations

import itertools
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray


class NoConvergeError(RuntimeError):
    """Se lanza cuando el método no converge dentro del número máximo de iteraciones."""


def es_diagonalmente_dominante(a: NDArray[np.float64]) -> bool:
    """Verifica si la matriz A es diagonalmente dominante por filas.

    No es una condición necesaria para la convergencia, pero si se cumple,
    la convergencia de Gauss-Seidel está garantizada.
    """
    diagonal = np.abs(np.diag(a))
    suma_filas = np.sum(np.abs(a), axis=1) - diagonal
    return bool(np.all(diagonal >= suma_filas))


def reordenar_para_dominancia_diagonal(
    a: ArrayLike, b: ArrayLike | None = None
) -> tuple[NDArray[np.float64], NDArray[np.float64] | None]:
    """Reordena las filas de A (y de b, si se da) para lograr dominancia diagonal.

    Las ecuaciones de un sistema se pueden escribir en cualquier orden sin
    cambiar su solución, pero Gauss-Seidel solo converge garantizado si esa
    matriz es diagonalmente dominante. Esta función prueba todas las
    permutaciones de filas y devuelve la que maximiza el margen mínimo de
    dominancia (diagonal - suma del resto de la fila).

    No garantiza encontrar una permutación estrictamente dominante si no
    existe ninguna; en ese caso devuelve la mejor encontrada, que puede no
    asegurar convergencia.

    Args:
        a: Matriz de coeficientes (n x n).
        b: Vector de términos independientes (n,), opcional.

    Returns:
        Tupla (a_reordenada, b_reordenada). b_reordenada es None si no se
        pasó b.

    Raises:
        ValueError: Si A no es cuadrada o tiene más de 8 filas (probar todas
            las permutaciones de una matriz más grande no es práctico).
    """
    a = np.array(a, dtype=np.float64)
    n, m = a.shape
    if n != m:
        raise ValueError(f"La matriz A debe ser cuadrada, se recibió {a.shape}")
    if n > 8:
        raise ValueError(
            "Solo se soportan matrices de hasta 8x8 (se prueban todas las "
            f"permutaciones de filas), se recibió una de {n}x{n}"
        )

    mejor_perm = tuple(range(n))
    mejor_score = -np.inf
    for perm in itertools.permutations(range(n)):
        candidata = a[list(perm), :]
        diagonal = np.abs(np.diag(candidata))
        suma_filas = np.sum(np.abs(candidata), axis=1) - diagonal
        score = np.min(diagonal - suma_filas)
        if score > mejor_score:
            mejor_score = score
            mejor_perm = perm

    a_reordenada = a[list(mejor_perm), :]
    b_reordenada = None if b is None else np.array(b, dtype=np.float64)[list(mejor_perm)]
    return a_reordenada, b_reordenada


def leer_matriz_desde_terminal(
    n: int | None = None, *, entrada: Callable[[str], str] = input
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Lee interactivamente el sistema A x = b desde la terminal.

    Pide el tamaño del sistema (si no se pasa `n`) y luego, fila por fila,
    los coeficientes de A separados por espacios y el término independiente
    b correspondiente. Si una fila no tiene la cantidad de valores esperada,
    vuelve a pedirla.

    Args:
        n: Tamaño del sistema (n x n). Si es None, se pregunta al usuario.
        entrada: Función usada para leer cada línea (por defecto `input`);
            se puede inyectar otra función en los tests.

    Returns:
        Tupla (a, b) con la matriz y el vector leídos.
    """
    if n is None:
        n = int(entrada("Tamaño del sistema (n): ").strip())

    filas: list[list[float]] = []
    valores_b: list[float] = []
    for i in range(n):
        while True:
            linea = entrada(f"Fila {i + 1} de A ({n} valores separados por espacios): ")
            valores = linea.split()
            if len(valores) == n:
                break
            print(f"Se esperaban {n} valores, se recibieron {len(valores)}. Probá de nuevo.")
        filas.append([float(v) for v in valores])
        valores_b.append(float(entrada(f"b[{i + 1}]: ").strip()))

    return np.array(filas, dtype=np.float64), np.array(valores_b, dtype=np.float64)


def gauss_seidel(
    a: ArrayLike,
    b: ArrayLike,
    x0: ArrayLike | None = None,
    tol: float = 1e-3,
    max_iter: int = 1000,
) -> tuple[NDArray[np.float64], int]:
    """Resuelve Ax = b con el método iterativo de Gauss-Seidel.

    Args:
        a: Matriz de coeficientes (n x n).
        b: Vector de términos independientes (n,).
        x0: Aproximación inicial (n,). Si es None, se usa el vector cero.
        tol: Tolerancia para el criterio de convergencia (norma infinito).
        max_iter: Número máximo de iteraciones permitidas.

    Returns:
        Tupla (x, iteraciones) con la solución aproximada y el número de
        iteraciones realizadas.

    Raises:
        ValueError: Si A no es cuadrada, las dimensiones no coinciden, o
            algún elemento de la diagonal es cero.
        NoConvergeError: Si no se alcanza la tolerancia en max_iter iteraciones.
    """
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)

    n, m = a.shape
    if n != m:
        raise ValueError(f"La matriz A debe ser cuadrada, se recibió {a.shape}")
    if b.shape != (n,):
        raise ValueError(f"b debe tener forma ({n},), se recibió {b.shape}")
    if np.any(np.diag(a) == 0):
        raise ValueError("La diagonal de A no puede tener ceros")

    x = np.zeros(n) if x0 is None else np.array(x0, dtype=np.float64).copy()
    error = np.inf

    for iteracion in range(1, max_iter + 1):
        x_anterior = x.copy()
        for i in range(n):
            suma = a[i, :i] @ x[:i] + a[i, i + 1 :] @ x_anterior[i + 1 :]
            x[i] = (b[i] - suma) / a[i, i]

        error = np.linalg.norm(x - x_anterior, ord=np.inf)
        print(f"Iteración {iteracion}: x = {x}, error = {error:.5f}")
        if error < tol:
            return x, iteracion

    raise NoConvergeError(
        f"No convergió después de {max_iter} iteraciones (último error: {error:.5f})"
    )


def main() -> None:
    # Sistema de ejemplo (filas reordenadas para que sea diagonalmente
    # dominante; el orden original no lo era y el método divergía):
    #  12x -  1y + 3z =  8
    #   1x +  7y - 3z = -51
    #   4x -  4y + 9z =  61
    a = [
        [12, -1, 3],
        [1, 7, -3],
        [4, -4, 9],
    ]
    b = [8, -51, 61]

    print(f"¿A es diagonalmente dominante? {es_diagonalmente_dominante(np.array(a))}")

    x, iteraciones = gauss_seidel(a, b)
    print(f"Solución: {x}")
    print(f"Iteraciones: {iteraciones}")
    print(f"Verificación (A @ x): {np.array(a) @ x}")
    print(f"b original:           {np.array(b)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
    """Pide sistemas por terminal y los resuelve, uno tras otro.

    Después de cada sistema pregunta si se quiere resolver otro; el proceso
    solo termina cuando la respuesta no es "s".
    """
    while True:
        a, b = leer_matriz_desde_terminal(entrada=entrada)

        if not es_diagonalmente_dominante(a):
            print("A no es diagonalmente dominante, reordenando filas...")
            a, b = reordenar_para_dominancia_diagonal(a, b)
            if es_diagonalmente_dominante(a):
                print("Filas reordenadas: ahora A es diagonalmente dominante.")
            else:
                print("No se encontró un orden diagonalmente dominante; puede no converger.")

        x, iteraciones = gauss_seidel(a, b)
        print(f"Solución: {x}")
        print(f"Iteraciones: {iteraciones}")
        print(f"Verificación (A @ x): {a @ x}")

        otro = entrada("¿Resolver otro sistema? (s/n): ").strip().lower()
        if otro != "s":
            break


if __name__ == "__main__":
    resolver_desde_terminal()
