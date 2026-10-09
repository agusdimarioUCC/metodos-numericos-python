"""Método de Gauss-Seidel para resolver sistemas de ecuaciones lineales Ax = b."""

from __future__ import annotations

import itertools
from typing import Callable

import numpy as np
from metodos_numericos import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	imprimir_iteracion,
	leer_matriz_desde_terminal,
)
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
	"""Verifica si la matriz A es estrictamente diagonalmente dominante por filas.

	Cada fila tiene que cumplir |aᵢᵢ| > Σⱼ≠ᵢ |aᵢⱼ| (con igualdad no alcanza).
	No es una condición necesaria para la convergencia, pero si se cumple,
	la convergencia de Gauss-Seidel está garantizada.
	"""
	diagonal = np.abs(np.diag(matriz_coeficientes))
	suma_filas = np.sum(np.abs(matriz_coeficientes), axis=1) - diagonal
	return bool(np.all(diagonal > suma_filas))


def reordenar_para_dominancia_diagonal(
		matriz_coeficientes: ArrayLike, terminos_independientes: ArrayLike | None = None
) -> tuple[NDArray[np.float64], NDArray[np.float64] | None]:
	"""Reordena las filas de A (y de b, si se da) para lograr dominancia diagonal.

	Las ecuaciones de un sistema se pueden escribir en cualquier orden sin
	cambiar su solución, pero Gauss-Seidel tiene la convergencia garantizada
	cuando esa matriz es estrictamente diagonalmente dominante. Esta función
	prueba todas las permutaciones de filas y devuelve la que maximiza el
	margen mínimo de dominancia (diagonal - suma del resto de la fila).

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
	cantidad_de_filas, cantidad_de_columnas = matriz_coeficientes.shape
	if cantidad_de_filas != cantidad_de_columnas:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {matriz_coeficientes.shape}")
	if cantidad_de_filas > 8:
		raise ValueError(
			"Solo se soportan matrices de hasta 8x8 (se prueban todas las "
			f"permutaciones de filas), se recibió una de {cantidad_de_filas}x{cantidad_de_filas}"
		)

	mejor_permutacion = tuple(range(cantidad_de_filas))
	mejor_margen_minimo = -np.inf
	for permutacion in itertools.permutations(range(cantidad_de_filas)):
		candidata = matriz_coeficientes[list(permutacion), :]
		diagonal = np.abs(np.diag(candidata))
		suma_filas = np.sum(np.abs(candidata), axis=1) - diagonal
		margen_minimo = np.min(diagonal - suma_filas)
		if margen_minimo > mejor_margen_minimo:
			mejor_margen_minimo = margen_minimo
			mejor_permutacion = permutacion

	matriz_reordenada = matriz_coeficientes[list(mejor_permutacion), :]
	terminos_independientes_reordenados = (
		None
		if terminos_independientes is None
		else np.array(terminos_independientes, dtype=np.float64)[list(mejor_permutacion)]
	)
	return matriz_reordenada, terminos_independientes_reordenados


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
		reportar_iteracion: Si se pasa, se llama una vez por fila de la
			tabla de la cátedra (i, X₁, |E₁|, X₂, |E₂|, ...), empezando por la
			fila 0 de la aproximación inicial (con `error=None`):
			`Iteracion(i, tuple(aproximacion), error, detalle)`, donde la
			aproximación va como tupla (nunca el array vivo, que el método
			sigue mutando), `error` es la norma infinito de la diferencia con
			la fila anterior y `detalle` trae `"componente_j"` (x_j) y
			`"error_j"` (|x_j - x_j anterior|) para j = 1..n.

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

	cantidad_de_filas, cantidad_de_columnas = matriz_coeficientes.shape
	if cantidad_de_filas != cantidad_de_columnas:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {matriz_coeficientes.shape}")
	if terminos_independientes.shape != (cantidad_de_filas,):
		raise ValueError(
			f"b debe tener forma ({cantidad_de_filas},), se recibió {terminos_independientes.shape}"
		)
	if np.any(np.diag(matriz_coeficientes) == 0):
		raise ValueError(
			"La diagonal de A no puede tener ceros: cada xᵢ se despeja dividiendo por aᵢᵢ. "
			"Reordená las ecuaciones."
		)

	aproximacion = (
		np.zeros(cantidad_de_filas)
		if aproximacion_inicial is None
		else np.array(aproximacion_inicial, dtype=np.float64).copy()
	)
	error: float | None = None
	if reportar_iteracion is not None:
		reportar_iteracion(Iteracion(0, tuple(aproximacion), None, _detalle_de_fila(aproximacion, None)))

	for iteracion in range(1, maximo_iteraciones + 1):
		aproximacion_anterior = aproximacion.copy()
		for fila in range(cantidad_de_filas):
			suma = (
				matriz_coeficientes[fila, :fila] @ aproximacion[:fila]
				+ matriz_coeficientes[fila, fila + 1:] @ aproximacion_anterior[fila + 1:]
			)
			aproximacion[fila] = (terminos_independientes[fila] - suma) / matriz_coeficientes[fila, fila]

		errores_por_componente = np.abs(aproximacion - aproximacion_anterior)
		error = float(np.max(errores_por_componente))
		if reportar_iteracion is not None:
			reportar_iteracion(
				Iteracion(
					iteracion, tuple(aproximacion), error, _detalle_de_fila(aproximacion, errores_por_componente)
				)
			)
		if error < tolerancia:
			return aproximacion, iteracion

	raise NoConvergeError.despues_de(maximo_iteraciones, error)


def _detalle_de_fila(
		aproximacion: NDArray[np.float64], errores_por_componente: NDArray[np.float64] | None
) -> dict[str, float | None]:
	"""Arma el `detalle` de una fila de la tabla: x_j y |E_j| de cada componente, numerados desde 1."""
	detalle: dict[str, float | None] = {}
	for indice, componente in enumerate(aproximacion, start=1):
		detalle[f"componente_{indice}"] = float(componente)
		detalle[f"error_{indice}"] = (
			None if errores_por_componente is None else float(errores_por_componente[indice - 1])
		)
	return detalle


def main() -> None:
	"""Resuelve el sistema de ejemplo fijo e imprime la tabla, la solución y la verificación A·x."""
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

	solucion, iteraciones = gauss_seidel(
		matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
	)
	print(f"Solución: {solucion}")
	print(f"Iteraciones: {iteraciones}")
	print(f"Verificación (A @ x): {np.array(matriz_coeficientes) @ solucion}")
	print(f"b original:           {np.array(terminos_independientes)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide sistemas por terminal y los resuelve, uno tras otro.

	Si el sistema no se puede resolver (diagonal con ceros, no converge,
	etc.) muestra el motivo y sigue. Después de cada sistema pregunta si se
	quiere resolver otro; el proceso solo termina cuando la respuesta no es
	"s".
	"""
	while True:
		filas, terminos_independientes = leer_matriz_desde_terminal(entrada=entrada)
		matriz_coeficientes = np.array(filas, dtype=np.float64)

		try:
			if not es_diagonalmente_dominante(matriz_coeficientes):
				print("A no es diagonalmente dominante, reordenando filas...")
				matriz_coeficientes, terminos_independientes = reordenar_para_dominancia_diagonal(
					matriz_coeficientes, terminos_independientes
				)
				if es_diagonalmente_dominante(matriz_coeficientes):
					print("Filas reordenadas: ahora A es diagonalmente dominante.")
				else:
					print("No se encontró un orden diagonalmente dominante; puede no converger.")

			solucion, iteraciones = gauss_seidel(
				matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
			)
		except (ValueError, NoConvergeError) as error:
			print(f"No se puede aplicar Gauss-Seidel: {error}")
		else:
			print(f"Solución: {solucion}")
			print(f"Iteraciones: {iteraciones}")
			print(f"Verificación (A @ x): {matriz_coeficientes @ solucion}")

		otro = entrada("¿Resolver otro sistema? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
