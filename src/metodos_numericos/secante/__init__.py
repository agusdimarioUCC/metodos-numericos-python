"""Método de la secante para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from typing import Callable

from metodos_numericos import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	formatear_valor_corto,
)

__all__ = ["NoConvergeError", "secante"]


def secante(
		funcion: Callable[[float], float],
		primera_aproximacion: float,
		segunda_aproximacion: float,
		tolerancia: float = 1e-3,
		maximo_iteraciones: int = 1000,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[float, int]:
	"""Busca una raíz de `funcion` a partir de dos aproximaciones iniciales con la secante.

	Args:
		funcion: Función continua de la que se busca una raíz.
		primera_aproximacion: Primera aproximación inicial x0.
		segunda_aproximacion: Segunda aproximación inicial x1, distinta de x0.
		tolerancia: Error máximo aceptado, medido como la diferencia
			absoluta entre dos aproximaciones sucesivas.
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por fila de la
			tabla de la cátedra (i, x_i, f(x_i), |E|): primero las filas 0 y 1
			de las dos semillas (con `error=None`), y después una por cada
			aproximación nueva, `Iteracion(i, x_i, |x_i - x_(i-1)|,
			{"valor_funcion": f(x_i)})`. Sirve para mostrar el progreso
			en la GUI sin acoplar el algoritmo a ella.

	Returns:
		Tupla (raiz, iteraciones) con la raíz aproximada y el número de
		iteraciones realizadas.

	Raises:
		ValueError: Si `primera_aproximacion` y `segunda_aproximacion` son
			iguales, o si `funcion` toma el mismo valor en dos aproximaciones
			consecutivas, porque la recta secante queda horizontal y no se
			puede seguir dividiendo por su pendiente.
		NoConvergeError: Si no se alcanza la tolerancia en
			maximo_iteraciones iteraciones.
	"""
	if primera_aproximacion == segunda_aproximacion:
		raise ValueError(
			f"x₀ y x₁ tienen que ser distintos (los dos valen {formatear_valor_corto(primera_aproximacion)}): "
			"la secante necesita dos puntos."
		)

	aproximacion_anterior = primera_aproximacion
	aproximacion_actual = segunda_aproximacion
	valor_funcion_anterior = funcion(aproximacion_anterior)
	valor_funcion_actual = funcion(aproximacion_actual)
	if reportar_iteracion is not None:
		reportar_iteracion(Iteracion(0, aproximacion_anterior, None, {"valor_funcion": valor_funcion_anterior}))
		reportar_iteracion(Iteracion(1, aproximacion_actual, None, {"valor_funcion": valor_funcion_actual}))

	error: float | None = None
	for iteracion in range(1, maximo_iteraciones + 1):
		denominador = valor_funcion_actual - valor_funcion_anterior
		if denominador == 0:
			raise ValueError(
				f"f(x) vale lo mismo en x = {formatear_valor_corto(aproximacion_anterior)} y en x = "
				f"{formatear_valor_corto(aproximacion_actual)}: la secante queda horizontal y no corta "
				"al eje. Probá con otras aproximaciones iniciales."
			)
		aproximacion_siguiente = aproximacion_actual - (
			valor_funcion_actual
			* (aproximacion_actual - aproximacion_anterior)
			/ denominador
		)
		error = abs(aproximacion_siguiente - aproximacion_actual)
		valor_funcion_siguiente = funcion(aproximacion_siguiente)
		if reportar_iteracion is not None:
			reportar_iteracion(
				Iteracion(
					iteracion + 1, aproximacion_siguiente, error, {"valor_funcion": valor_funcion_siguiente}
				)
			)

		if error < tolerancia:
			return aproximacion_siguiente, iteracion

		aproximacion_anterior = aproximacion_actual
		valor_funcion_anterior = valor_funcion_actual
		aproximacion_actual = aproximacion_siguiente
		valor_funcion_actual = valor_funcion_siguiente

	raise NoConvergeError.despues_de(maximo_iteraciones, error)
