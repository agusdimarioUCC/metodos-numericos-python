"""Polinomio de interpolación de Newton en diferencias divididas.

Dados n+1 puntos (xᵢ, yᵢ) con xᵢ distintos, arma la tabla de diferencias
divididas

	f[xᵢ] = yᵢ
	f[xᵢ₊ₖ;…;xᵢ] = (f[xᵢ₊ₖ;…;xᵢ₊₁] − f[xᵢ₊ₖ₋₁;…;xᵢ]) / (xᵢ₊ₖ − xᵢ)

y toma su primera fila como coeficientes bₖ = f[xₖ;…;x₀] de

	Pₙ(x) = b₀ + b₁(x − x₀) + b₂(x − x₀)(x − x₁) + … + bₙ(x − x₀)…(x − xₙ₋₁)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

from metodos_numericos import (
	Iteracion,
	ReportarIteracion,
)

__all__ = ["desarrollar_polinomio", "interpolacion_newton"]


def interpolacion_newton(
		valores_x: Sequence[float],
		valores_y: Sequence[float],
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[tuple[float, ...], Callable[[float], float]]:
	"""Calcula los coeficientes del polinomio de Newton por diferencias divididas.

	Args:
		valores_x: Las abscisas xᵢ, todas distintas (en cualquier orden).
		valores_y: Las ordenadas yᵢ = f(xᵢ), en la misma correspondencia.
		reportar_iteracion: Si se pasa, se llama una vez por punto con
			`Iteracion(i, (xᵢ, yᵢ), None, detalle)`, donde `detalle` trae
			`valor_x`, `valor_y` y `orden_k` = f[xᵢ₊ₖ;…;xᵢ] para cada k que
			exista en esa fila (la fila i tiene n − i diferencias), como la
			tabla escalonada de los apuntes.

	Returns:
		Tupla (coeficientes, polinomio): `coeficientes` son b₀…bₙ y
		`polinomio` evalúa Pₙ(x) en forma anidada.

	Raises:
		ValueError: Si `valores_x`/`valores_y` no tienen la misma longitud,
			si hay menos de 2 puntos, o si algún xᵢ se repite (el
			denominador de la diferencia dividida da cero).
	"""
	if len(valores_x) != len(valores_y):
		raise ValueError(
			f"x e y tienen que tener la misma cantidad de valores (x tiene {len(valores_x)}, "
			f"y tiene {len(valores_y)})."
		)
	cantidad = len(valores_x)
	if cantidad < 2:
		raise ValueError(f"Hacen falta al menos 2 puntos para interpolar (se recibieron {cantidad}).")
	if len(set(valores_x)) != cantidad:
		raise ValueError("Los Xᵢ tienen que ser todos distintos (dos puntos con la misma x no definen una función).")

	# tabla[k][i] = f[xᵢ₊ₖ;…;xᵢ]; la columna k tiene n+1−k valores
	tabla: list[list[float]] = [list(valores_y)]
	for orden in range(1, cantidad):
		anterior = tabla[-1]
		tabla.append([
			(anterior[indice + 1] - anterior[indice]) / (valores_x[indice + orden] - valores_x[indice])
			for indice in range(cantidad - orden)
		])

	if reportar_iteracion is not None:
		for indice, (valor_x, valor_y) in enumerate(zip(valores_x, valores_y)):
			detalle = {"valor_x": valor_x, "valor_y": valor_y}
			for orden in range(1, cantidad - indice):
				detalle[f"orden_{orden}"] = tabla[orden][indice]
			reportar_iteracion(Iteracion(indice, (valor_x, valor_y), None, detalle))

	coeficientes = tuple(columna[0] for columna in tabla)

	def polinomio(valor_x: float) -> float:
		resultado = coeficientes[-1]
		for orden in range(cantidad - 2, -1, -1):
			resultado = resultado * (valor_x - valores_x[orden]) + coeficientes[orden]
		return resultado

	return coeficientes, polinomio


def desarrollar_polinomio(coeficientes: Sequence[float], valores_x: Sequence[float]) -> tuple[float, ...]:
	"""Pasa Pₙ de la forma de Newton (b₀…bₙ sobre los nodos x₀…xₙ₋₁) a potencias de x.

	Es la evaluación anidada de `interpolacion_newton`, pero con polinomios
	en vez de números: se arranca con bₙ y, de k = n−1 a 0, se multiplica
	por (x − xₖ) y se suma bₖ.

	Returns:
		Los coeficientes a₀…aₙ de a₀ + a₁x + … + aₙxⁿ, en orden ascendente.
	"""
	desarrollado = [coeficientes[-1]]
	for orden in range(len(coeficientes) - 2, -1, -1):
		# (a₀ + a₁x + …)·(x − xₖ): cada coeficiente sube un grado y se le resta xₖ veces el suyo.
		desarrollado = [0.0, *desarrollado]
		for grado in range(len(desarrollado) - 1):
			desarrollado[grado] -= valores_x[orden] * desarrollado[grado + 1]
		desarrollado[0] += coeficientes[orden]
	return tuple(desarrollado)
