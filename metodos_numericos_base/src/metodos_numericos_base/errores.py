"""Errores compartidos por los métodos numéricos iterativos."""

from __future__ import annotations


class NoConvergeError(RuntimeError):
	"""Se lanza cuando un método no converge dentro del número máximo de iteraciones."""


class EntradaInvalidaError(ValueError):
	"""Se lanza cuando el texto que el usuario escribió en un campo de la GUI no se pudo interpretar.

	Hereda de ValueError a propósito: el manejador de errores de
	`PanelDeMetodo` atrapa `ValueError` de todos modos (lo lanzan los
	propios métodos por precondiciones incumplidas), así que no hace
	falta un `except` aparte para los errores de conversión de entrada.
	"""
