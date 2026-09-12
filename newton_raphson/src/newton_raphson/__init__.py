"""Método de Newton-Raphson para encontrar raíces de f(x) = 0."""

from __future__ import annotations

from typing import Callable

from metodos_numericos_base import (
	Iteracion,
	NoConvergeError,
	ReportarIteracion,
	evaluar_funcion,
	formatear_valor_corto,
	imprimir_iteracion,
	leer_funcion_desde_terminal,
	leer_valor_inicial_desde_terminal,
)

__all__ = [
	"NoConvergeError",
	"derivada_ejemplo",
	"evaluar_funcion",
	"funcion_ejemplo",
	"leer_funcion_desde_terminal",
	"leer_valor_inicial_desde_terminal",
	"main",
	"newton_raphson",
	"resolver_desde_terminal",
]


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
			mostrar el progreso por terminal o en una GUI sin acoplar el
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


def funcion_ejemplo(valor_x: float) -> float:
	return valor_x**2 - 2


def derivada_ejemplo(valor_x: float) -> float:
	return 2 * valor_x


def main() -> None:
	# Ejemplo: raíz de x^2 - 2 desde x0 = 1.5, converge a sqrt(2) ≈ 1.41421356
	raiz, iteraciones = newton_raphson(
		funcion_ejemplo, derivada_ejemplo, 1.5, reportar_iteracion=imprimir_iteracion
	)
	print(f"Raíz aproximada: {raiz}")
	print(f"Iteraciones: {iteraciones}")
	print(f"f(raíz) = {funcion_ejemplo(raiz)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide f(x), f'(x) y un valor inicial por terminal y los resuelve, uno tras otro.

	Después de cada intento pregunta si se quiere resolver otro; el
	proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		funcion, expresion_funcion = leer_funcion_desde_terminal(etiqueta="f(x)", entrada=entrada)
		derivada, expresion_derivada = leer_funcion_desde_terminal(etiqueta="f'(x)", entrada=entrada)
		valor_inicial = leer_valor_inicial_desde_terminal(
			etiqueta="Valor inicial (x0)", entrada=entrada
		)

		try:
			raiz, iteraciones = newton_raphson(
				funcion, derivada, valor_inicial, reportar_iteracion=imprimir_iteracion
			)
		except (ValueError, NoConvergeError) as error:
			print(f"No se puede aplicar Newton-Raphson con f(x) = {expresion_funcion}: {error}")
		else:
			print(f"Raíz aproximada de f(x) = {expresion_funcion}: {raiz}")
			print(f"Iteraciones: {iteraciones}")
			print(f"f(raíz) = {funcion(raiz)}")

		otro = entrada("¿Resolver otra función? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
