"""Método de punto fijo para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from typing import Callable

from metodos_numericos import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
)

__all__ = ["NoConvergeError", "punto_fijo"]


def punto_fijo(
		funcion_g: Callable[[float], float],
		valor_inicial: float,
		tolerancia: float = 1e-3,
		maximo_iteraciones: int = 1000,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[float, int]:
	"""Busca una raíz de f(x) = 0 iterando x_{n+1} = funcion_g(x_n).

	Args:
		funcion_g: Función de iteración `g(x)`, resultado de despejar `x`
			en `f(x) = 0`.
		valor_inicial: Aproximación inicial x0.
		tolerancia: Error máximo aceptado, medido como la diferencia
			absoluta entre dos aproximaciones sucesivas.
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por fila de la
			tabla de la cátedra (i, x_i, g(x_i), |E|), empezando por la fila
			0 del valor inicial: `Iteracion(i, x_i, error, {"valor_g": g(x_i)})`,
			con `error = |x_i - x_(i-1)|` (`None` en la fila 0). Sirve para
			mostrar el progreso en la GUI sin acoplar el
			algoritmo a ninguna de las dos.

	Returns:
		Tupla (raiz, iteraciones) con la raíz aproximada y el número de
		iteraciones realizadas.

	Raises:
		NoConvergeError: Si no se alcanza la tolerancia en
			maximo_iteraciones iteraciones.
	"""
	aproximacion = valor_inicial
	error: float | None = None
	for numero in range(maximo_iteraciones + 1):
		valor_g = funcion_g(aproximacion)
		if reportar_iteracion is not None:
			reportar_iteracion(Iteracion(numero, aproximacion, error, {"valor_g": valor_g}))

		if error is not None and error < tolerancia:
			return aproximacion, numero

		error = abs(valor_g - aproximacion)
		aproximacion = valor_g

	raise NoConvergeError.despues_de(maximo_iteraciones, error)
