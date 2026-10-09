"""Trazadoras cúbicas (natural y condicionada), con el algoritmo del apunte (Burden y Faires).

Entre cada par de puntos consecutivos pasa un polinomio de tercer grado

	Sᵢ(x) = aᵢ + bᵢ(x − xᵢ) + cᵢ(x − xᵢ)² + dᵢ(x − xᵢ)³,    aᵢ = yᵢ

con Sᵢ, Sᵢ′ y Sᵢ″ continuas en los empalmes. Los bordes se cierran de una de dos formas:
natural (S″ = 0 en x₀ y xₙ) o condicionada (S′ dada en x₀ y xₙ).
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Sequence
from typing import Callable

from metodos_numericos import (
	Iteracion,
	ReportarIteracion,
)

__all__ = ["MODELOS_DISPONIBLES", "trazadora_cubica"]

MODELOS_DISPONIBLES = ("Natural", "Condicionada")


def trazadora_cubica(
		valores_x: Sequence[float],
		valores_y: Sequence[float],
		tipo: str = "Natural",
		derivada_inicial: float = 0.0,
		derivada_final: float = 0.0,
		reportar_iteracion: ReportarIteracion | None = None,
) -> tuple[tuple[tuple[float, float, float, float], ...], Callable[[float], float]]:
	"""Calcula los coeficientes de la trazadora cúbica que pasa por todos los puntos.

	Args:
		valores_x: Las abscisas xᵢ, todas distintas (en cualquier orden: se ordenan).
		valores_y: Las ordenadas yᵢ = f(xᵢ), en la misma correspondencia.
		tipo: "Natural" o "Condicionada".
		derivada_inicial: S′(x₀), solo se usa en la condicionada.
		derivada_final: S′(xₙ), solo se usa en la condicionada.
		reportar_iteracion: Si se pasa, se llama una vez por punto (filas 0..n,
			ya ordenados) con `Iteracion(i, (xᵢ, yᵢ), None, detalle)`, donde
			`detalle` trae `valor_x`, `valor_a` y, de `h`, `alfa`, `l`, `mu`,
			`z`, `c`, `b`, `d`, las que existan en esa fila.

	Returns:
		Tupla (coeficientes, trazadora): `coeficientes[i]` es (aᵢ, bᵢ, cᵢ, dᵢ)
		del tramo [xᵢ, xᵢ₊₁] y `trazadora` evalúa S(x); fuera de [x₀, xₙ]
		extiende el primer o el último tramo.

	Raises:
		ValueError: Si `valores_x`/`valores_y` no tienen la misma longitud, si
			hay menos de 2 puntos, si algún xᵢ se repite o si `tipo` no es
			uno de `MODELOS_DISPONIBLES`.
	"""
	if tipo not in MODELOS_DISPONIBLES:
		raise ValueError(f"El tipo de trazadora tiene que ser uno de {MODELOS_DISPONIBLES} (se recibió {tipo!r}).")
	if len(valores_x) != len(valores_y):
		raise ValueError(
			f"x e y tienen que tener la misma cantidad de valores (x tiene {len(valores_x)}, "
			f"y tiene {len(valores_y)})."
		)
	cantidad = len(valores_x)
	if cantidad < 2:
		raise ValueError(f"Hacen falta al menos 2 puntos para trazar (se recibieron {cantidad}).")
	if len(set(valores_x)) != cantidad:
		raise ValueError("Los Xᵢ tienen que ser todos distintos (dos puntos con la misma x no definen una función).")

	abscisas, ordenadas = (list(columna) for columna in zip(*sorted(zip(valores_x, valores_y))))
	ultimo = cantidad - 1
	es_condicionada = tipo == "Condicionada"

	pasos = [abscisas[indice + 1] - abscisas[indice] for indice in range(ultimo)]
	alfa: dict[int, float] = {
		indice: 3 / pasos[indice] * (ordenadas[indice + 1] - ordenadas[indice])
		- 3 / pasos[indice - 1] * (ordenadas[indice] - ordenadas[indice - 1])
		for indice in range(1, ultimo)
	}
	if es_condicionada:
		alfa[0] = 3 / pasos[0] * (ordenadas[1] - ordenadas[0]) - 3 * derivada_inicial
		alfa[ultimo] = 3 * derivada_final - 3 * (ordenadas[ultimo] - ordenadas[ultimo - 1]) / pasos[ultimo - 1]

	# Barrido hacia adelante: resuelve el sistema tridiagonal de los cᵢ
	diagonal = [0.0] * cantidad
	multiplicador = [0.0] * ultimo
	auxiliar = [0.0] * cantidad
	if es_condicionada:
		diagonal[0] = 2 * pasos[0]
		multiplicador[0] = 0.5
		auxiliar[0] = alfa[0] / diagonal[0]
	else:
		diagonal[0] = 1.0
	for indice in range(1, ultimo):
		diagonal[indice] = 2 * (abscisas[indice + 1] - abscisas[indice - 1]) - pasos[indice - 1] * multiplicador[indice - 1]
		multiplicador[indice] = pasos[indice] / diagonal[indice]
		auxiliar[indice] = (alfa[indice] - pasos[indice - 1] * auxiliar[indice - 1]) / diagonal[indice]

	coeficientes_c = [0.0] * cantidad
	if es_condicionada:
		diagonal[ultimo] = pasos[ultimo - 1] * (2 - multiplicador[ultimo - 1])
		auxiliar[ultimo] = (alfa[ultimo] - pasos[ultimo - 1] * auxiliar[ultimo - 1]) / diagonal[ultimo]
		coeficientes_c[ultimo] = auxiliar[ultimo]
	else:
		diagonal[ultimo] = 1.0

	# Sustitución hacia atrás
	coeficientes_b = [0.0] * ultimo
	coeficientes_d = [0.0] * ultimo
	for indice in range(ultimo - 1, -1, -1):
		coeficientes_c[indice] = auxiliar[indice] - multiplicador[indice] * coeficientes_c[indice + 1]
		coeficientes_b[indice] = (
			(ordenadas[indice + 1] - ordenadas[indice]) / pasos[indice]
			- pasos[indice] * (coeficientes_c[indice + 1] + 2 * coeficientes_c[indice]) / 3
		)
		coeficientes_d[indice] = (coeficientes_c[indice + 1] - coeficientes_c[indice]) / (3 * pasos[indice])

	if reportar_iteracion is not None:
		for indice in range(cantidad):
			detalle: dict[str, float] = {
				"valor_x": abscisas[indice],
				"valor_a": ordenadas[indice],
				"l": diagonal[indice],
				"z": auxiliar[indice],
				"c": coeficientes_c[indice],
			}
			if indice in alfa:
				detalle["alfa"] = alfa[indice]
			if indice < ultimo:
				detalle.update(
					h=pasos[indice],
					mu=multiplicador[indice],
					b=coeficientes_b[indice],
					d=coeficientes_d[indice],
				)
			reportar_iteracion(Iteracion(indice, (abscisas[indice], ordenadas[indice]), None, detalle))

	coeficientes = tuple(
		(ordenadas[indice], coeficientes_b[indice], coeficientes_c[indice], coeficientes_d[indice])
		for indice in range(ultimo)
	)

	def trazadora(valor_x: float) -> float:
		tramo = min(max(bisect_right(abscisas, valor_x) - 1, 0), ultimo - 1)
		constante, lineal, cuadratico, cubico = coeficientes[tramo]
		desplazamiento = valor_x - abscisas[tramo]
		return constante + desplazamiento * (lineal + desplazamiento * (cuadratico + desplazamiento * cubico))

	return coeficientes, trazadora
