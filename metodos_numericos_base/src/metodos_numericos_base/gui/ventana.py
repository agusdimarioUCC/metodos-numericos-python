"""La ventana de la aplicación: barra lateral con los métodos y un panel por método."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from tkinter import ttk

from metodos_numericos_base.descriptor import DescriptorDeMetodo
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.barra_lateral import BarraLateral
from metodos_numericos_base.gui.campos import GrillaDeSistema
from metodos_numericos_base.gui.panel import PanelDeMetodo
from metodos_numericos_base.gui.tema import activar_nitidez_en_pantallas_escaladas, crear_tema


class VentanaMetodosNumericos(tk.Tk):
	"""La única ventana de la aplicación: barra lateral + un `PanelDeMetodo` por método.

	No conoce ningún método concreto — recibe una secuencia de
	`DescriptorDeMetodo` y arma un panel por cada uno, todos apilados en
	la misma celda; elegir un método en la barra lateral solo trae su
	panel al frente (`tkraise`), sin reconstruir nada. El orden de la
	secuencia es el orden de la barra lateral. Ctrl+Tab y Ctrl+Shift+Tab
	pasan al método siguiente o anterior.
	"""

	def __init__(self, descriptores: Sequence[DescriptorDeMetodo]) -> None:
		activar_nitidez_en_pantallas_escaladas()
		super().__init__()
		self.title("Métodos numéricos")
		self.tema = crear_tema(self)
		px = self.tema.px

		ancho_de_pantalla, alto_de_pantalla = self.winfo_screenwidth(), self.winfo_screenheight()
		ancho = max(min(px(1100), ancho_de_pantalla), round(ancho_de_pantalla * 0.85))
		alto = max(min(px(700), alto_de_pantalla), round(alto_de_pantalla * 0.85))
		self.geometry(f"{ancho}x{alto}+{(ancho_de_pantalla - ancho) // 2}+{max(0, (alto_de_pantalla - alto) // 3)}")
		self.minsize(min(px(1000), ancho_de_pantalla), min(px(640), alto_de_pantalla))

		self._descriptores = tuple(descriptores)
		self._indice_actual: int | None = None
		self.barra_lateral = BarraLateral(self, self.tema, self._descriptores, self.mostrar_metodo)
		self.barra_lateral.grid(row=0, column=0, sticky="ns")
		self.barra_lateral.configure(width=px(220))
		self.barra_lateral.grid_propagate(False)
		self.barra_lateral.pack_propagate(False)
		tk.Frame(self, width=1, background=colores.LINEA).grid(row=0, column=1, sticky="ns")

		contenedor = ttk.Frame(self)
		contenedor.grid(row=0, column=2, sticky="nsew")
		contenedor.rowconfigure(0, weight=1)
		contenedor.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)

		self.paneles: list[PanelDeMetodo] = []
		for descriptor in self._descriptores:
			panel = PanelDeMetodo(contenedor, descriptor, self.tema)
			panel.grid(row=0, column=0, sticky="nsew")
			self.paneles.append(panel)

		vincular_grillas_de_sistema(self.paneles)
		self.bind_all("<Control-Tab>", lambda evento: self._pasar_de_metodo(1))
		self.bind_all("<Control-Shift-Tab>", lambda evento: self._pasar_de_metodo(-1))
		if self.paneles:
			self.mostrar_metodo(0)

	def mostrar_metodo(self, indice: int) -> None:
		"""Trae al frente el panel del método `indice` (y lo marca en la barra lateral).

		Antes de cambiar, sincroniza las grillas de sistema del panel que
		se deja: hacer clic en otro método no dispara `<FocusOut>` en la
		celda que se estaba editando (solo cambia qué panel se ve), así
		que un valor recién tipeado no se habría propagado todavía.
		"""
		anterior = self._indice_actual
		if anterior is not None and anterior != indice:
			for grilla in self.paneles[anterior].grillas_de_sistema():
				if grilla.al_cambiar is not None:
					grilla.al_cambiar()
		self._indice_actual = indice
		self.barra_lateral.seleccionar(indice)
		self.paneles[indice].tkraise()

	def _pasar_de_metodo(self, delta: int) -> str:
		if self.paneles:
			self.mostrar_metodo(((self._indice_actual or 0) + delta) % len(self.paneles))
		return "break"

	def ejecutar(self) -> None:
		"""Inicia el bucle principal de la GUI. Bloquea hasta que se cierra la ventana."""
		self.mainloop()


def vincular_grillas_de_sistema(paneles: Sequence[PanelDeMetodo]) -> None:
	"""Enlaza entre sí las grillas de sistema Ax = b de todos los paneles.

	Cuando el usuario termina de editar una celda en una grilla, el
	sistema completo (tamaño, coeficientes y términos independientes) se
	copia a las demás grillas enlazadas, para poder escribirlo una sola
	vez y comparar el mismo sistema entre métodos (por ejemplo,
	Gauss-Seidel y Descomposición LU) sin volver a tipearlo. Si hay menos
	de dos grillas de sistema en total, no hay nada que enlazar.
	"""
	grillas = [grilla for panel in paneles for grilla in panel.grillas_de_sistema()]
	if len(grillas) < 2:
		return

	for grilla in grillas:
		otras = [otra for otra in grillas if otra is not grilla]
		grilla.al_cambiar = lambda grilla=grilla, otras=otras: _propagar_sistema(grilla, otras)


def _propagar_sistema(origen: GrillaDeSistema, destinos: Sequence[GrillaDeSistema]) -> None:
	try:
		filas, terminos_independientes = origen.obtener_sistema()
	except ValueError:
		return  # Entrada incompleta o inválida (p.ej. a mitad de tipear); no se propaga todavía.
	for destino in destinos:
		destino.establecer_sistema(filas, terminos_independientes)
