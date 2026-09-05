"""Punto de entrada de la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import VentanaMetodosNumericos

from metodos_numericos_gui.registro import METODOS_DISPONIBLES

__all__ = ["iniciar_gui"]


def iniciar_gui() -> None:
	"""Abre la ventana unificada (una pestaña por método) y bloquea hasta que se cierra."""
	ventana = VentanaMetodosNumericos(METODOS_DISPONIBLES)
	ventana.ejecutar()
