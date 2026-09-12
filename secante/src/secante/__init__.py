"""Método de la secante para encontrar raíces de f(x) = 0."""

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
	"evaluar_funcion",
	"funcion_ejemplo",
	"leer_funcion_desde_terminal",
	"leer_valor_inicial_desde_terminal",
	"main",
	"resolver_desde_terminal",
	"secante",
]


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
			{"valor_funcion": f(x_i)})`. Sirve para mostrar el progreso por
			terminal o en una GUI sin acoplar el algoritmo a ninguna de las
			dos.

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


def funcion_ejemplo(valor_x: float) -> float:
	return valor_x**2 - 2


def main() -> None:
	# Ejemplo: raíz de x^2 - 2 desde x0 = 1 y x1 = 2, converge a sqrt(2) ≈ 1.41421356
	raiz, iteraciones = secante(funcion_ejemplo, 1, 2, reportar_iteracion=imprimir_iteracion)
	print(f"Raíz aproximada: {raiz}")
	print(f"Iteraciones: {iteraciones}")
	print(f"f(raíz) = {funcion_ejemplo(raiz)}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide f(x) y dos aproximaciones iniciales por terminal y las resuelve, una tras otra.

	Después de cada intento pregunta si se quiere resolver otro; el
	proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		funcion, expresion = leer_funcion_desde_terminal(etiqueta="f(x)", entrada=entrada)
		primera_aproximacion = leer_valor_inicial_desde_terminal(
			etiqueta="Primera aproximación (x0)", entrada=entrada
		)
		segunda_aproximacion = leer_valor_inicial_desde_terminal(
			etiqueta="Segunda aproximación (x1)", entrada=entrada
		)

		try:
			raiz, iteraciones = secante(
				funcion,
				primera_aproximacion,
				segunda_aproximacion,
				reportar_iteracion=imprimir_iteracion,
			)
		except (ValueError, NoConvergeError) as error:
			print(f"No se puede aplicar la secante con f(x) = {expresion}: {error}")
		else:
			print(f"Raíz aproximada de f(x) = {expresion}: {raiz}")
			print(f"Iteraciones: {iteraciones}")
			print(f"f(raíz) = {funcion(raiz)}")

		otro = entrada("¿Resolver otra función? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
