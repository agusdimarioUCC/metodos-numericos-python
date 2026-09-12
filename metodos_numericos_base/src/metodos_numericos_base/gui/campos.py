"""Widgets de entrada especiales: el teclado matemático y la grilla de un sistema Ax = b."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from typing import NamedTuple

from metodos_numericos_base.formato import formatear_valor_editable, leer_numero, subindice
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.tema import Tema
from metodos_numericos_base.sistemas import leer_sistema_desde_texto

TAMANO_MAXIMO_SISTEMA = 5
"""Los ejercicios de la materia llegan a 5×5; más grande no entra cómodo en la columna de datos."""


class _BotonDeTeclado(NamedTuple):
	"""Un botón del teclado matemático: lo que se ve y lo que se inserta.

	Casi siempre coinciden (`"("` inserta `"("`), pero no siempre: los
	botones de trigonometría muestran la notación en español que se
	enseña en la facultad (`sen`, `tg`) mientras insertan el nombre real
	de `math` en inglés (`sin(`, `tan(`), que es lo único que
	`evaluar_funcion` reconoce.
	"""

	etiqueta: str
	texto_a_insertar: str


_FILAS_DE_BOTONES_DEL_TECLADO: tuple[tuple[_BotonDeTeclado, ...], ...] = (
	(
		_BotonDeTeclado("x", "x"),
		_BotonDeTeclado("π", "pi"),
		_BotonDeTeclado("e", "e"),
		_BotonDeTeclado("(", "("),
		_BotonDeTeclado(")", ")"),
		_BotonDeTeclado(",", ","),
	),
	(
		_BotonDeTeclado("x²", "**2"),
		_BotonDeTeclado("xʸ", "**"),
		_BotonDeTeclado("√", "sqrt("),
		_BotonDeTeclado("∛", "cbrt("),
		_BotonDeTeclado("eˣ", "exp("),
		_BotonDeTeclado("10ˣ", "10**"),
	),
	(
		_BotonDeTeclado("sen", "sin("),
		_BotonDeTeclado("cos", "cos("),
		_BotonDeTeclado("tg", "tan("),
		_BotonDeTeclado("sen⁻¹", "asin("),
		_BotonDeTeclado("cos⁻¹", "acos("),
		_BotonDeTeclado("tg⁻¹", "atan("),
	),
	(
		_BotonDeTeclado("ln", "log("),
		_BotonDeTeclado("log₁₀", "log10("),
		_BotonDeTeclado("log₂", "log2("),
		_BotonDeTeclado("|x|", "fabs("),
	),
)


class TecladoMatematico(ttk.Frame):
	"""Botones estilo GeoGebra que insertan sintaxis matemática en un campo.

	Se construye una sola vez por panel, cuando ese panel tiene al menos
	un campo `EXPRESION_MATEMATICA`. Si hay más de uno (como `f(x)` y
	`f′(x)` en Newton-Raphson), rastrea cuál está enfocado mediante
	`<FocusIn>` — no se puede usar `focus_get()` en el momento del click,
	porque Tkinter ya movió el foco al botón antes de correr su `command`
	— y muestra "Escribiendo en: ..." para que se sepa dónde va a caer.
	Los botones no toman el foco con Tab (`takefocus=False`), para no
	obligar a atravesar 27 teclas para llegar al botón Calcular.
	"""

	def __init__(self, contenedor: tk.Widget, campos_de_expresion: list[tuple[str, ttk.Entry]]) -> None:
		super().__init__(contenedor)
		self._entrada_activa: ttk.Entry = campos_de_expresion[0][1]

		self._etiqueta_entrada_activa: ttk.Label | None = None
		if len(campos_de_expresion) > 1:
			self._etiqueta_entrada_activa = ttk.Label(
				self, text=f"Escribiendo en {campos_de_expresion[0][0]}", style="Chica.TLabel"
			)
			self._etiqueta_entrada_activa.pack(anchor="w", pady=(0, 3))

		for etiqueta, entrada in campos_de_expresion:
			entrada.bind(
				"<FocusIn>",
				lambda evento, entrada=entrada, etiqueta=etiqueta: self._fijar_entrada_activa(entrada, etiqueta),
				add="+",
			)

		grilla = ttk.Frame(self)
		grilla.pack(anchor="w")
		for numero_de_fila, fila_de_botones in enumerate(_FILAS_DE_BOTONES_DEL_TECLADO):
			for numero_de_columna, boton in enumerate(fila_de_botones):
				self._armar_tecla(
					grilla, boton.etiqueta, lambda texto=boton.texto_a_insertar: self._insertar_texto(texto)
				).grid(row=numero_de_fila, column=numero_de_columna, padx=1, pady=1)

		# Las teclas de edición van en una columna aparte, a la derecha, como en una calculadora.
		columna_de_acciones = max(len(fila) for fila in _FILAS_DE_BOTONES_DEL_TECLADO)
		acciones = (
			("⌫", self._borrar_caracter_anterior),
			("←", lambda: self._mover_cursor(-1)),
			("→", lambda: self._mover_cursor(1)),
		)
		for numero_de_fila, (etiqueta, accion) in enumerate(acciones):
			self._armar_tecla(grilla, etiqueta, accion).grid(
				row=numero_de_fila, column=columna_de_acciones, padx=(4, 1), pady=1
			)

	@staticmethod
	def _armar_tecla(contenedor: tk.Widget, etiqueta: str, accion: Callable[[], None]) -> ttk.Button:
		return ttk.Button(contenedor, text=etiqueta, style="Tecla.TButton", command=accion, takefocus=False)

	def _fijar_entrada_activa(self, entrada: ttk.Entry, etiqueta: str) -> None:
		self._entrada_activa = entrada
		if self._etiqueta_entrada_activa is not None:
			self._etiqueta_entrada_activa.config(text=f"Escribiendo en {etiqueta}")

	def _insertar_texto(self, texto: str) -> None:
		entrada = self._entrada_activa
		if entrada.selection_present():
			entrada.delete(tk.SEL_FIRST, tk.SEL_LAST)
		posicion = entrada.index(tk.INSERT)
		entrada.insert(posicion, texto)
		entrada.icursor(posicion + len(texto))
		entrada.focus_set()
		entrada.event_generate("<<Editado>>")

	def _borrar_caracter_anterior(self) -> None:
		entrada = self._entrada_activa
		posicion = entrada.index(tk.INSERT)
		if posicion > 0:
			entrada.delete(posicion - 1, posicion)
		entrada.focus_set()
		entrada.event_generate("<<Editado>>")

	def _mover_cursor(self, delta: int) -> None:
		entrada = self._entrada_activa
		posicion = entrada.index(tk.INSERT)
		entrada.icursor(max(0, min(len(entrada.get()), posicion + delta)))
		entrada.focus_set()


class GrillaDeSistema(ttk.Frame):
	"""Entradas para un sistema Ax = b, dibujado como la matriz extendida de los apuntes.

	Un selector "Ecuaciones" (1 a `TAMANO_MAXIMO_SISTEMA`) y una casilla por coeficiente, con la columna
	de términos independientes separada por una raya y en rojo, como en
	los apuntes. Cambiar n redimensiona la grilla conservando los valores
	que siguen entrando (lo que sobra se descarta, lo nuevo arranca en 0).

	Se construye una sola vez, pero a diferencia de `PanelDeMetodo` sí
	reconstruye sus celdas cuando cambia `n`: son `Entry` simples,
	baratos de destruir y recrear.

	`al_cambiar`, si se asigna después de construir la grilla, se llama
	cada vez que el usuario termina de editar una celda (al perder el
	foco) o cambia el tamaño. Es lo que usa `VentanaMetodosNumericos`
	para sincronizar el mismo sistema entre las grillas de distintos
	métodos (ver `vincular_grillas_de_sistema`); no se llama mientras
	`establecer_sistema` está aplicando un cambio que vino de afuera,
	para no generar un ping-pong infinito entre dos grillas enlazadas.
	"""

	def __init__(self, contenedor: tk.Widget, valor_por_defecto: str, tema: Tema) -> None:
		super().__init__(contenedor)
		self._tema = tema
		self.al_cambiar: Callable[[], None] | None = None
		self._suprimir_aviso = False

		try:
			filas_iniciales, terminos_iniciales = leer_sistema_desde_texto(valor_por_defecto)
		except ValueError:
			filas_iniciales, terminos_iniciales = [[0.0]], [0.0]
		self._tamano = len(filas_iniciales)

		selector = ttk.Frame(self)
		selector.pack(anchor="w", pady=(0, tema.px(6)))
		ttk.Label(selector, text="Ecuaciones").pack(side="left")
		self._variable_tamano = tk.StringVar(value=str(self._tamano))
		self._selector_tamano = ttk.Spinbox(
			selector,
			from_=1,
			to=TAMANO_MAXIMO_SISTEMA,
			width=3,
			textvariable=self._variable_tamano,
			command=self._aplicar_tamano,
			font=tema.interfaz,
		)
		self._selector_tamano.pack(side="left", padx=(tema.px(8), 0))
		self._selector_tamano.bind("<Return>", lambda evento: self._aplicar_tamano())
		self._selector_tamano.bind("<FocusOut>", lambda evento: self._aplicar_tamano())

		self._grilla = ttk.Frame(self)
		self._grilla.pack(anchor="w")
		self._entradas_coeficientes: list[list[ttk.Entry]] = []
		self._entradas_terminos: list[ttk.Entry] = []
		self._armar_grilla(filas_iniciales, terminos_iniciales)

	def _armar_grilla(self, filas: list[list[float]], terminos: list[float]) -> None:
		for widget in self._grilla.winfo_children():
			widget.destroy()
		self._entradas_coeficientes = []
		self._entradas_terminos = []
		px = self._tema.px
		columna_del_termino = self._tamano + 1

		for columna in range(self._tamano):
			ttk.Label(self._grilla, text=f"x{subindice(columna + 1)}", style="Encabezado.TLabel").grid(
				row=0, column=columna, pady=(0, px(2))
			)
		ttk.Label(self._grilla, text="b", style="Termino.TLabel").grid(row=0, column=columna_del_termino, pady=(0, px(2)))
		tk.Frame(self._grilla, width=px(1), background=colores.LINEA_FUERTE).grid(
			row=1, column=self._tamano, rowspan=self._tamano, sticky="ns", padx=px(5)
		)

		for fila in range(self._tamano):
			entradas_fila = []
			for columna in range(self._tamano):
				entrada = self._armar_celda("Celda.TEntry", filas[fila][columna])
				entrada.grid(row=fila + 1, column=columna, padx=px(1), pady=px(1))
				entradas_fila.append(entrada)
			self._entradas_coeficientes.append(entradas_fila)

			entrada_termino = self._armar_celda("CeldaTermino.TEntry", terminos[fila])
			entrada_termino.grid(row=fila + 1, column=columna_del_termino, padx=px(1), pady=px(1))
			self._entradas_terminos.append(entrada_termino)

	def _armar_celda(self, estilo: str, valor: float) -> ttk.Entry:
		entrada = ttk.Entry(self._grilla, width=5, style=estilo, font=self._tema.numeros, justify="right")
		entrada.insert(0, formatear_valor_editable(valor))
		entrada.bind("<FocusOut>", self._avisar_cambio)
		entrada.bind("<Key>", lambda evento, entrada=entrada, estilo=estilo: entrada.configure(style=estilo), add="+")
		return entrada

	def _leer_celdas_sin_validar(self) -> tuple[list[list[float]], list[float]]:
		def leer(entrada: ttk.Entry) -> float:
			try:
				return leer_numero(entrada.get())
			except ValueError:
				return 0.0

		filas = [[leer(entrada) for entrada in fila] for fila in self._entradas_coeficientes]
		return filas, [leer(entrada) for entrada in self._entradas_terminos]

	def _aplicar_tamano(self) -> None:
		try:
			nuevo_tamano = int(self._variable_tamano.get().strip())
		except ValueError:
			nuevo_tamano = self._tamano
		nuevo_tamano = max(1, min(TAMANO_MAXIMO_SISTEMA, nuevo_tamano))
		self._variable_tamano.set(str(nuevo_tamano))
		if nuevo_tamano == self._tamano:
			return

		filas_actuales, terminos_actuales = self._leer_celdas_sin_validar()
		filas = [
			[
				filas_actuales[fila][columna] if fila < self._tamano and columna < self._tamano else 0.0
				for columna in range(nuevo_tamano)
			]
			for fila in range(nuevo_tamano)
		]
		terminos = [terminos_actuales[fila] if fila < self._tamano else 0.0 for fila in range(nuevo_tamano)]
		self._tamano = nuevo_tamano
		self._armar_grilla(filas, terminos)
		self._avisar_cambio()

	def _avisar_cambio(self, evento: object = None) -> None:
		if not self._suprimir_aviso and self.al_cambiar is not None:
			self.al_cambiar()

	def establecer_sistema(self, filas: list[list[float]], terminos: list[float]) -> None:
		"""Reemplaza el contenido de la grilla por el sistema dado.

		Usado por `VentanaMetodosNumericos` para copiar el sistema de otra
		grilla enlazada. Suprime `al_cambiar` mientras reconstruye, para no
		reenviar el mismo cambio de vuelta a la grilla de origen.
		"""
		self._suprimir_aviso = True
		try:
			self._tamano = len(filas)
			self._variable_tamano.set(str(self._tamano))
			self._armar_grilla(filas, terminos)
		finally:
			self._suprimir_aviso = False

	def obtener_sistema(self) -> tuple[list[list[float]], list[float]]:
		"""Lee la grilla y devuelve (filas_de_coeficientes, terminos_independientes).

		Raises:
			ValueError: Si alguna celda no es un número; la celda queda
				marcada en rojo hasta que se la vuelva a editar.
		"""
		filas: list[list[float]] = []
		for numero_de_fila, entradas_fila in enumerate(self._entradas_coeficientes, start=1):
			fila: list[float] = []
			for numero_de_columna, entrada in enumerate(entradas_fila, start=1):
				fila.append(
					self._leer_celda(
						entrada, f"a{subindice(numero_de_fila)}{subindice(numero_de_columna)}"
					)
				)
			filas.append(fila)

		terminos_independientes = [
			self._leer_celda(entrada, f"b{subindice(numero_de_fila)}")
			for numero_de_fila, entrada in enumerate(self._entradas_terminos, start=1)
		]
		return filas, terminos_independientes

	@staticmethod
	def _leer_celda(entrada: ttk.Entry, nombre: str) -> float:
		try:
			return leer_numero(entrada.get())
		except ValueError as error:
			entrada.configure(style="CeldaInvalida.TEntry")
			raise ValueError(f"{nombre}: {error}") from error
