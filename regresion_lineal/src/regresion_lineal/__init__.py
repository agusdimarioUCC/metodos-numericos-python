"""Regresión lineal por mínimos cuadrados, con linealización de modelos no lineales.

Ajusta y = a₀ + a₁x a un conjunto de puntos (xᵢ, yᵢ), o una versión
linealizada de un modelo exponencial, potencial o de crecimiento, según
el modelo elegido:

- Lineal:       y = a₀ + a₁x                    (directo, sin linealizar)
- Exponencial:  y = A·e^(Bx)  → Ln y = Ln A + Bx  (u=x, v=Ln y)
- Potencial:    y = A·x^B     → Log y = Log A + B·Log x  (u=Log x, v=Log y)
- Crecimiento:  y = A·x/(b+x) → 1/y = 1/A + (b/A)·(1/x)  (u=1/x, v=1/y)
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Callable

from metodos_numericos_base import (
	Iteracion,
	ReportarIteracion,
	imprimir_iteracion,
	leer_opcion_desde_terminal,
	leer_puntos_desde_terminal,
)

MODELOS_DISPONIBLES: tuple[str, ...] = ("Lineal", "Exponencial", "Potencial", "Crecimiento")

__all__ = [
	"MODELOS_DISPONIBLES",
	"ajuste_lineal",
	"main",
	"regresion_lineal",
	"resolver_desde_terminal",
]


def ajuste_lineal(valores_u: Sequence[float], valores_v: Sequence[float]) -> tuple[float, float]:
	"""Ajusta v = ordenada_al_origen + pendiente·u por mínimos cuadrados a n pares (u, v).

	Args:
		valores_u: Las abscisas del ajuste lineal (para el modelo lineal,
			son directamente los Xᵢ; para uno linealizado, ya transformados).
		valores_v: Las ordenadas del ajuste lineal, en la misma correspondencia.

	Returns:
		Tupla (ordenada_al_origen, pendiente) = (a₀, a₁) de los apuntes.

	Raises:
		ValueError: Si `valores_u`/`valores_v` no tienen la misma longitud,
			si hay menos de 2 puntos, o si todos los uᵢ son iguales (el
			denominador de a₁ da cero).
	"""
	if len(valores_u) != len(valores_v):
		raise ValueError(
			f"u y v tienen que tener la misma cantidad de valores (u tiene {len(valores_u)}, "
			f"v tiene {len(valores_v)})."
		)
	cantidad = len(valores_u)
	if cantidad < 2:
		raise ValueError(f"Hacen falta al menos 2 puntos para ajustar una recta (se recibieron {cantidad}).")

	suma_u = sum(valores_u)
	suma_v = sum(valores_v)
	suma_uv = sum(valor_u * valor_v for valor_u, valor_v in zip(valores_u, valores_v))
	suma_u_cuadrado = sum(valor_u**2 for valor_u in valores_u)

	denominador = cantidad * suma_u_cuadrado - suma_u**2
	if denominador == 0:
		raise ValueError(
			"Todos los valores de u son iguales: no se puede ajustar una recta (la pendiente queda indefinida)."
		)

	pendiente = (cantidad * suma_uv - suma_u * suma_v) / denominador
	promedio_u = suma_u / cantidad
	promedio_v = suma_v / cantidad
	ordenada_al_origen = promedio_v - pendiente * promedio_u
	return ordenada_al_origen, pendiente


def _linealizar(
		tipo_modelo: str, valores_x: Sequence[float], valores_y: Sequence[float]
) -> tuple[list[float], list[float]]:
	"""Transforma (xᵢ, yᵢ) al par (uᵢ, vᵢ) que se ajusta linealmente, según el modelo."""
	if tipo_modelo == "Lineal":
		return list(valores_x), list(valores_y)
	if tipo_modelo == "Exponencial":
		if any(valor_y <= 0 for valor_y in valores_y):
			raise ValueError(
				"El modelo exponencial (y = A·e^(Bx)) necesita que todos los Yᵢ sean positivos "
				"(para poder calcular Ln Yᵢ)."
			)
		return list(valores_x), [math.log(valor_y) for valor_y in valores_y]
	if tipo_modelo == "Potencial":
		if any(valor_x <= 0 for valor_x in valores_x):
			raise ValueError(
				"El modelo potencial (y = A·xᴮ) necesita que todos los Xᵢ sean positivos "
				"(para poder calcular Log Xᵢ)."
			)
		if any(valor_y <= 0 for valor_y in valores_y):
			raise ValueError(
				"El modelo potencial (y = A·xᴮ) necesita que todos los Yᵢ sean positivos "
				"(para poder calcular Log Yᵢ)."
			)
		return [math.log10(valor_x) for valor_x in valores_x], [math.log10(valor_y) for valor_y in valores_y]
	if tipo_modelo == "Crecimiento":
		if any(valor_x == 0 for valor_x in valores_x):
			raise ValueError(
				"El modelo de crecimiento (y = A·x/(b+x)) necesita que ningún Xᵢ sea cero "
				"(para poder calcular 1/Xᵢ)."
			)
		if any(valor_y == 0 for valor_y in valores_y):
			raise ValueError(
				"El modelo de crecimiento (y = A·x/(b+x)) necesita que ningún Yᵢ sea cero "
				"(para poder calcular 1/Yᵢ)."
			)
		return [1 / valor_x for valor_x in valores_x], [1 / valor_y for valor_y in valores_y]
	raise ValueError(f"Modelo desconocido: '{tipo_modelo}'. Los modelos disponibles son: {', '.join(MODELOS_DISPONIBLES)}.")


def _armar_resultado(
		tipo_modelo: str, ordenada_al_origen: float, pendiente: float
) -> tuple[dict[str, float], Callable[[float], float]]:
	"""Vuelve del espacio linealizado al espacio original: parámetros del modelo y f(x) = y."""
	parametros: dict[str, float] = {"a0": ordenada_al_origen, "a1": pendiente}
	if tipo_modelo == "Lineal":
		return parametros, lambda valor_x: ordenada_al_origen + pendiente * valor_x
	if tipo_modelo == "Exponencial":
		amplitud = math.exp(ordenada_al_origen)
		exponente = pendiente
		parametros["A"] = amplitud
		parametros["B"] = exponente
		return parametros, lambda valor_x: amplitud * math.exp(exponente * valor_x)
	if tipo_modelo == "Potencial":
		amplitud = 10**ordenada_al_origen
		exponente = pendiente
		parametros["A"] = amplitud
		parametros["B"] = exponente
		return parametros, lambda valor_x: amplitud * valor_x**exponente
	if tipo_modelo == "Crecimiento":
		if ordenada_al_origen == 0:
			raise ValueError("El ajuste dio a₀ = 0: no se puede despejar A = 1/a₀ del modelo de crecimiento.")
		amplitud = 1 / ordenada_al_origen
		asintota = pendiente * amplitud
		parametros["A"] = amplitud
		parametros["b"] = asintota
		return parametros, lambda valor_x: amplitud * valor_x / (asintota + valor_x)
	raise ValueError(f"Modelo desconocido: '{tipo_modelo}'.")


def regresion_lineal(
		tipo_modelo: str,
		valores_x: Sequence[float],
		valores_y: Sequence[float],
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[dict[str, float], Callable[[float], float]]:
	"""Ajusta el modelo elegido a (xᵢ, yᵢ) por mínimos cuadrados, linealizando si hace falta.

	Args:
		tipo_modelo: Uno de `MODELOS_DISPONIBLES` ("Lineal", "Exponencial",
			"Potencial" o "Crecimiento").
		valores_x: Las abscisas de los puntos, sin transformar.
		valores_y: Las ordenadas de los puntos, sin transformar.
		reportar_iteracion: Si se pasa, se llama una vez por punto con
			`Iteracion(i, (xᵢ, yᵢ), None, detalle)`, donde `detalle` trae
			`valor_x`, `valor_y` y el par linealizado `u`, `v` (junto con
			`u_cuadrado` y `uv`) que arma la tabla de sumatorias de los
			apuntes — el mismo `detalle` sirve para cualquier modelo, y
			GUI/terminal deciden qué columnas mostrar según `tipo_modelo`.

	Returns:
		Tupla (parametros, funcion): `parametros` siempre trae `"a0"`/`"a1"`
		(los coeficientes de la recta ajustada en el espacio linealizado) y,
		si el modelo no es lineal, además `"A"` y `"B"` (o `"b"` para
		Crecimiento) en el espacio original. `funcion` es y = f(x) ya en el
		espacio original, lista para graficar o evaluar.

	Raises:
		ValueError: Si `valores_x`/`valores_y` no tienen la misma longitud,
			si hay menos de 2 puntos, si el modelo no está en
			`MODELOS_DISPONIBLES`, o si los datos no cumplen lo que el
			modelo elegido necesita (Yᵢ positivos para Exponencial, Xᵢ e Yᵢ
			positivos para Potencial, Xᵢ e Yᵢ no nulos para Crecimiento).
	"""
	if len(valores_x) != len(valores_y):
		raise ValueError(
			f"x e y tienen que tener la misma cantidad de valores (x tiene {len(valores_x)}, "
			f"y tiene {len(valores_y)})."
		)
	if len(valores_x) < 2:
		raise ValueError(f"Hacen falta al menos 2 puntos para ajustar un modelo (se recibieron {len(valores_x)}).")

	valores_u, valores_v = _linealizar(tipo_modelo, valores_x, valores_y)
	ordenada_al_origen, pendiente = ajuste_lineal(valores_u, valores_v)
	parametros, funcion = _armar_resultado(tipo_modelo, ordenada_al_origen, pendiente)

	if reportar_iteracion is not None:
		for indice, (valor_x, valor_y, valor_u, valor_v) in enumerate(
				zip(valores_x, valores_y, valores_u, valores_v), start=1
		):
			detalle = {
				"valor_x": valor_x,
				"valor_y": valor_y,
				"u": valor_u,
				"v": valor_v,
				"u_cuadrado": valor_u**2,
				"uv": valor_u * valor_v,
			}
			reportar_iteracion(Iteracion(indice, (valor_x, valor_y), None, detalle))

	return parametros, funcion


def main() -> None:
	# Ejemplo: ejercicio 1.1 de la guía, ajuste lineal a 7 puntos, converge a y = 0,8393x + 0,0714
	valores_x = [1, 2, 3, 4, 5, 6, 7]
	valores_y = [0.5, 2.5, 2.0, 4.0, 3.5, 6.0, 5.5]
	parametros, _ = regresion_lineal("Lineal", valores_x, valores_y, reportar_iteracion=imprimir_iteracion)
	print(f"a₀ = {parametros['a0']:.4f}")
	print(f"a₁ = {parametros['a1']:.4f}")
	print(f"y = {parametros['a1']:.4f}x + {parametros['a0']:.4f}")


def resolver_desde_terminal(*, entrada: Callable[[str], str] = input) -> None:
	"""Pide el modelo y los puntos por terminal y los ajusta, uno tras otro.

	Después de cada intento pregunta si se quiere ajustar otro conjunto de
	puntos; el proceso solo termina cuando la respuesta no es "s".
	"""
	while True:
		tipo_modelo = leer_opcion_desde_terminal("Modelo", MODELOS_DISPONIBLES, entrada=entrada)
		valores_x, valores_y = leer_puntos_desde_terminal(entrada=entrada)

		try:
			parametros, _ = regresion_lineal(
				tipo_modelo, valores_x, valores_y, reportar_iteracion=imprimir_iteracion
			)
		except ValueError as error:
			print(f"No se puede ajustar el modelo {tipo_modelo}: {error}")
		else:
			print(f"a₀ = {parametros['a0']:.4f}, a₁ = {parametros['a1']:.4f}")
			if tipo_modelo != "Lineal":
				segundo_parametro = "b" if tipo_modelo == "Crecimiento" else "B"
				print(f"A = {parametros['A']:.4f}, {segundo_parametro} = {parametros[segundo_parametro]:.4f}")

		otro = entrada("¿Ajustar otro conjunto de puntos? (s/n): ").strip().lower()
		if otro != "s":
			break


if __name__ == "__main__":
	resolver_desde_terminal()
