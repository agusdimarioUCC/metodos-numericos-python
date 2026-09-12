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

	Valida sin evaluar: compila la expresión (rechaza errores de sintaxis)
	y revisa que cada nombre que usa sea `x` o algo de `math` (rechaza
	nombres desconocidos y trucos de atributos como `x.__class__`, cuyo
	nombre de atributo también aparece en `co_names`). No se evalúa en
	ningún punto a propósito: `log(x)` o `1/x` son expresiones válidas
	aunque no estén definidas en x = 0. Junta en un solo lugar el patrón
	"validar + envolver" que cada `gui.py` de método necesitaba repetir.

	Raises:
		SyntaxError: Si la expresión no es sintácticamente válida.
		NameError: Si usa un nombre que no es `x` ni está en `math`.
	"""
	if not expresion.strip():
		raise SyntaxError("la expresión está vacía")
	codigo = compile(expresion, "<expresión>", "eval")
	for nombre in codigo.co_names:
		if nombre != "x" and nombre not in _FUNCIONES_PERMITIDAS:
			raise NameError(f"no se reconoce «{nombre}»", name=nombre)

	def funcion(valor_x: float) -> float:
		return float(eval(codigo, {"__builtins__": {}}, {**_FUNCIONES_PERMITIDAS, "x": valor_x}))

	return funcion
