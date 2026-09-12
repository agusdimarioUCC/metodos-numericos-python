"""Método de punto fijo para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from math import sqrt
from typing import Callable

from metodos_numericos_base import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	evaluar_funcion,
	imprimir_iteracion,
	leer_funcion_desde_terminal,
	leer_valor_inicial_desde_terminal,
)

__all__ = [
	"NoConvergeError",
	"evaluar_funcion",
	"funcion_ejemplo_g",
	"leer_funcion_desde_terminal",
	"leer_valor_inicial_desde_terminal",
	"main",
	"punto_fijo",
	"resolver_desde_terminal",
]


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
			mostrar el progreso por terminal o en una GUI sin acoplar el
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


def funcion_ejemplo_g(valor_x: float) -> float:
	return sqrt(valor_x + 2)


def main() -> None:
	# Ejemplo: raíz de x^2 - x - 2 = 0 despejada como g(x) = sqrt(x + 2),
	# converge a x=2 partiendo de x0=1.5.
	raiz, iteraciones = punto_fijo(funcion_ejemplo_g, 1.5, reportar_iteracion=imprimir_iteracion)
	print(f"Raíz aproximada: {raiz}")
	print(f"Iteraciones: {iteraciones}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide g(x) y un valor inicial por terminal y los resuelve, uno tras otro.

	Después de cada intento pregunta si se quiere resolver otro; el
	proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		funcion_g, expresion = leer_funcion_desde_terminal(etiqueta="g(x)", entrada=entrada)
		valor_inicial = leer_valor_inicial_desde_terminal(
			etiqueta="Valor inicial (x0)", entrada=entrada
		)

		try:
			raiz, iteraciones = punto_fijo(
				funcion_g, valor_inicial, reportar_iteracion=imprimir_iteracion
			)
		except NoConvergeError as error:
			print(f"No se pudo aplicar punto fijo con g(x) = {expresion}: {error}")
		else:
			print(f"Raíz aproximada de g(x) = {expresion}: {raiz}")
			print(f"Iteraciones: {iteraciones}")

		otro = entrada("¿Resolver otra función? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
