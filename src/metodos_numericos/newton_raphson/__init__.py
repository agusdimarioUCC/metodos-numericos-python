"""Método de Newton-Raphson para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from typing import Callable

from metodos_numericos import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	formatear_valor_corto,
)

__all__ = ["NoConvergeError", "newton_raphson"]


def newton_raphson(
		funcion: Callable[[float], float],
		derivada: Callable[[float], float],
		valor_inicial: float,
		tolerancia: float = 1e-3,
		maximo_iteraciones: int = 1000,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[float, int]:
	"""Busca una raíz de `funcion` a partir de `valor_inicial` con Newton-Raphson.

	Args:
		funcion: Función continua y derivable de la que se busca una raíz.
		derivada: Derivada de `funcion`, provista por el usuario (no se
			deriva simbólicamente).
		valor_inicial: Aproximación inicial x0 de la que parte el método.
		tolerancia: Error máximo aceptado, medido como la diferencia
			absoluta entre dos aproximaciones sucesivas.
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por fila de la
			tabla de la cátedra (i, x_i, f(x_i), f'(x_i), |E|), empezando por
			la fila 0 de x0: `Iteracion(i, x_i, error, {"valor_funcion": f(x_i),
			"valor_derivada": f'(x_i)})` con `error = |x_i - x_(i-1)|` (`None`
			en la fila 0). La última fila, la de la raíz, no trae `detalle`:
			como en los apuntes, f y f' ya no se evalúan ahí. Sirve para
			mostrar el progreso en la GUI sin acoplar el
			algoritmo a ninguna de las dos.

	Returns:
		Tupla (raiz, iteraciones) con la raíz aproximada y el número de
		iteraciones realizadas.

	Raises:
		ValueError: Si `derivada` se anula en alguna aproximación, porque
			no se puede seguir dividiendo por cero.
		NoConvergeError: Si no se alcanza la tolerancia en
			maximo_iteraciones iteraciones.
	"""
	aproximacion_actual = valor_inicial
	error: float | None = None
	for iteracion in range(1, maximo_iteraciones + 1):
		valor_funcion = funcion(aproximacion_actual)
		valor_derivada = derivada(aproximacion_actual)
		if reportar_iteracion is not None:
			reportar_iteracion(
				Iteracion(
					iteracion - 1,
					aproximacion_actual,
					error,
					{"valor_funcion": valor_funcion, "valor_derivada": valor_derivada},
				)
			)
		if valor_derivada == 0:
			raise ValueError(
				f"f'(x) se anula en x = {formatear_valor_corto(aproximacion_actual)}: la tangente es "
				"horizontal y no corta al eje. Probá con otro valor inicial."
			)
		aproximacion_siguiente = aproximacion_actual - valor_funcion / valor_derivada
		error = abs(aproximacion_siguiente - aproximacion_actual)

		if error < tolerancia:
			if reportar_iteracion is not None:
				reportar_iteracion(Iteracion(iteracion, aproximacion_siguiente, error))
			return aproximacion_siguiente, iteracion

		aproximacion_actual = aproximacion_siguiente

	raise NoConvergeError.despues_de(maximo_iteraciones, error)
