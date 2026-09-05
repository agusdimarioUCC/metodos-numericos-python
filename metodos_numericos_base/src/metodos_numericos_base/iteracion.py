"""Representación genérica del progreso de un método iterativo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Iteracion:
	"""Una fila del progreso de un método iterativo.

	`aproximacion` es lo que el método considera su mejor estimación en
	esa iteración: un float para los métodos de búsqueda de raíces (el
	punto medio en bisección, `x_n` en punto fijo o Newton-Raphson), o
	una tupla de floats para un método que itera sobre un vector (la
	solución parcial de Gauss-Seidel). Siempre una tupla, nunca un array
	vivo, para que no cambie por detrás una vez reportada. `error` es la
	estimación de error que use cada método (ancho del intervalo,
	diferencia entre aproximaciones sucesivas, norma del residuo, etc.).
	"""

	numero: int
	aproximacion: float | tuple[float, ...]
	error: float


ReportarIteracion = Callable[[Iteracion], None]


def formatear_aproximacion(aproximacion: float | tuple[float, ...]) -> str:
	"""Da formato legible a una aproximación, sea un escalar o un vector.

	No importa numpy: si `aproximacion` no es directamente convertible a
	float (por ejemplo, es una tupla o un array), la trata como una
	secuencia de componentes y formatea cada una.
	"""
	try:
		return f"{float(aproximacion):.6f}"
	except (TypeError, ValueError):
		return ", ".join(f"{float(componente):.6f}" for componente in aproximacion)


def imprimir_iteracion(iteracion: Iteracion) -> None:
	"""Reporta una iteración imprimiéndola por consola.

	Pensado para pasarse como `reportar_iteracion` desde las funciones
	de terminal de cada método, para no repetir el mismo `print` en
	cada uno.
	"""
	print(
		f"Iteración {iteracion.numero}: aproximación = {formatear_aproximacion(iteracion.aproximacion)}, "
		f"error = {float(iteracion.error):.5f}"
	)
