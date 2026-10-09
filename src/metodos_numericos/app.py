"""Punto de entrada de la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos import VentanaMetodosNumericos
from metodos_numericos.registro import METODOS_DISPONIBLES

__all__ = ["iniciar_gui"]


def iniciar_gui() -> None:
	"""Abre la ventana unificada y bloquea hasta que se cierra.

	La ventana tiene una barra lateral con los métodos agrupados por
	capítulo y un panel por método.
	"""
	ventana = VentanaMetodosNumericos(METODOS_DISPONIBLES)
	ventana.ejecutar()
