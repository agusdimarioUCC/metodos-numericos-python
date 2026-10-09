"""Errores compartidos por los métodos numéricos iterativos."""

from __future__ import annotations

from metodos_numericos.formato import formatear_valor_corto


class NoConvergeError(RuntimeError):
	"""Se lanza cuando un método no converge dentro del número máximo de iteraciones."""

	@classmethod
	def despues_de(cls, maximo_iteraciones: int, ultimo_error: float | None) -> NoConvergeError:
		"""Arma el error con el mensaje estándar: cuántas iteraciones se probaron y el último |E|."""
		detalle = "" if ultimo_error is None else f" (último |E| = {formatear_valor_corto(float(ultimo_error))})"
		return cls(f"No convergió en {maximo_iteraciones} iteraciones{detalle}.")


class EntradaInvalidaError(ValueError):
	"""Se lanza cuando el texto que el usuario escribió en un campo de la GUI no se pudo interpretar.

	Hereda de ValueError porque es un error en un valor de entrada;
	`PanelDeMetodo._calcular` lo atrapa por separado de los errores del
	método, para marcar en rojo el campo `nombre_del_campo` (el
	`CampoDeEntrada.nombre` del campo que falló).
	"""

	def __init__(self, mensaje: str, nombre_del_campo: str | None = None) -> None:
		super().__init__(mensaje)
		self.nombre_del_campo = nombre_del_campo
