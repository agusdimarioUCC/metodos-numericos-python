"""Representación genérica del progreso de un método iterativo."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Iteracion:
	"""Una fila del progreso de un método iterativo.

	`aproximacion` es lo que el método considera su mejor estimación en
	esa fila: un float para los métodos de búsqueda de raíces (el punto
	medio en bisección, `x_i` en punto fijo o Newton-Raphson), o una
	tupla de floats para un método que itera sobre un vector (la
	solución parcial de Gauss-Seidel). Siempre una tupla, nunca un array
	vivo, para que no cambie por detrás una vez reportada.

	`error` es la estimación de error que use cada método (diferencia
	entre aproximaciones sucesivas, norma de esa diferencia, etc.), o
	`None` cuando todavía no hay una aproximación anterior contra la cual
	medirlo — la fila 0 de las tablas de la cátedra, que muestran "-".

	Los métodos directos (LU, regresión, interpolación) reusan la misma
	fila para su tabla: ahí `aproximacion` es el dato de la fila (el
	punto (xᵢ, yᵢ), los multiplicadores de un paso o una columna de A⁻¹)
	y `error` no mide convergencia: es `None`, 0.0 o un residuo.

	`detalle` lleva las columnas propias de cada método en las tablas de
	los apuntes (a, b, f(a), f(c) en bisección; g(x_i) en punto fijo;
	f(x_i), f'(x_i) en Newton-Raphson...), con claves que el método
	declara en las `ColumnaDeTabla` de su descriptor. Un valor `None` o
	una clave ausente se muestra como celda vacía.
	"""

	numero: int
	aproximacion: float | tuple[float, ...]
	error: float | None
	detalle: Mapping[str, float | None] = field(default_factory=dict)


ReportarIteracion = Callable[[Iteracion], None]
