"""Lectura de valores desde la terminal, compartida entre métodos iterativos."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

from metodos_numericos_base.expresiones import compilar_funcion


def leer_funcion_desde_terminal(
		*, etiqueta: str = "f(x)", entrada: Callable[[str], str] = input
) -> tuple[Callable[[float], float], str]:
	"""Lee una expresión matemática desde terminal y devuelve la función y su texto.

	Valida la expresión con `compilar_funcion` (sin evaluarla, así que
	`log(x)` se acepta aunque no esté definida en 0); si tiene un error
	de sintaxis o usa un nombre no permitido, vuelve a pedirla.

	Args:
		etiqueta: Texto mostrado antes del "=" al pedir la expresión (por
			defecto "f(x)"; un método puede pasar "g(x)", "f'(x)", etc.
			según qué expresión necesite).
		entrada: Función usada para leer la línea (por defecto `input`);
			se puede inyectar otra función en los tests.

	Returns:
		Tupla (funcion, expresion) con la función evaluable y el texto
		original que escribió el usuario.
	"""
	while True:
		expresion = entrada(f"{etiqueta} = ").strip()
		try:
			funcion = compilar_funcion(expresion)
		except (SyntaxError, NameError) as error:
			print(f"Expresión inválida ({error}). Probá de nuevo.")
			continue
		return funcion, expresion


def leer_valor_inicial_desde_terminal(
		*, etiqueta: str = "Valor inicial", entrada: Callable[[str], str] = input
) -> float:
	"""Lee un único valor numérico desde terminal (ej. la aproximación inicial x0).

	Vuelve a pedirlo si lo que se escribió no se puede convertir a float.

	Args:
		etiqueta: Texto mostrado antes del ":" al pedir el valor.
		entrada: Función usada para leer la línea (por defecto `input`);
			se puede inyectar otra función en los tests.
	"""
	while True:
		texto = entrada(f"{etiqueta}: ").strip()
		try:
			return float(texto)
		except ValueError:
			print(f"'{texto}' no es un número válido. Probá de nuevo.")


def leer_opcion_desde_terminal(
		etiqueta: str, opciones: Sequence[str], *, entrada: Callable[[str], str] = input
) -> str:
	"""Pide elegir una entre varias opciones nombradas, reintentando si no coincide con ninguna.

	La comparación no distingue mayúsculas/minúsculas, pero devuelve la
	opción tal como está escrita en `opciones`.

	Args:
		etiqueta: Texto mostrado antes de la lista de opciones.
		opciones: Las opciones válidas, en el orden en que se muestran.
		entrada: Función usada para leer la línea (por defecto `input`);
			se puede inyectar otra función en los tests.
	"""
	texto_de_opciones = " / ".join(opciones)
	while True:
		respuesta = entrada(f"{etiqueta} ({texto_de_opciones}): ").strip()
		for opcion in opciones:
			if respuesta.lower() == opcion.lower():
				return opcion
		print(f"'{respuesta}' no es una opción válida. Elegí una de: {texto_de_opciones}.")


def leer_puntos_desde_terminal(
		*, entrada: Callable[[str], str] = input
) -> tuple[tuple[float, ...], tuple[float, ...]]:
	"""Lee una cantidad y luego esa cantidad de pares (x, y) desde terminal.

	Vuelve a pedir la cantidad si no es un entero mayor o igual a 2, y
	vuelve a pedir un punto si su línea no tiene exactamente 2 números.

	Args:
		entrada: Función usada para leer cada línea (por defecto `input`);
			se puede inyectar otra función en los tests.
	"""
	while True:
		texto_cantidad = entrada("Cantidad de puntos: ").strip()
		if texto_cantidad.isdigit() and int(texto_cantidad) >= 2:
			cantidad = int(texto_cantidad)
			break
		print("Tiene que ser un número entero mayor o igual a 2. Probá de nuevo.")

	valores_x: list[float] = []
	valores_y: list[float] = []
	for numero_de_punto in range(1, cantidad + 1):
		while True:
			texto_punto = entrada(f"Punto {numero_de_punto} (x y): ").strip()
			valores_texto = texto_punto.split()
			if len(valores_texto) == 2:
				try:
					valor_x, valor_y = (float(valor) for valor in valores_texto)
				except ValueError:
					print("Los dos valores tienen que ser números. Probá de nuevo.")
					continue
				valores_x.append(valor_x)
				valores_y.append(valor_y)
				break
			print("Escribí exactamente 2 valores separados por un espacio (x y). Probá de nuevo.")

	return tuple(valores_x), tuple(valores_y)
