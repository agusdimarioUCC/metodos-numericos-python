"""Barra lateral con los métodos agrupados por capítulo de los apuntes."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence

from metodos_numericos_base.descriptor import DescriptorDeMetodo
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.tema import Tema


class BarraLateral(tk.Frame):
	"""Lista de métodos agrupados por `DescriptorDeMetodo.capitulo`, en el orden en que llegan.

	Reemplaza a las pestañas: con seis métodos (y más por venir) una
	lista vertical agrupada se lee mejor que una fila de pestañas, y los
	capítulos repiten la organización de los apuntes. Se usa con el
	mouse o con el teclado: Tab llega a la lista, ↑/↓ cambian de método,
	y `al_elegir` recibe el índice del método elegido.
	"""

	def __init__(
			self,
			contenedor: tk.Widget,
			tema: Tema,
			descriptores: Sequence[DescriptorDeMetodo],
			al_elegir: Callable[[int], None],
	) -> None:
		super().__init__(contenedor, background=colores.LATERAL)
		self._tema = tema
		self._al_elegir = al_elegir
		self._items: list[tuple[tk.Frame, tk.Frame, tk.Label]] = []
		self._elegido: int | None = None
		px = tema.px

		tk.Label(
			self, text="Métodos numéricos", font=tema.marca, background=colores.LATERAL,
			foreground=colores.TINTA, anchor="w",
		).pack(fill="x", padx=px(20), pady=(px(22), px(10)))

		capitulo_actual: str | None = None
		for indice, descriptor in enumerate(descriptores):
			if descriptor.capitulo != capitulo_actual:
				capitulo_actual = descriptor.capitulo
				tk.Label(
					self, text=capitulo_actual, font=tema.interfaz_chica, background=colores.LATERAL,
					foreground=colores.TINTA_SUAVE, anchor="w", justify="left", wraplength=px(190),
				).pack(fill="x", padx=px(20), pady=(px(16), px(4)))
			self._items.append(self._armar_item(indice, descriptor.nombre_para_mostrar))

	def _armar_item(self, indice: int, texto: str) -> tuple[tk.Frame, tk.Frame, tk.Label]:
		px = self._tema.px
		item = tk.Frame(
			self, background=colores.LATERAL, takefocus=True, cursor="hand2",
			highlightthickness=px(1), highlightbackground=colores.LATERAL, highlightcolor=colores.AZUL,
		)
		item.pack(fill="x", padx=(px(8), px(8)), pady=px(1))
		marca = tk.Frame(item, width=px(3), background=colores.LATERAL)
		marca.pack(side="left", fill="y")
		etiqueta = tk.Label(
			item, text=texto, font=self._tema.interfaz, background=colores.LATERAL,
			foreground=colores.TINTA, anchor="w", padx=px(12), pady=px(7),
		)
		etiqueta.pack(side="left", fill="x", expand=True)

		for widget in (item, marca, etiqueta):
			widget.bind("<Button-1>", lambda evento, indice=indice: self._elegir(indice, enfocar=True))
			widget.bind("<Enter>", lambda evento, indice=indice: self._pintar(indice, sobre=True))
			widget.bind("<Leave>", lambda evento, indice=indice: self._pintar(indice))
		item.bind("<Return>", lambda evento, indice=indice: self._elegir(indice))
		item.bind("<space>", lambda evento, indice=indice: self._elegir(indice))
		item.bind("<Up>", lambda evento, indice=indice: self._elegir(indice - 1, enfocar=True))
		item.bind("<Down>", lambda evento, indice=indice: self._elegir(indice + 1, enfocar=True))
		return item, marca, etiqueta

	def _elegir(self, indice: int, enfocar: bool = False) -> None:
		if not (0 <= indice < len(self._items)):
			return
		self.seleccionar(indice)
		if enfocar:
			self._items[indice][0].focus_set()
		self._al_elegir(indice)

	def seleccionar(self, indice: int) -> None:
		"""Marca `indice` como el método elegido (sin avisar a `al_elegir`)."""
		anterior = self._elegido
		self._elegido = indice
		if anterior is not None:
			self._pintar(anterior)
		self._pintar(indice)

	def _pintar(self, indice: int, sobre: bool = False) -> None:
		item, marca, etiqueta = self._items[indice]
		elegido = indice == self._elegido
		fondo = colores.SUPERFICIE if elegido else (colores.LATERAL_RESALTADO if sobre else colores.LATERAL)
		item.configure(background=fondo, highlightbackground=fondo)
		marca.configure(background=colores.AZUL if elegido else fondo)
		etiqueta.configure(
			background=fondo,
			font=self._tema.interfaz_destacada if elegido else self._tema.interfaz,
		)
