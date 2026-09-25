"""Tabla de iteraciones con el formato de las tablas de los apuntes."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import ttk

from metodos_numericos_base.descriptor import ColumnaDeTabla, FormatoDeColumna
from metodos_numericos_base.formato import SIGNO_MENOS, formatear_numero, formatear_numero_legible, formatear_signo
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.tema import Tema, mostrar_barra_solo_si_hace_falta
from metodos_numericos_base.iteracion import Iteracion

_ESTIRAMIENTO_MAXIMO = 1.6
"""Cuánto se pueden ensanchar las columnas para ocupar el ancho disponible, sin que la tabla se desparrame."""


class TablaDeIteraciones(ttk.Frame):
	"""Tabla dibujada en un `Canvas`, con celdas resaltadas como en los apuntes.

	No es un `ttk.Treeview` porque el `Treeview` solo colorea filas
	enteras, y los apuntes resaltan celdas sueltas: la de la raíz en
	ámbar (en la última fila, columna `es_raiz`) y, en cada columna de
	error, la primera celda por debajo de ε en verde.

	Guarda las `Iteracion` crudas, así que cambiar los decimales vuelve a
	formatear todo sin recalcular. Las filas se agregan de a una mientras
	el método corre (`agregar_fila`) y se dibujan de forma incremental;
	solo se redibuja todo si un valor nuevo no entra en el ancho de su
	columna. `al_seleccionar` se llama con el índice de la fila elegida
	con el mouse o el teclado (↑/↓, Inicio/Fin, RePág/AvPág).
	"""

	def __init__(self, contenedor: tk.Widget, tema: Tema, mensaje_vacio: str) -> None:
		super().__init__(contenedor, style="Superficie.TFrame")
		self._tema = tema
		self._mensaje_vacio = mensaje_vacio
		self.al_seleccionar: Callable[[int], None] | None = None

		self._columnas: list[ColumnaDeTabla] = []
		self._filas: list[Iteracion] = []
		self._decimales = 4
		self._tolerancia: float | None = None
		self._raiz_resaltada = False
		self._seleccion: int | None = None
		self._primera_fila_bajo_tolerancia: dict[int, int] = {}
		self._anchos_base: list[int] = []
		self._anchos: list[int] = []
		self._bordes: list[int] = [0]
		self._redibujo_pendiente: str | None = None

		self._alto_de_fila = tema.px(26)
		self._margen_de_celda = tema.px(10)

		self._encabezado = tk.Canvas(
			self,
			height=tema.px(32),
			background=colores.SUPERFICIE,
			highlightthickness=0,
			borderwidth=0,
			xscrollincrement=tema.px(20),
		)
		self._cuerpo = tk.Canvas(
			self,
			background=colores.SUPERFICIE,
			highlightthickness=tema.px(2),
			highlightbackground=colores.SUPERFICIE,
			highlightcolor=colores.AZUL,
			borderwidth=0,
			takefocus=True,
			yscrollincrement=self._alto_de_fila,
			xscrollincrement=tema.px(20),
		)
		barra_vertical = ttk.Scrollbar(self, orient="vertical", command=self._cuerpo.yview)
		barra_horizontal = ttk.Scrollbar(self, orient="horizontal", command=self._desplazar_horizontal)
		self._cuerpo.configure(
			yscrollcommand=mostrar_barra_solo_si_hace_falta(barra_vertical),
			xscrollcommand=mostrar_barra_solo_si_hace_falta(barra_horizontal),
		)

		self._encabezado.grid(row=0, column=0, sticky="ew", padx=(tema.px(2), tema.px(2)))
		self._cuerpo.grid(row=1, column=0, sticky="nsew")
		barra_vertical.grid(row=1, column=1, sticky="ns")
		barra_horizontal.grid(row=2, column=0, sticky="ew")
		self.rowconfigure(1, weight=1)
		self.columnconfigure(0, weight=1)

		self._cuerpo.bind("<Button-1>", self._al_hacer_clic)
		self._cuerpo.bind("<Up>", lambda evento: self._mover_seleccion(-1))
		self._cuerpo.bind("<Down>", lambda evento: self._mover_seleccion(1))
		self._cuerpo.bind("<Prior>", lambda evento: self._mover_seleccion(-10))
		self._cuerpo.bind("<Next>", lambda evento: self._mover_seleccion(10))
		self._cuerpo.bind("<Home>", lambda evento: self._elegir_fila(0))
		self._cuerpo.bind("<End>", lambda evento: self._elegir_fila(len(self._filas) - 1))
		for widget in (self._cuerpo, self._encabezado):
			widget.bind("<MouseWheel>", self._al_girar_rueda)
			widget.bind("<Shift-MouseWheel>", self._al_girar_rueda_con_mayuscula)
		self._cuerpo.bind("<Configure>", lambda evento: self._programar_redibujo())

	# --- API pública -------------------------------------------------------

	def configurar(self, columnas: Sequence[ColumnaDeTabla], tolerancia: float | None) -> None:
		"""Vacía la tabla y la prepara para un cálculo nuevo con estas columnas."""
		self._columnas = list(columnas)
		self._tolerancia = tolerancia
		self._filas = []
		self._raiz_resaltada = False
		self._seleccion = None
		self._primera_fila_bajo_tolerancia = {}
		self._calcular_anchos_base()
		self._dibujar_todo()

	def agregar_fila(self, iteracion: Iteracion) -> None:
		"""Agrega una fila al final mientras el método corre, y la deja a la vista."""
		self._filas.append(iteracion)
		indice = len(self._filas) - 1
		self._registrar_errores_bajo_tolerancia(indice)

		if self._ensanchar_si_hace_falta(iteracion):
			self._dibujar_todo()
		else:
			if indice == 0:
				self._cuerpo.delete("vacio")
			self._dibujar_fila(indice)
			self._actualizar_lineas_verticales_y_region()
		self._cuerpo.yview_moveto(1.0)

	def finalizar(self, resaltar_raiz: bool) -> None:
		"""Marca el fin del cálculo: si terminó bien, pinta de ámbar la celda de la raíz."""
		self._raiz_resaltada = resaltar_raiz and bool(self._filas)
		if self._filas:
			self._redibujar_fila(len(self._filas) - 1)

	def seleccionar(self, indice: int | None) -> None:
		"""Selecciona una fila (sin avisar a `al_seleccionar`) y la deja a la vista."""
		self._seleccion = indice
		self._dibujar_seleccion()
		if indice is not None:
			self._mostrar_fila(indice)

	def establecer_decimales(self, decimales: int) -> None:
		"""Vuelve a formatear toda la tabla con otra cantidad de decimales."""
		self._decimales = decimales
		self._calcular_anchos_base()
		for iteracion in self._filas:
			self._ensanchar_si_hace_falta(iteracion)
		self._dibujar_todo()

	def limpiar(self) -> None:
		"""Deja la tabla vacía, con el mensaje de estado vacío."""
		self.configurar([], None)

	def texto_de_celda(self, indice_de_fila: int, clave: str) -> str:
		"""El texto que muestra una celda, tal cual se ve (útil para verificar la tabla)."""
		for columna in self._columnas:
			if columna.clave == clave:
				return self._texto(self._filas[indice_de_fila], columna)
		raise KeyError(clave)

	@property
	def cantidad_de_filas(self) -> int:
		return len(self._filas)

	# --- Contenido de las celdas ------------------------------------------

	@staticmethod
	def _valor(iteracion: Iteracion, columna: ColumnaDeTabla) -> object:
		if columna.clave == "numero":
			return iteracion.numero
		if columna.clave == "aproximacion":
			return iteracion.aproximacion
		if columna.clave == "error":
			return iteracion.error
		return iteracion.detalle.get(columna.clave)

	def _texto(self, iteracion: Iteracion, columna: ColumnaDeTabla) -> str:
		valor = self._valor(iteracion, columna)
		if valor is None:
			return "-" if columna.es_error else ""
		if isinstance(valor, tuple):
			return "; ".join(formatear_numero(float(componente), self._decimales) for componente in valor)
		if columna.formato is FormatoDeColumna.ENTERO:
			return str(int(valor))
		if columna.formato is FormatoDeColumna.SIGNO:
			return formatear_signo(float(valor))
		if abs(float(valor)) >= 1e7:
			# Una sucesión que diverge llega a números de 30 cifras: en notación científica se leen.
			return formatear_numero_legible(float(valor), self._decimales)
		return formatear_numero(float(valor), self._decimales)

	def _registrar_errores_bajo_tolerancia(self, indice: int) -> None:
		if self._tolerancia is None:
			return
		for indice_de_columna, columna in enumerate(self._columnas):
			if not columna.es_error or indice_de_columna in self._primera_fila_bajo_tolerancia:
				continue
			valor = self._valor(self._filas[indice], columna)
			if valor is not None and float(valor) < self._tolerancia:
				self._primera_fila_bajo_tolerancia[indice_de_columna] = indice

	# --- Medidas ------------------------------------------------------------

	def _calcular_anchos_base(self) -> None:
		medir_numero = self._tema.numeros.measure
		medir_encabezado = self._tema.numeros_destacados.measure
		margen = 2 * self._margen_de_celda
		ejemplo_numerico = SIGNO_MENOS + "00," + "0" * self._decimales
		self._anchos_base = []
		for columna in self._columnas:
			if columna.formato is FormatoDeColumna.ENTERO:
				ejemplo = "000"
			elif columna.formato is FormatoDeColumna.SIGNO:
				ejemplo = "< 0"
			else:
				ejemplo = ejemplo_numerico
			self._anchos_base.append(
				max(medir_encabezado(columna.encabezado), medir_numero(ejemplo)) + margen
			)

	def _ensanchar_si_hace_falta(self, iteracion: Iteracion) -> bool:
		"""Agranda las columnas donde un valor de esta fila no entra. Devuelve si cambió algo."""
		cambio = False
		for indice_de_columna, columna in enumerate(self._columnas):
			ancho = self._tema.numeros.measure(self._texto(iteracion, columna)) + 2 * self._margen_de_celda
			if ancho > self._anchos_base[indice_de_columna]:
				self._anchos_base[indice_de_columna] = ancho
				cambio = True
		return cambio

	def _calcular_bordes(self) -> None:
		total_base = sum(self._anchos_base)
		disponible = max(1, self._cuerpo.winfo_width() - 2 * self._tema.px(2))
		factor = 1.0
		if total_base and disponible > total_base:
			factor = min(_ESTIRAMIENTO_MAXIMO, disponible / total_base)
		self._anchos = [round(ancho * factor) for ancho in self._anchos_base]
		self._bordes = [0]
		for ancho in self._anchos:
			self._bordes.append(self._bordes[-1] + ancho)

	# --- Dibujo -------------------------------------------------------------

	def _programar_redibujo(self) -> None:
		if self._redibujo_pendiente is not None:
			self.after_cancel(self._redibujo_pendiente)
		self._redibujo_pendiente = self.after(60, self._dibujar_todo)

	def _dibujar_todo(self) -> None:
		self._redibujo_pendiente = None
		self._cuerpo.delete("all")
		self._encabezado.delete("all")
		self._calcular_bordes()
		ancho_total = self._bordes[-1]

		self._dibujar_encabezado()
		for indice in range(len(self._filas)):
			self._dibujar_fila(indice)
		self._actualizar_lineas_verticales_y_region()
		self._dibujar_seleccion()
		self._encabezado.configure(scrollregion=(0, 0, ancho_total, int(self._encabezado["height"])))

		if not self._filas:
			self._cuerpo.create_text(
				max(self._cuerpo.winfo_width(), ancho_total) / 2,
				self._tema.px(48),
				text=self._mensaje_vacio,
				fill=colores.TINTA_SUAVE,
				font=self._tema.interfaz,
				tags="vacio",
			)

	def _dibujar_encabezado(self) -> None:
		if not self._columnas:
			return
		alto = int(self._encabezado["height"])
		ancho_total = self._bordes[-1]
		for indice_de_columna, columna in enumerate(self._columnas):
			self._encabezado.create_text(
				*self._ancla_de_texto(indice_de_columna, alto / 2),
				text=columna.encabezado,
				anchor=self._ancla(columna),
				font=self._tema.numeros_destacados,
				fill=colores.TINTA,
			)
		for borde in self._bordes:
			self._encabezado.create_line(borde, self._tema.px(6), borde, alto, fill=colores.LINEA)
		self._encabezado.create_line(0, alto - 1, ancho_total, alto - 1, fill=colores.TINTA_SUAVE)

	def _ancla(self, columna: ColumnaDeTabla) -> str:
		return "center" if columna.formato is not FormatoDeColumna.NUMERO else "e"

	def _ancla_de_texto(self, indice_de_columna: int, y: float) -> tuple[float, float]:
		columna = self._columnas[indice_de_columna]
		if self._ancla(columna) == "center":
			return (self._bordes[indice_de_columna] + self._bordes[indice_de_columna + 1]) / 2, y
		return self._bordes[indice_de_columna + 1] - self._margen_de_celda, y

	def _dibujar_fila(self, indice: int) -> None:
		iteracion = self._filas[indice]
		arriba = indice * self._alto_de_fila
		abajo = arriba + self._alto_de_fila
		etiqueta_de_fila = f"fila{indice}"
		es_ultima = indice == len(self._filas) - 1

		for indice_de_columna, columna in enumerate(self._columnas):
			izquierda = self._bordes[indice_de_columna]
			derecha = self._bordes[indice_de_columna + 1]
			corrimiento = columna.desplazamiento_en_filas * self._alto_de_fila
			texto = self._texto(iteracion, columna)
			relleno = None
			if columna.es_raiz and self._raiz_resaltada and es_ultima:
				relleno = colores.AMBAR
			elif columna.es_error and self._primera_fila_bajo_tolerancia.get(indice_de_columna) == indice:
				relleno = colores.VERDE_CELDA
			if relleno is not None:
				self._cuerpo.create_rectangle(
					izquierda + 1,
					arriba + corrimiento + 1,
					derecha,
					abajo + corrimiento,
					fill=relleno,
					width=0,
					tags=(etiqueta_de_fila, "resaltado"),
				)
			self._cuerpo.create_text(
				*self._ancla_de_texto(indice_de_columna, arriba + corrimiento + self._alto_de_fila / 2),
				text=texto,
				anchor=self._ancla(columna),
				font=self._tema.numeros,
				fill=colores.TINTA,
				tags=(etiqueta_de_fila, "texto"),
			)
			if not columna.desplazamiento_en_filas:
				self._cuerpo.create_line(
					izquierda, abajo, derecha, abajo, fill=colores.LINEA, tags=(etiqueta_de_fila, "linea")
				)
			elif texto:
				# Caja suelta: las celdas vacías no se dibujan y la columna queda escalonada.
				self._cuerpo.create_rectangle(
					izquierda, arriba + corrimiento, derecha, abajo + corrimiento,
					outline=colores.LINEA, tags=(etiqueta_de_fila, "linea"),
				)
		self._cuerpo.tag_lower("seleccion")

	def _redibujar_fila(self, indice: int) -> None:
		self._cuerpo.delete(f"fila{indice}")
		self._dibujar_fila(indice)
		self._cuerpo.tag_raise("vertical")

	def _actualizar_lineas_verticales_y_region(self) -> None:
		self._cuerpo.delete("vertical")
		alto_total = len(self._filas) * self._alto_de_fila
		if self._filas:
			for indice_de_borde, borde in enumerate(self._bordes):
				# Un borde entre dos columnas corridas ya lo dibujan sus cajas.
				vecinas = self._columnas[max(0, indice_de_borde - 1):indice_de_borde + 1]
				if all(columna.desplazamiento_en_filas for columna in vecinas):
					continue
				self._cuerpo.create_line(borde, 0, borde, alto_total, fill=colores.LINEA, tags="vertical")
		self._cuerpo.configure(scrollregion=(0, 0, self._bordes[-1], alto_total))

	def _dibujar_seleccion(self) -> None:
		self._cuerpo.delete("seleccion")
		if self._seleccion is None or not (0 <= self._seleccion < len(self._filas)):
			return
		arriba = self._seleccion * self._alto_de_fila
		self._cuerpo.create_rectangle(
			0, arriba, self._bordes[-1], arriba + self._alto_de_fila,
			fill=colores.AZUL_TENUE, width=0, tags="seleccion",
		)
		self._cuerpo.create_rectangle(
			0, arriba, self._tema.px(3), arriba + self._alto_de_fila,
			fill=colores.AZUL, width=0, tags="seleccion",
		)
		self._cuerpo.tag_lower("seleccion")

	# --- Interacción ----------------------------------------------------------

	def _elegir_fila(self, indice: int) -> None:
		if not self._filas:
			return
		indice = max(0, min(len(self._filas) - 1, indice))
		self.seleccionar(indice)
		if self.al_seleccionar is not None:
			self.al_seleccionar(indice)

	def _mover_seleccion(self, delta: int) -> str:
		actual = self._seleccion if self._seleccion is not None else (len(self._filas) if delta < 0 else -1)
		self._elegir_fila(actual + delta)
		return "break"

	def _al_hacer_clic(self, evento: tk.Event) -> None:
		self._cuerpo.focus_set()
		indice = int(self._cuerpo.canvasy(evento.y) // self._alto_de_fila)
		if 0 <= indice < len(self._filas):
			self._elegir_fila(indice)

	def _mostrar_fila(self, indice: int) -> None:
		alto_total = len(self._filas) * self._alto_de_fila
		if alto_total <= 0:
			return
		primera, ultima = self._cuerpo.yview()
		arriba = indice * self._alto_de_fila / alto_total
		abajo = (indice + 1) * self._alto_de_fila / alto_total
		if arriba < primera:
			self._cuerpo.yview_moveto(arriba)
		elif abajo > ultima:
			self._cuerpo.yview_moveto(abajo - (ultima - primera))

	def _desplazar_horizontal(self, *argumentos: object) -> None:
		self._cuerpo.xview(*argumentos)
		self._encabezado.xview(*argumentos)

	def _al_girar_rueda(self, evento: tk.Event) -> str:
		self._cuerpo.yview_scroll(-3 * round(evento.delta / 120), "units")
		return "break"

	def _al_girar_rueda_con_mayuscula(self, evento: tk.Event) -> str:
		self._desplazar_horizontal("scroll", -3 * round(evento.delta / 120), "units")
		return "break"
