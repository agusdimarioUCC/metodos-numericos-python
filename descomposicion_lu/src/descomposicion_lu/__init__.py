"""Descomposición LU: resuelve Ax = b, invierte A y evalúa su condición."""

from __future__ import annotations

from typing import Callable

import numpy as np
from metodos_numericos_base import Iteracion, ReportarIteracion, imprimir_iteracion
from numpy.typing import ArrayLike, NDArray

__all__ = [
	"calcular_inversa",
	"descomponer_lu",
	"descomposicion_lu",
	"leer_matriz_desde_terminal",
	"main",
	"norma_renglon_suma",
	"numero_de_condicion",
	"resolver_con_lu",
	"resolver_desde_terminal",
	"sustitucion_adelante",
	"sustitucion_atras",
]


def descomponer_lu(
		matriz_coeficientes: ArrayLike,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
	"""Descompone A en L (triangular inferior, diagonal 1) y U (triangular superior).

	Implementa la descomposición de Doolittle tal como surge de la
	eliminación de Gauss (ecuaciones 10.9-10.11): los factores usados para
	anular cada elemento bajo la diagonal se guardan en L en vez de
	descartarse. No hace pivoteo.

	Args:
		matriz_coeficientes: Matriz de coeficientes A (n x n).
		reportar_iteracion: Si se pasa, se llama una vez por columna pivote
			(el "PASO" de la eliminación Gaussiana) con un
			Iteracion(numero_de_paso, multiplicadores_de_ese_paso, error),
			donde multiplicadores_de_ese_paso son los l_ij recién calculados
			bajo la diagonal en esa columna. Este método es directo (no
			iterativo/convergente), así que error siempre es 0.0: el campo
			solo existe para cumplir el contrato de Iteracion, no porque
			haya un error de convergencia que reportar.

	Returns:
		Tupla (triangular_inferior, triangular_superior) tal que
		A = triangular_inferior @ triangular_superior.

	Raises:
		ValueError: Si A no es cuadrada o si aparece un pivote cero (este
			método no pivotea para evitarlo).
	"""
	triangular_superior = np.array(matriz_coeficientes, dtype=np.float64)
	n, m = triangular_superior.shape
	if n != m:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {triangular_superior.shape}")

	triangular_inferior = np.eye(n)
	for columna_pivote in range(n - 1):
		pivote = triangular_superior[columna_pivote, columna_pivote]
		if pivote == 0:
			raise ValueError(
				f"Apareció un pivote cero en a{columna_pivote + 1}{columna_pivote + 1} y este método "
				"no intercambia filas. Reordená las ecuaciones para que no haya ceros en la diagonal."
			)
		for fila in range(columna_pivote + 1, n):
			factor = triangular_superior[fila, columna_pivote] / pivote
			triangular_inferior[fila, columna_pivote] = factor
			triangular_superior[fila, columna_pivote:] -= (
				factor * triangular_superior[columna_pivote, columna_pivote:]
			)

		if reportar_iteracion is not None:
			multiplicadores_de_este_paso = tuple(triangular_inferior[columna_pivote + 1:, columna_pivote])
			reportar_iteracion(Iteracion(columna_pivote + 1, multiplicadores_de_este_paso, 0.0))

	return triangular_inferior, triangular_superior


def sustitucion_adelante(
		triangular_inferior: ArrayLike, terminos_independientes: ArrayLike
) -> NDArray[np.float64]:
	"""Resuelve L d = b por sustitución hacia adelante (ecuación 10.12).

	Asume que triangular_inferior tiene unos en la diagonal, como la que
	produce descomponer_lu.
	"""
	triangular_inferior = np.array(triangular_inferior, dtype=np.float64)
	terminos_independientes = np.array(terminos_independientes, dtype=np.float64)
	n = triangular_inferior.shape[0]

	vector_intermedio = np.zeros(n)
	for i in range(n):
		vector_intermedio[i] = terminos_independientes[i] - triangular_inferior[i, :i] @ vector_intermedio[:i]

	return vector_intermedio


def sustitucion_atras(
		triangular_superior: ArrayLike, terminos_independientes: ArrayLike
) -> NDArray[np.float64]:
	"""Resuelve U x = d por sustitución hacia atrás (ecuaciones 10.13-10.14)."""
	triangular_superior = np.array(triangular_superior, dtype=np.float64)
	terminos_independientes = np.array(terminos_independientes, dtype=np.float64)
	n = triangular_superior.shape[0]

	x = np.zeros(n)
	for i in range(n - 1, -1, -1):
		x[i] = (
			terminos_independientes[i] - triangular_superior[i, i + 1:] @ x[i + 1:]
		) / triangular_superior[i, i]

	return x


def resolver_con_lu(
		triangular_inferior: ArrayLike, triangular_superior: ArrayLike, terminos_independientes: ArrayLike
) -> NDArray[np.float64]:
	"""Resuelve Ax = b a partir de una descomposición A = LU ya calculada.

	Encadena la sustitución hacia adelante (L d = b) con la sustitución
	hacia atrás (U x = d), como en la figura 10.1 del libro.
	"""
	vector_intermedio = sustitucion_adelante(triangular_inferior, terminos_independientes)
	return sustitucion_atras(triangular_superior, vector_intermedio)


def calcular_inversa(
		matriz_coeficientes: ArrayLike, reportar_iteracion: ReportarIteracion | None = None
) -> tuple[NDArray[np.float64], int]:
	"""Calcula A⁻¹ resolviendo Ax = e_i columna por columna (sección 10.2.1).

	Descompone A una sola vez y reutiliza L y U para resolver un sistema
	por cada vector unitario e_i, lo cual es mucho más barato que repetir
	la eliminación completa n veces.

	Args:
		matriz_coeficientes: Matriz de coeficientes A (n x n).
		reportar_iteracion: Si se pasa, se llama una vez por columna
			calculada con un Iteracion(numero_de_columna, columna_de_la_inversa,
			error), donde error es el residuo máximo ‖A @ columna - e_i‖∞
			(cuadro 10.1).

	Returns:
		Tupla (inversa, n) con A⁻¹ y la cantidad de columnas calculadas.
	"""
	matriz_coeficientes = np.array(matriz_coeficientes, dtype=np.float64)
	n = matriz_coeficientes.shape[0]
	triangular_inferior, triangular_superior = descomponer_lu(matriz_coeficientes)

	inversa = np.zeros((n, n))
	for columna in range(n):
		vector_unitario = np.zeros(n)
		vector_unitario[columna] = 1.0
		columna_de_la_inversa = resolver_con_lu(triangular_inferior, triangular_superior, vector_unitario)
		inversa[:, columna] = columna_de_la_inversa

		if reportar_iteracion is not None:
			error = float(np.max(np.abs(matriz_coeficientes @ columna_de_la_inversa - vector_unitario)))
			reportar_iteracion(Iteracion(columna + 1, tuple(columna_de_la_inversa), error))

	return inversa, n


def norma_renglon_suma(matriz: ArrayLike) -> float:
	"""Norma matricial uniforme o renglón-suma (ecuación 10.25).

	Suma los valores absolutos de cada fila y toma la mayor de esas sumas.
	"""
	matriz = np.array(matriz, dtype=np.float64)
	return float(np.max(np.sum(np.abs(matriz), axis=1)))


def numero_de_condicion(matriz_coeficientes: ArrayLike, inversa: ArrayLike) -> float:
	"""Cond[A] = ‖A‖·‖A⁻¹‖ con la norma renglón-suma (ecuación 10.26).

	Un valor considerablemente mayor que 1 indica que el sistema está mal
	condicionado (sección 10.3).
	"""
	return norma_renglon_suma(matriz_coeficientes) * norma_renglon_suma(inversa)


def descomposicion_lu(
		matriz_coeficientes: ArrayLike,
		terminos_independientes: ArrayLike,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float, int]:
	"""Resuelve Ax = b por descomposición LU y evalúa A⁻¹ y su condición.

	Args:
		matriz_coeficientes: Matriz de coeficientes A (n x n).
		terminos_independientes: Vector de términos independientes b (n,).
		reportar_iteracion: Si se pasa, se llama una vez por columna de A⁻¹
			calculada (ver calcular_inversa).

	Returns:
		Tupla (x, inversa, condicion, iteraciones) con la solución de
		Ax = b, la matriz inversa A⁻¹, el número de condición Cond[A] y la
		cantidad de columnas de la inversa calculadas (= n).

	Raises:
		ValueError: Si A no es cuadrada, las dimensiones no coinciden, o
			aparece un pivote cero durante la descomposición.
	"""
	matriz_coeficientes = np.array(matriz_coeficientes, dtype=np.float64)
	terminos_independientes = np.array(terminos_independientes, dtype=np.float64)

	n, m = matriz_coeficientes.shape
	if n != m:
		raise ValueError(f"La matriz A debe ser cuadrada, se recibió {matriz_coeficientes.shape}")
	if terminos_independientes.shape != (n,):
		raise ValueError(f"b debe tener forma ({n},), se recibió {terminos_independientes.shape}")

	triangular_inferior, triangular_superior = descomponer_lu(
		matriz_coeficientes, reportar_iteracion=reportar_iteracion
	)
	x = resolver_con_lu(triangular_inferior, triangular_superior, terminos_independientes)

	inversa, iteraciones = calcular_inversa(matriz_coeficientes, reportar_iteracion=reportar_iteracion)
	condicion = numero_de_condicion(matriz_coeficientes, inversa)

	return x, inversa, condicion, iteraciones


def leer_matriz_desde_terminal(
		n: int | None = None, *, entrada: Callable[[str], str] = input
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
	"""Lee interactivamente el sistema A x = b desde la terminal.

	Pide el tamaño del sistema (si no se pasa n) y luego, fila por fila,
	los coeficientes de A separados por espacios y el término independiente
	b correspondiente. Si una fila no tiene la cantidad de valores
	esperada, vuelve a pedirla.

	Args:
		n: Tamaño del sistema (n x n). Si es None, se pregunta al usuario.
		entrada: Función usada para leer cada línea (por defecto input); se
			puede inyectar otra función en los tests.

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
		filas.append([float(valor) for valor in valores])
		valores_b.append(float(entrada(f"b[{i + 1}]: ").strip()))

	return np.array(filas, dtype=np.float64), np.array(valores_b, dtype=np.float64)


def main() -> None:
	# Ejemplos 10.1-10.3 del libro.
	matriz_coeficientes = [
		[3, -0.1, -0.2],
		[0.1, 7, -0.3],
		[0.3, -0.2, 10],
	]
	terminos_independientes = [7.85, -19.3, 71.4]

	x, inversa, condicion, iteraciones = descomposicion_lu(
		matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
	)
	print(f"Solución: {x}")
	print(f"Inversa:\n{inversa}")
	print(f"Número de condición: {condicion:.5f}")
	print(f"Columnas de la inversa calculadas: {iteraciones}")
	print(f"Verificación (A @ x): {np.array(matriz_coeficientes) @ x}")
	print(f"b original:           {np.array(terminos_independientes)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide sistemas por terminal y los resuelve, uno tras otro.

	Después de cada sistema pregunta si se quiere resolver otro; el
	proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		matriz_coeficientes, terminos_independientes = leer_matriz_desde_terminal(entrada=entrada)

		x, inversa, condicion, iteraciones = descomposicion_lu(
			matriz_coeficientes, terminos_independientes, reportar_iteracion=imprimir_iteracion
		)
		print(f"Solución: {x}")
		print(f"Inversa:\n{inversa}")
		print(f"Número de condición: {condicion:.5f}")
		print(f"Columnas de la inversa calculadas: {iteraciones}")
		print(f"Verificación (A @ x): {matriz_coeficientes @ x}")

		otro = entrada("¿Resolver otro sistema? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
