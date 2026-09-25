"""Lectura de una tabla de puntos (x, y) escrita como texto.

No es específico de ningún método: cualquiera que ajuste o interpole a
partir de un conjunto de puntos (hoy solo regresión lineal) puede
reusarlo, tanto para interpretar texto tipeado a mano como para poblar
una grilla de entradas con un ejemplo.
"""

from __future__ import annotations


def leer_puntos_desde_texto(texto: str) -> tuple[tuple[float, ...], tuple[float, ...]]:
	"""Interpreta una tabla de puntos (xᵢ, yᵢ) escrita como texto, un punto por línea.

	Cada línea tiene x e y separados por espacios, por ejemplo `"2 4.5"`.

	Raises:
		ValueError: Si el texto está vacío o si alguna línea no tiene
			exactamente 2 valores, señalando qué fila falló.
	"""
	lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
	if not lineas:
		raise ValueError("La tabla de puntos no puede estar vacía")

	valores_x: list[float] = []
	valores_y: list[float] = []
	for numero_de_fila, linea in enumerate(lineas, start=1):
		valores_texto = linea.split()
		if len(valores_texto) != 2:
			raise ValueError(
				f"Fila {numero_de_fila}: se esperaban 2 valores (x e y), se recibieron {len(valores_texto)}"
			)
		try:
			valor_x, valor_y = (float(valor) for valor in valores_texto)
		except ValueError as error:
			raise ValueError(f"Fila {numero_de_fila}: {error}") from error
		valores_x.append(valor_x)
		valores_y.append(valor_y)

	return tuple(valores_x), tuple(valores_y)
