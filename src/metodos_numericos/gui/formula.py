"""Dibujo de fórmulas en LaTeX (mathtext de matplotlib) como imagen para widgets de Tk."""

from __future__ import annotations

import base64
import io
import tkinter as tk

from matplotlib import rc_context
from matplotlib.figure import Figure

from metodos_numericos.gui import tema as colores
from metodos_numericos.gui.tema import Tema

_TAMANO_DE_LETRA_EN_PUNTOS = 15


def crear_imagen_de_formula(latex: str, tema: Tema) -> tk.PhotoImage:
	"""Dibuja `latex` (sintaxis mathtext: `\\frac`, `\\sum`, `x_{i+1}`…) recortada al texto y con el color del papel.

	Se dibuja con la misma escala que el resto de la ventana (`tema.escala`),
	así que sale nítida y del tamaño de la letra de la interfaz en pantallas
	escaladas. Quien la use tiene que guardar la imagen devuelta: Tk no
	mantiene viva una `PhotoImage` que ningún objeto de Python referencia.
	"""
	figura = Figure()
	figura.text(0, 0, f"${latex}$", fontsize=_TAMANO_DE_LETRA_EN_PUNTOS, color=colores.TINTA_SUAVE)
	memoria = io.BytesIO()
	with rc_context({"mathtext.fontset": "cm"}):
		figura.savefig(
			memoria,
			format="png",
			dpi=96 * tema.escala,
			facecolor=colores.PAPEL,
			bbox_inches="tight",
			pad_inches=0.03,
		)
	return tk.PhotoImage(data=base64.b64encode(memoria.getvalue()))
