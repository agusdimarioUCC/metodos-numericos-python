"""Toolkit de Tkinter para la GUI unificada de métodos numéricos ("apunte de cátedra").

Módulos:

- `tema` — colores, tipografías, estilos ttk y escalado por DPI.
- `ventana` — `VentanaMetodosNumericos`: barra lateral + un panel por método.
- `barra_lateral` — la lista de métodos agrupada por capítulo.
- `panel` — `PanelDeMetodo`: datos, criterio de parada, resultado, gráfico y tabla.
- `campos` — el teclado matemático y la grilla de un sistema Ax = b.
- `tabla` — la tabla de iteraciones con celdas resaltadas como en los apuntes.
- `grafico` — el gráfico de cada método (matplotlib embebido).
- `matrices` — matrices del resultado entre corchetes (descomposición LU).
"""

from __future__ import annotations

from metodos_numericos_base.gui.panel import PanelDeMetodo
from metodos_numericos_base.gui.ventana import VentanaMetodosNumericos

__all__ = ["PanelDeMetodo", "VentanaMetodosNumericos"]
