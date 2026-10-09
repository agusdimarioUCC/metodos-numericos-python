"""Polinomio de interpolación de Lagrange.

Dados n+1 puntos (xᵢ, yᵢ) con xᵢ distintos, arma

	Pₙ(x) = Σ Lᵢ(x)·yᵢ,    Lᵢ(x) = Π (x − xⱼ) / (xᵢ − xⱼ)    (j ≠ i)

donde cada Lᵢ vale 1 en xᵢ y 0 en los demás nodos, así que Pₙ pasa por todos los puntos.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

from metodos_numericos import (
	Iteracion,
	ReportarIteracion,
)

__all__ = ["interpolacion_lagrange"]


def interpolacion_lagrange(
		valores_x: Sequence[float],
		valores_y: Sequence[float],
		valor_a_interpolar: float,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[float, Callable[[float], float]]:
	"""Evalúa el polinomio de Lagrange en `valor_a_interpolar`.

	Args:
		valores_x: Las abscisas xᵢ, todas distintas (en cualquier orden).
		valores_y: Las ordenadas yᵢ = f(xᵢ), en la misma correspondencia.
		valor_a_interpolar: El x donde se evalúa Pₙ.
		reportar_iteracion: Si se pasa, se llama una vez por punto con
			`Iteracion(i, (xᵢ, yᵢ), None, detalle)`, donde `detalle` trae
			`valor_x`, `valor_y`, `base` = Lᵢ(x) y `termino` = Lᵢ(x)·yᵢ.

	Returns:
		Tupla (valor, polinomio): `valor` es Pₙ(valor_a_interpolar) y
		`polinomio` evalúa Pₙ en cualquier otro x.

	Raises:
		ValueError: Si `valores_x`/`valores_y` no tienen la misma longitud,
			si hay menos de 2 puntos, o si algún xᵢ se repite (el
			denominador de Lᵢ da cero).
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

	def base(indice: int, valor_x: float) -> float:
		resultado = 1.0
		for otro, extremo in enumerate(valores_x):
			if otro != indice:
				resultado *= (valor_x - extremo) / (valores_x[indice] - extremo)
		return resultado

	def polinomio(valor_x: float) -> float:
		return sum(base(indice, valor_x) * valores_y[indice] for indice in range(cantidad))

	valor = 0.0
	for indice, (valor_xi, valor_yi) in enumerate(zip(valores_x, valores_y)):
		valor_base = base(indice, valor_a_interpolar)
		termino = valor_base * valor_yi
		valor += termino
		if reportar_iteracion is not None:
			detalle = {"valor_x": valor_xi, "valor_y": valor_yi, "base": valor_base, "termino": termino}
			reportar_iteracion(Iteracion(indice, (valor_xi, valor_yi), None, detalle))

	return valor, polinomio
