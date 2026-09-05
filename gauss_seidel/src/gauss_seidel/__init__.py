"""Método de Gauss-Seidel para resolver sistemas de ecuaciones lineales Ax = b."""

from __future__ import annotations

import itertools
from typing import Callable

import numpy as np
from metodos_numericos_base import Iteracion, NoConvergeError, ReportarIteracion, imprimir_iteracion
from numpy.typing import ArrayLike, NDArray

__all__ = [
	"NoConvergeError",
	"es_diagonalmente_dominante",
	"gauss_seidel",
	"leer_matriz_desde_terminal",
	"main",
	"reordenar_para_dominancia_diagonal",
	"resolver_desde_terminal",
]


def es_diagonalmente_dominante(matriz_coeficientes: NDArray[np.float64]) -> bool:
	"""Verifica si la matriz A es diagonalmente dominante por filas.

	No es una condición necesaria para la convergencia, pero si se cumple,
	la convergencia de Gauss-Seidel está garantizada.
	"""
	diagonal = np.abs(np.diag(matriz_coeficientes))
	suma_filas = np.sum(np.abs(matriz_coeficientes), axis=1) - diagonal
	return bool(np.all(diagonal >= suma_filas))


def reordenar_para_dominancia_diagonal(
		matriz_coeficientes: ArrayLike, terminos_independientes: ArrayLike | None = None
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
		matriz_coeficientes: Matriz de coeficientes A (n x n).
		terminos_independientes: Vector de términos independientes b (n,), opcional.

	Returns:
		Tupla (matriz_reordenada, terminos_independientes_reordenados).
		terminos_independientes_reordenados es None si no se pasó
		terminos_independientes.

	Raises:
		ValueError: Si A no es cuadrada o tiene más de 8 filas (probar todas
			las permutaciones de una matriz más grande no es práctico).
	"""
	matriz_coeficientes = np.array(matriz_coeficientes, dtype=np.float64)
	n, m = matriz_coeficientes.shape
	if n != m:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {matriz_coeficientes.shape}")
	if n > 8:
		raise ValueError(
			"Solo se soportan matrices de hasta 8x8 (se prueban todas las "
			f"permutaciones de filas), se recibió una de {n}x{n}"
		)

	mejor_perm = tuple(range(n))
	mejor_score = -np.inf
	for perm in itertools.permutations(range(n)):
		candidata = matriz_coeficientes[list(perm), :]
		diagonal = np.abs(np.diag(candidata))
		suma_filas = np.sum(np.abs(candidata), axis=1) - diagonal
		score = np.min(diagonal - suma_filas)
		if score > mejor_score:
			mejor_score = score
			mejor_perm = perm

	matriz_reordenada = matriz_coeficientes[list(mejor_perm), :]
	terminos_independientes_reordenados = (
		None
		if terminos_independientes is None
		else np.array(terminos_independientes, dtype=np.float64)[list(mejor_perm)]
	)
	return matriz_reordenada, terminos_independientes_reordenados


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
		Tupla (matriz_coeficientes, terminos_independientes) con la matriz
		y el vector leídos.
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
		matriz_coeficientes: ArrayLike,
		terminos_independientes: ArrayLike,
		aproximacion_inicial: ArrayLike | None = None,
		tolerancia: float = 1e-3,
		maximo_iteraciones: int = 1000,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[NDArray[np.float64], int]:
	"""Resuelve Ax = b con el método iterativo de Gauss-Seidel.

	Args:
		matriz_coeficientes: Matriz de coeficientes A (n x n).
		terminos_independientes: Vector de términos independientes b (n,).
		aproximacion_inicial: Aproximación inicial x0 (n,). Si es None, se
			usa el vector cero.
		tolerancia: Tolerancia para el criterio de convergencia (norma infinito).
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por iteración con
			un `Iteracion(numero, aproximacion, error)`, donde `aproximacion`
			es `tuple(x)` (nunca el array vivo, que el método sigue mutando).

	Returns:
		Tupla (x, iteraciones) con la solución aproximada y el número de
		iteraciones realizadas.

	Raises:
		ValueError: Si A no es cuadrada, las dimensiones no coinciden, o
			algún elemento de la diagonal es cero.
		NoConvergeError: Si no se alcanza la tolerancia en maximo_iteraciones
			iteraciones.
	"""
	matriz_coeficientes = np.array(matriz_coeficientes, dtype=np.float64)
	terminos_independientes = np.array(terminos_independientes, dtype=np.float64)

	n, m = matriz_coeficientes.shape
	if n != m:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {matriz_coeficientes.shape}")
	if terminos_independientes.shape != (n,):
		raise ValueError(f"b debe tener forma ({n},), se recibió {terminos_independientes.shape}")
	if np.any(np.diag(matriz_coeficientes) == 0):
		raise ValueError("La diagonal de A no puede tener ceros")

	x = (
		np.zeros(n)
		if aproximacion_inicial is None
		else np.array(aproximacion_inicial, dtype=np.float64).copy()
	)
	error = np.inf

	for iteracion in range(1, maximo_iteraciones + 1):
		x_anterior = x.copy()
		for i in range(n):
			suma = (
				matriz_coeficientes[i, :i] @ x[:i]
				+ matriz_coeficientes[i, i + 1:] @ x_anterior[i + 1:]
			)
			x[i] = (terminos_independientes[i] - suma) / matriz_coeficientes[i, i]

		error = np.linalg.norm(x - x_anterior, ord=np.inf)
		if reportar_iteracion is not None:
			reportar_iteracion(Iteracion(iteracion, tuple(x), error))
		if error < tolerancia:
			return x, iteracion

	raise NoConvergeError(
		f"No convergió después de {maximo_iteraciones} iteraciones (último error: {error:.5f})"
	)


def main() -> None:
	# Sistema de ejemplo (filas reordenadas para que sea diagonalmente
	# dominante; el orden original no lo era y el método divergía):
	#  12x -  1y + 3z =  8
	#   1x +  7y - 3z = -51
	#   4x -  4y + 9z =  61
	matriz_coeficientes = [
		[12, -1, 3],
		[1, 7, -3],
		[4, -4, 9],
	]
	terminos_independientes = [8, -51, 61]

	print(
		f"¿A es diagonalmente dominante? {es_diagonalmente_dominante(np.array(matriz_coeficientes))}"
	)

	x, iteraciones = gauss_seidel(
		matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
	)
	print(f"Solución: {x}")
	print(f"Iteraciones: {iteraciones}")
	print(f"Verificación (A @ x): {np.array(matriz_coeficientes) @ x}")
	print(f"b original:           {np.array(terminos_independientes)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide sistemas por terminal y los resuelve, uno tras otro.

	Después de cada sistema pregunta si se quiere resolver otro; el proceso
	solo termina cuando la respuesta no es "s".
	"""
	while True:
		matriz_coeficientes, terminos_independientes = leer_matriz_desde_terminal(entrada=entrada)

		if not es_diagonalmente_dominante(matriz_coeficientes):
			print("A no es diagonalmente dominante, reordenando filas...")
			matriz_coeficientes, terminos_independientes = reordenar_para_dominancia_diagonal(
				matriz_coeficientes, terminos_independientes
			)
			if es_diagonalmente_dominante(matriz_coeficientes):
				print("Filas reordenadas: ahora A es diagonalmente dominante.")
			else:
				print("No se encontró un orden diagonalmente dominante; puede no converger.")

		x, iteraciones = gauss_seidel(
			matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
		)
		print(f"Solución: {x}")
		print(f"Iteraciones: {iteraciones}")
		print(f"Verificación (A @ x): {matriz_coeficientes @ x}")

		otro = entrada("¿Resolver otro sistema? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
