"""Método de bisección para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from typing import Callable

from metodos_numericos import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	formatear_valor_corto,
)

__all__ = ["NoConvergeError", "biseccion"]


def biseccion(
		funcion: Callable[[float], float],
		extremo_inferior: float,
		extremo_superior: float,
		tolerancia: float = 1e-3,
		maximo_iteraciones: int = 1000,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[float, int]:
	"""Busca una raíz de `funcion` en [extremo_inferior, extremo_superior].

	Args:
		funcion: Función continua de la que se busca una raíz.
		extremo_inferior: Punta inferior del intervalo inicial.
		extremo_superior: Punta superior del intervalo inicial.
		tolerancia: Error máximo aceptado, medido como en los apuntes: la
			diferencia |c_k - c_(k-1)| entre dos puntos medios sucesivos
			(que es igual a la mitad del ancho del intervalo actual).
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por iteración con
			un `Iteracion(numero, punto_medio, error, detalle)`, una fila de
			la tabla de la cátedra: `detalle` trae `"extremo_inferior"`,
			`"extremo_superior"`, `"valor_extremo_inferior"`,
			`"valor_punto_medio"` y `"producto"` (f(a)·f(c)). La primera
			fila tiene `error=None` porque todavía no hay un punto medio
			anterior. Sirve para mostrar el progreso en la GUI
			sin acoplar el algoritmo a ella.

	Returns:
		Tupla (raiz, iteraciones) con la raíz aproximada y el número de
		iteraciones realizadas.

	Raises:
		ValueError: Si extremo_inferior >= extremo_superior, o si
			funcion(extremo_inferior) y funcion(extremo_superior) no
			tienen signos opuestos.
		NoConvergeError: Si no se alcanza la tolerancia en
			maximo_iteraciones iteraciones.
	"""
	if extremo_inferior >= extremo_superior:
		raise ValueError(
			f"a tiene que ser menor que b (se recibió a = {formatear_valor_corto(extremo_inferior)}, "
			f"b = {formatear_valor_corto(extremo_superior)})"
		)

	valor_extremo_inferior = funcion(extremo_inferior)
	valor_extremo_superior = funcion(extremo_superior)

	if valor_extremo_inferior == 0:
		return extremo_inferior, 0
	if valor_extremo_superior == 0:
		return extremo_superior, 0
	if valor_extremo_inferior * valor_extremo_superior > 0:
		raise ValueError(
			f"f(a) = {formatear_valor_corto(valor_extremo_inferior)} y "
			f"f(b) = {formatear_valor_corto(valor_extremo_superior)} tienen el mismo signo, así que no "
			"se puede asegurar una raíz en [a; b]. Elegí un intervalo donde f cambie de signo."
		)

	error: float | None = None
	punto_medio_anterior: float | None = None
	for iteracion in range(1, maximo_iteraciones + 1):
		punto_medio = (extremo_inferior + extremo_superior) / 2
		valor_punto_medio = funcion(punto_medio)
		error = None if punto_medio_anterior is None else abs(punto_medio - punto_medio_anterior)
		if reportar_iteracion is not None:
			reportar_iteracion(
				Iteracion(
					iteracion,
					punto_medio,
					error,
					{
						"extremo_inferior": extremo_inferior,
						"extremo_superior": extremo_superior,
						"valor_extremo_inferior": valor_extremo_inferior,
						"valor_punto_medio": valor_punto_medio,
						"producto": valor_extremo_inferior * valor_punto_medio,
					},
				)
			)

		if valor_punto_medio == 0 or (error is not None and error < tolerancia):
			return punto_medio, iteracion
		punto_medio_anterior = punto_medio

		if valor_extremo_inferior * valor_punto_medio < 0:
			extremo_superior = punto_medio
		else:
			extremo_inferior = punto_medio
			valor_extremo_inferior = valor_punto_medio

	raise NoConvergeError.despues_de(maximo_iteraciones, error)
