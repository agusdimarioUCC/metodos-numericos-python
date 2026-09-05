"""Lectura de un sistema de ecuaciones lineales Ax = b escrito como texto.

No es específico de ningún método: cualquiera que resuelva un sistema
(hoy solo Gauss-Seidel) puede reusarlo, tanto para interpretar texto
tipeado a mano como para poblar una grilla de entradas con un ejemplo.
"""

from __future__ import annotations


def leer_sistema_desde_texto(texto: str) -> tuple[list[list[float]], list[float]]:
	"""Interpreta un sistema Ax = b escrito como texto, una ecuación por línea.

	Cada línea tiene los coeficientes y el término independiente separados
	por espacios, con un "|" (o "=") opcional antes del último valor, por
	ejemplo `"12 -1 3 | 8"`. El número de ecuaciones define `n`, y cada
	línea debe tener exactamente `n` coeficientes más el término
	independiente.

	Raises:
		ValueError: Si el texto está vacío o si alguna línea no tiene la
			cantidad de valores esperada, señalando qué fila falló.
	"""
	lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
	if not lineas:
		raise ValueError("El sistema no puede estar vacío")

	cantidad_de_ecuaciones = len(lineas)
	filas: list[list[float]] = []
	terminos_independientes: list[float] = []
	for numero_de_fila, linea in enumerate(lineas, start=1):
		valores_texto = linea.replace("|", " ").replace("=", " ").split()
		if len(valores_texto) != cantidad_de_ecuaciones + 1:
			raise ValueError(
				f"Fila {numero_de_fila}: se esperaban {cantidad_de_ecuaciones + 1} valores "
				f"(coeficientes + término independiente), se recibieron {len(valores_texto)}"
			)
		try:
			valores = [float(valor) for valor in valores_texto]
		except ValueError as error:
			raise ValueError(f"Fila {numero_de_fila}: {error}") from error
		filas.append(valores[:-1])
		terminos_independientes.append(valores[-1])

	return filas, terminos_independientes
