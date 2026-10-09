"""Matrices del resultado dibujadas entre corchetes, como en los apuntes (L, U, y, x, A⁻¹)."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from tkinter import ttk
from typing import NamedTuple

from metodos_numericos.descriptor import MatrizDeResultado
from metodos_numericos.formato import formatear_numero
from metodos_numericos.gui import tema as colores
from metodos_numericos.gui.tema import Tema, mostrar_barra_solo_si_hace_falta


class _GeometriaDeMatriz(NamedTuple):
	"""Los textos y medidas de una matriz, calculados una sola vez por redibujo.

	`_dibujar` los usa para ubicar la matriz y `_dibujar_matriz` para
	dibujarla, así lo que se mide y lo que se dibuja no pueden dejar de
	coincidir. `ancho` y `alto` incluyen el nombre (`L =`) y los corchetes.
	"""

	textos: list[list[str]]
	anchos_de_columna: list[int]
	alto_de_fila: int
	ancho_del_nombre: int
	ancho: int
	alto: int


class VistaDeMatrices(ttk.Frame):
	"""Muestra una o más matrices una al lado de la otra, pasando de renglón si no entran.

	Se usa en lugar del gráfico y la tabla para los métodos directos
	(descomposición LU), donde el paso a paso que importa son las
	matrices intermedias. La matriz marcada `es_resultado` va sobre fondo
	ámbar, como la respuesta en el resto de la app.
	"""

	def __init__(self, contenedor: tk.Widget, tema: Tema, mensaje_vacio: str) -> None:
		super().__init__(contenedor, style="Superficie.TFrame")
		self._tema = tema
		self._mensaje_vacio = mensaje_vacio
		self._matrices: tuple[MatrizDeResultado, ...] = ()
		self._decimales = 4

		self._lienzo = tk.Canvas(self, background=colores.SUPERFICIE, highlightthickness=0, borderwidth=0)
		barra_vertical = ttk.Scrollbar(self, orient="vertical", command=self._lienzo.yview)
		self._lienzo.configure(yscrollcommand=mostrar_barra_solo_si_hace_falta(barra_vertical))
		self._lienzo.grid(row=0, column=0, sticky="nsew")
		barra_vertical.grid(row=0, column=1, sticky="ns")
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self._lienzo.bind("<Configure>", lambda evento: self._dibujar())
		self._lienzo.bind("<MouseWheel>", lambda evento: self._lienzo.yview_scroll(-round(evento.delta / 120), "units"))

	def mostrar(self, matrices: Sequence[MatrizDeResultado]) -> None:
		"""Reemplaza las matrices mostradas y redibuja; con una secuencia vacía muestra el mensaje vacío."""
		self._matrices = tuple(matrices)
		self._dibujar()

	def establecer_decimales(self, decimales: int) -> None:
		"""Cambia la cantidad de decimales de los números y redibuja sin recalcular."""
		self._decimales = decimales
		self._dibujar()

	def _dibujar(self) -> None:
		lienzo = self._lienzo
		lienzo.delete("all")
		px = self._tema.px
		margen = px(24)
		ancho_disponible = max(lienzo.winfo_width(), px(200))

		if not self._matrices:
			lienzo.create_text(
				ancho_disponible / 2, px(48), text=self._mensaje_vacio,
				fill=colores.TINTA_SUAVE, font=self._tema.interfaz,
			)
			lienzo.configure(scrollregion=(0, 0, ancho_disponible, px(100)))
			return

		izquierda_actual, arriba_actual = margen, margen
		alto_del_renglon = 0
		for matriz in self._matrices:
			geometria = self._medir(matriz)
			if izquierda_actual > margen and izquierda_actual + geometria.ancho > ancho_disponible - margen:
				izquierda_actual = margen
				arriba_actual += alto_del_renglon + px(28)
				alto_del_renglon = 0
			self._dibujar_matriz(matriz, geometria, izquierda_actual, arriba_actual)
			izquierda_actual += geometria.ancho + px(40)
			alto_del_renglon = max(alto_del_renglon, geometria.alto)
		lienzo.configure(scrollregion=(0, 0, ancho_disponible, arriba_actual + alto_del_renglon + margen))

	def _textos(self, matriz: MatrizDeResultado) -> list[list[str]]:
		return [[formatear_numero(valor, self._decimales) for valor in fila] for fila in matriz.filas]

	def _anchos_de_columna(self, textos: list[list[str]]) -> list[int]:
		medir = self._tema.numeros.measure
		cantidad_de_columnas = max(len(fila) for fila in textos)
		return [
			max(medir(fila[columna]) for fila in textos if columna < len(fila)) + self._tema.px(16)
			for columna in range(cantidad_de_columnas)
		]

	def _medir(self, matriz: MatrizDeResultado) -> _GeometriaDeMatriz:
		px = self._tema.px
		textos = self._textos(matriz)
		anchos_de_columna = self._anchos_de_columna(textos)
		alto_de_fila = self._tema.numeros.metrics("linespace") + px(6)
		ancho_del_nombre = self._tema.formula.measure(f"{matriz.nombre} =") + px(10)
		return _GeometriaDeMatriz(
			textos=textos,
			anchos_de_columna=anchos_de_columna,
			alto_de_fila=alto_de_fila,
			ancho_del_nombre=ancho_del_nombre,
			ancho=ancho_del_nombre + sum(anchos_de_columna) + px(16),
			alto=len(textos) * alto_de_fila + px(8),
		)

	def _dibujar_matriz(
			self,
			matriz: MatrizDeResultado,
			geometria: _GeometriaDeMatriz,
			izquierda_del_nombre: int,
			arriba: int,
	) -> None:
		lienzo = self._lienzo
		px = self._tema.px
		alto = geometria.alto

		lienzo.create_text(
			izquierda_del_nombre, arriba + alto / 2, text=f"{matriz.nombre} =", anchor="w",
			font=self._tema.formula, fill=colores.TINTA,
		)
		izquierda = izquierda_del_nombre + geometria.ancho_del_nombre
		derecha = izquierda_del_nombre + geometria.ancho

		if matriz.es_resultado:
			lienzo.create_rectangle(
				izquierda + px(4), arriba + px(2), derecha - px(4), arriba + alto - px(2),
				fill=colores.AMBAR, width=0,
			)

		serif = px(6)
		grosor = max(1, px(1.5))
		for borde, sentido in ((izquierda, 1), (derecha, -1)):
			lienzo.create_line(
				borde + sentido * serif, arriba, borde, arriba, borde, arriba + alto, borde + sentido * serif, arriba + alto,
				fill=colores.TINTA, width=grosor,
			)

		for numero_de_fila, fila in enumerate(geometria.textos):
			centro_vertical = arriba + px(4) + (numero_de_fila + 0.5) * geometria.alto_de_fila
			borde_derecho = izquierda + px(8)
			for numero_de_columna, texto in enumerate(fila):
				borde_derecho += geometria.anchos_de_columna[numero_de_columna]
				lienzo.create_text(
					borde_derecho - px(8), centro_vertical, text=texto, anchor="e",
					font=self._tema.numeros, fill=colores.TINTA,
				)
