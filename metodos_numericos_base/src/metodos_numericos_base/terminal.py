"""Lectura de valores desde la terminal, compartida entre métodos iterativos."""

from __future__ import annotations

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
