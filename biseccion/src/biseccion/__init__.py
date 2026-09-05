"""Método de bisección para encontrar raíces de f(x) = 0."""

from __future__ import annotations

import math
from typing import Callable

from metodos_numericos_base import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	evaluar_funcion,
	imprimir_iteracion,
	leer_funcion_desde_terminal,
)

__all__ = [
	"NoConvergeError",
	"biseccion",
	"evaluar_funcion",
	"funcion_ejemplo",
	"leer_funcion_desde_terminal",
	"leer_intervalo_desde_terminal",
	"main",
	"resolver_desde_terminal",
]


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
		tolerancia: Error máximo aceptado, medido como la mitad del ancho
			del intervalo que todavía contiene la raíz.
		maximo_iteraciones: Número máximo de iteraciones permitidas.
		reportar_iteracion: Si se pasa, se llama una vez por iteración con
			un `Iteracion(numero, aproximacion, error)`. Sirve para mostrar
			el progreso por terminal o en una GUI sin acoplar el algoritmo
			a ninguna de las dos.

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
			"extremo_inferior debe ser menor que extremo_superior, se recibió "
			f"extremo_inferior={extremo_inferior}, extremo_superior={extremo_superior}"
		)

	valor_extremo_inferior = funcion(extremo_inferior)
	valor_extremo_superior = funcion(extremo_superior)

	if valor_extremo_inferior == 0:
		return extremo_inferior, 0
	if valor_extremo_superior == 0:
		return extremo_superior, 0
	if valor_extremo_inferior * valor_extremo_superior > 0:
		raise ValueError(
			"funcion(extremo_inferior) y funcion(extremo_superior) deben tener signos "
			f"opuestos, se recibió {valor_extremo_inferior} y {valor_extremo_superior}"
		)

	error = math.inf
	for iteracion in range(1, maximo_iteraciones + 1):
		punto_medio = (extremo_inferior + extremo_superior) / 2
		valor_punto_medio = funcion(punto_medio)
		error = (extremo_superior - extremo_inferior) / 2
		if reportar_iteracion is not None:
			reportar_iteracion(Iteracion(iteracion, punto_medio, error))

		if valor_punto_medio == 0 or error < tolerancia:
			return punto_medio, iteracion

		if valor_extremo_inferior * valor_punto_medio < 0:
			extremo_superior = punto_medio
		else:
			extremo_inferior = punto_medio
			valor_extremo_inferior = valor_punto_medio

	raise NoConvergeError(
		f"No convergió después de {maximo_iteraciones} iteraciones (último error: {error:.5f})"
	)


def leer_intervalo_desde_terminal(*, entrada: Callable[[str], str] = input) -> tuple[float, float]:
	"""Lee el intervalo [extremo_inferior, extremo_superior] desde terminal.

	Vuelve a pedirlo si extremo_inferior no es menor que extremo_superior.

	Args:
		entrada: Función usada para leer cada línea (por defecto `input`);
			se puede inyectar otra función en los tests.

	Returns:
		Tupla (extremo_inferior, extremo_superior).
	"""
	while True:
		extremo_inferior = float(entrada("Extremo inferior del intervalo: ").strip())
		extremo_superior = float(entrada("Extremo superior del intervalo: ").strip())
		if extremo_inferior < extremo_superior:
			return extremo_inferior, extremo_superior
		print("El extremo inferior debe ser menor que el extremo superior. Probá de nuevo.")


def funcion_ejemplo(valor_x: float) -> float:
	return valor_x**2 - 2


def main() -> None:
	# Ejemplo: raíz de x^2 - 2 en [1, 2], converge a sqrt(2) ≈ 1.41421356
	raiz, iteraciones = biseccion(funcion_ejemplo, 1, 2, reportar_iteracion=imprimir_iteracion)
	print(f"Raíz aproximada: {raiz}")
	print(f"Iteraciones: {iteraciones}")
	print(f"f(raíz) = {funcion_ejemplo(raiz)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide funciones e intervalos por terminal y los resuelve, uno tras otro.

	Después de cada intento pregunta si se quiere resolver otro; el
	proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		funcion, expresion = leer_funcion_desde_terminal(entrada=entrada)
		extremo_inferior, extremo_superior = leer_intervalo_desde_terminal(entrada=entrada)

		try:
			raiz, iteraciones = biseccion(
				funcion, extremo_inferior, extremo_superior, reportar_iteracion=imprimir_iteracion
			)
		except ValueError as error:
			print(f"No se puede aplicar bisección con f(x) = {expresion}: {error}")
		else:
			print(f"Raíz aproximada de f(x) = {expresion}: {raiz}")
			print(f"Iteraciones: {iteraciones}")
			print(f"f(raíz) = {funcion(raiz)}")

		otro = entrada("¿Resolver otra función? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
