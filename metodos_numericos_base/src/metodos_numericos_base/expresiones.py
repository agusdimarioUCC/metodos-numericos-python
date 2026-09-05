"""Evaluación de expresiones matemáticas f(x) escritas por el usuario."""

from __future__ import annotations

import math
from typing import Callable

_FUNCIONES_PERMITIDAS = {
	nombre: valor for nombre, valor in vars(math).items() if not nombre.startswith("_")
}


def evaluar_funcion(expresion: str, valor_x: float) -> float:
	"""Evalúa una expresión matemática en `valor_x`.

	La expresión puede usar `x` como variable y cualquier función o
	constante del módulo `math` (sin, cos, sqrt, exp, log, pi, etc.). No
	tiene acceso a builtins de Python, así que no puede importar módulos
	ni llamar funciones fuera de esa lista.
	"""
	entorno = {**_FUNCIONES_PERMITIDAS, "x": valor_x}
	return float(eval(expresion, {"__builtins__": {}}, entorno))


def compilar_funcion(expresion: str) -> Callable[[float], float]:
	"""Valida una expresión y devuelve una función evaluable a partir de ella.

	Valida evaluándola en x=0 (deja pasar `"x**2 - 2"`, rechaza una
	expresión con error de sintaxis o un nombre no permitido) y después
	devuelve un envoltorio que llama a `evaluar_funcion` con cada `x`
	que se le pida. Junta en un solo lugar el patrón "validar + envolver"
	que cada `gui.py` de método necesitaba repetir por su cuenta.

	Raises:
		Cualquier excepción que lance `evaluar_funcion` al evaluar en x=0
		(SyntaxError, NameError, etc., según qué esté mal en la expresión).
	"""
	evaluar_funcion(expresion, 0.0)

	def funcion(valor_x: float) -> float:
		return evaluar_funcion(expresion, valor_x)

	return funcion
