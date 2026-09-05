"""Toolkit de Tkinter compartido para la GUI unificada de métodos numéricos."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Sequence
from tkinter import font as tkfont
from tkinter import ttk
from typing import NamedTuple

from metodos_numericos_base.descriptor import DescriptorDeMetodo, TipoDeCampo
from metodos_numericos_base.errores import EntradaInvalidaError, NoConvergeError
from metodos_numericos_base.expresiones import compilar_funcion
from metodos_numericos_base.iteracion import Iteracion, formatear_aproximacion
from metodos_numericos_base.sistemas import leer_sistema_desde_texto

_FUENTES_MATEMATICAS_PREFERIDAS = ("Cambria Math", "STIX Two Math", "DejaVu Sans")
_TAMANO_MAXIMO_SISTEMA = 8  # mismo tope que reordenar_para_dominancia_diagonal


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


def _formatear_valor_de_celda(valor: float) -> str:
	"""Formatea un número para precargarlo en una celda, sin ceros de sobra (12 en vez de 12.0)."""
	return f"{valor:g}"


class _GrillaDeSistema(ttk.Frame):
	"""Entradas para un sistema Ax = b: tamaño ajustable + una casilla por valor.

	Se construye una sola vez, pero a diferencia de `PanelDeMetodo` sí
	reconstruye su grilla interna cuando cambia `n` — acá no hay ningún
	`Treeview` cuyos encabezados se puedan perder; son `Entry` simples,
	baratos de destruir y recrear.
	"""

	def __init__(self, contenedor: tk.Widget, valor_por_defecto: str, fuente_monoespaciada: tkfont.Font) -> None:
		super().__init__(contenedor)
		self._fuente = fuente_monoespaciada

		try:
			filas_iniciales, terminos_iniciales = leer_sistema_desde_texto(valor_por_defecto)
		except ValueError:
			filas_iniciales, terminos_iniciales = [[0.0]], [0.0]
		self._tamano = len(filas_iniciales)

		selector = ttk.Frame(self)
		selector.pack(fill="x", pady=(0, 4))
		ttk.Label(selector, text="Tamaño del sistema (n):").pack(side="left")
		self._entrada_tamano = ttk.Entry(selector, width=4)
		self._entrada_tamano.insert(0, str(self._tamano))
		self._entrada_tamano.bind("<Return>", lambda evento: self._regenerar())
		self._entrada_tamano.pack(side="left", padx=(4, 4))
		ttk.Button(selector, text="Generar campos", command=self._regenerar).pack(side="left")

		self._grilla = ttk.Frame(self)
		self._grilla.pack()
		self._entradas_coeficientes: list[list[ttk.Entry]] = []
		self._entradas_terminos: list[ttk.Entry] = []
		self._armar_grilla(filas_iniciales, terminos_iniciales)

	def _armar_grilla(
			self, filas: list[list[float]] | None = None, terminos: list[float] | None = None
	) -> None:
		for widget in self._grilla.winfo_children():
			widget.destroy()
		self._entradas_coeficientes = []
		self._entradas_terminos = []

		for columna in range(self._tamano):
			ttk.Label(self._grilla, text=f"x{columna + 1}").grid(row=0, column=columna)
		ttk.Label(self._grilla, text="=").grid(row=0, column=self._tamano, padx=6)
		ttk.Label(self._grilla, text="b").grid(row=0, column=self._tamano + 1)

		for fila in range(self._tamano):
			entradas_fila = []
			for columna in range(self._tamano):
				valor = 0.0
				if filas and fila < len(filas) and columna < len(filas[fila]):
					valor = filas[fila][columna]
				entrada = ttk.Entry(self._grilla, width=6, font=self._fuente, justify="right")
				entrada.insert(0, _formatear_valor_de_celda(valor))
				entrada.grid(row=fila + 1, column=columna, padx=2, pady=1)
				entradas_fila.append(entrada)
			self._entradas_coeficientes.append(entradas_fila)

			valor_termino = terminos[fila] if terminos and fila < len(terminos) else 0.0
			entrada_termino = ttk.Entry(self._grilla, width=6, font=self._fuente, justify="right")
			entrada_termino.insert(0, _formatear_valor_de_celda(valor_termino))
			entrada_termino.grid(row=fila + 1, column=self._tamano + 1, padx=2, pady=1)
			self._entradas_terminos.append(entrada_termino)

	def _regenerar(self) -> None:
		try:
			nuevo_tamano = int(self._entrada_tamano.get().strip())
		except ValueError:
			return
		nuevo_tamano = max(1, min(_TAMANO_MAXIMO_SISTEMA, nuevo_tamano))
		self._entrada_tamano.delete(0, "end")
		self._entrada_tamano.insert(0, str(nuevo_tamano))
		self._tamano = nuevo_tamano
		self._armar_grilla()

	def obtener_sistema(self) -> tuple[list[list[float]], list[float]]:
		"""Lee la grilla y devuelve (filas_de_coeficientes, terminos_independientes)."""
		filas: list[list[float]] = []
		for numero_de_fila, entradas_fila in enumerate(self._entradas_coeficientes, start=1):
			fila: list[float] = []
			for numero_de_columna, entrada in enumerate(entradas_fila, start=1):
				texto = entrada.get().strip()
				try:
					fila.append(float(texto))
				except ValueError as error:
					raise ValueError(
						f"fila {numero_de_fila}, columna {numero_de_columna}: "
						f"{texto!r} no es un número válido"
					) from error
			filas.append(fila)

		terminos_independientes: list[float] = []
		for numero_de_fila, entrada in enumerate(self._entradas_terminos, start=1):
			texto = entrada.get().strip()
			try:
				terminos_independientes.append(float(texto))
			except ValueError as error:
				raise ValueError(
					f"fila {numero_de_fila}, término independiente: {texto!r} no es un número válido"
				) from error

		return filas, terminos_independientes


class _TecladoMatematico(ttk.Frame):
	"""Botones estilo GeoGebra que insertan sintaxis matemática en un campo.

	Se construye una sola vez por pestaña, cuando esa pestaña tiene al
	menos un campo `EXPRESION_MATEMATICA`. Si hay más de uno (como
	`f(x)` y `f'(x)` en Newton-Raphson), rastrea cuál está enfocado
	mediante `<FocusIn>` — no se puede usar `focus_get()` en el momento
	del click, porque Tkinter ya movió el foco al botón antes de correr
	su `command`.
	"""

	def __init__(
			self,
			contenedor: tk.Widget,
			campos_de_expresion: list[tuple[str, ttk.Entry]],
	) -> None:
		super().__init__(contenedor)
		self._entrada_activa: ttk.Entry = campos_de_expresion[0][1]

		self._etiqueta_entrada_activa: ttk.Label | None = None
		if len(campos_de_expresion) > 1:
			self._etiqueta_entrada_activa = ttk.Label(
				self, text=f"Escribiendo en: {campos_de_expresion[0][0]}", foreground="#555555"
			)
			self._etiqueta_entrada_activa.pack(anchor="w", pady=(0, 2))

		for etiqueta, entrada in campos_de_expresion:
			entrada.bind(
				"<FocusIn>",
				lambda evento, entrada=entrada, etiqueta=etiqueta: self._fijar_entrada_activa(
					entrada, etiqueta
				),
			)

		# Botones tk.Button clásicos, no ttk.Button: en Windows, ttk.Button
		# se dibuja con el tema nativo "vista", que ignora el `padding` de
		# estilo e impone su propio tamaño mínimo. tk.Button respeta
		# `font`/`padx`/`pady` de forma directa y predecible.
		#
		# Fuente de la interfaz (Segoe UI en Windows), NO la fuente
		# matemática (Cambria Math): esta última reserva mucha altura de
		# línea para símbolos apilados (integrales, radicales extendidos)
		# — perfecta para el campo de f(x), pero en un botón chico eso
		# infla el `linespace` a ~65px y con 5 filas se comía la ventana
		# entera. Segoe UI también renderiza bien √, π, ² y ⁻¹.
		fuente_boton = tkfont.Font(family=tkfont.nametofont("TkDefaultFont").actual("family"), size=9)

		grilla = ttk.Frame(self)
		grilla.pack()
		for numero_de_fila, fila_de_botones in enumerate(_FILAS_DE_BOTONES_DEL_TECLADO):
			for numero_de_columna, boton in enumerate(fila_de_botones):
				tk.Button(
					grilla,
					text=boton.etiqueta,
					width=3,
					font=fuente_boton,
					padx=1,
					pady=0,
					command=lambda texto=boton.texto_a_insertar: self._insertar_texto(texto),
				).grid(row=numero_de_fila, column=numero_de_columna, padx=1, pady=1)

		fila_de_acciones = len(_FILAS_DE_BOTONES_DEL_TECLADO)
		tk.Button(
			grilla,
			text="⌫",
			width=3,
			font=fuente_boton,
			padx=1,
			pady=0,
			command=self._borrar_caracter_anterior,
		).grid(row=fila_de_acciones, column=0, padx=1, pady=1)
		tk.Button(
			grilla,
			text="←",
			width=3,
			font=fuente_boton,
			padx=1,
			pady=0,
			command=lambda: self._mover_cursor(-1),
		).grid(row=fila_de_acciones, column=1, padx=1, pady=1)
		tk.Button(
			grilla,
			text="→",
			width=3,
			font=fuente_boton,
			padx=1,
			pady=0,
			command=lambda: self._mover_cursor(1),
		).grid(row=fila_de_acciones, column=2, padx=1, pady=1)

	def _fijar_entrada_activa(self, entrada: ttk.Entry, etiqueta: str) -> None:
		self._entrada_activa = entrada
		if self._etiqueta_entrada_activa is not None:
			self._etiqueta_entrada_activa.config(text=f"Escribiendo en: {etiqueta}")

	def _insertar_texto(self, texto: str) -> None:
		entrada = self._entrada_activa
		posicion = entrada.index(tk.INSERT)
		entrada.insert(posicion, texto)
		entrada.icursor(posicion + len(texto))
		entrada.focus_set()

	def _borrar_caracter_anterior(self) -> None:
		entrada = self._entrada_activa
		posicion = entrada.index(tk.INSERT)
		if posicion > 0:
			entrada.delete(posicion - 1, posicion)
		entrada.focus_set()

	def _mover_cursor(self, delta: int) -> None:
		entrada = self._entrada_activa
		posicion = entrada.index(tk.INSERT)
		longitud = len(entrada.get())
		entrada.icursor(max(0, min(longitud, posicion + delta)))
		entrada.focus_set()


def elegir_fuente_matematica(tamano: int = 11) -> tkfont.Font:
	"""Elige la mejor fuente disponible en el sistema para símbolos matemáticos.

	Prueba una lista de fuentes con buen soporte de símbolos (√, π, ², etc.)
	de más a menos preferida, y usa la fuente por defecto de Tkinter si
	ninguna está instalada.
	"""
	familias_disponibles = set(tkfont.families())
	for familia in _FUENTES_MATEMATICAS_PREFERIDAS:
		if familia in familias_disponibles:
			return tkfont.Font(family=familia, size=tamano)
	return tkfont.nametofont("TkDefaultFont").copy()


def elegir_fuente_monoespaciada(tamano: int = 11) -> tkfont.Font:
	"""Elige una fuente monoespaciada para texto tabular (matrices, verificaciones).

	Prueba la fuente monoespaciada por defecto de Tkinter y cae a la
	fuente por defecto si el sistema no tiene ninguna registrada con ese
	nombre lógico.
	"""
	try:
		fuente = tkfont.nametofont("TkFixedFont").copy()
	except tk.TclError:
		fuente = tkfont.nametofont("TkDefaultFont").copy()
	fuente.configure(size=tamano)
	return fuente


class PanelDeMetodo(ttk.Frame):
	"""Una pestaña de la ventana unificada: el panel de entradas y resultados de un método.

	Se construye una única vez a partir de un `DescriptorDeMetodo` —
	campos de entrada, tabla de iteraciones, etiquetas de resultado —
	y nunca reconstruye ni reconfigura esos widgets después. Cambiar de
	pestaña en el `Notebook` solo muestra u oculta este frame; no hay
	ninguna operación de Tkinter que se repita ni que pueda perder
	encabezados o dejar widgets superpuestos.
	"""

	def __init__(
			self,
			contenedor: tk.Widget,
			descriptor: DescriptorDeMetodo,
			fuente_matematica: tkfont.Font,
			fuente_monoespaciada: tkfont.Font,
	) -> None:
		super().__init__(contenedor, padding=10)
		self._descriptor = descriptor
		self._fuente_matematica = fuente_matematica
		self._fuente_monoespaciada = fuente_monoespaciada
		self._widgets: dict[str, object] = {}

		ttk.Label(self, text=descriptor.descripcion, wraplength=560, justify="left").pack(
			fill="x", padx=10, pady=(10, 0)
		)
		campos_de_expresion = self._armar_panel_entradas()
		if campos_de_expresion:
			_TecladoMatematico(self, campos_de_expresion).pack(fill="x", padx=10, pady=(0, 10))
		ttk.Button(self, text="Calcular", command=self._calcular).pack(pady=10)
		self._armar_tabla_iteraciones()

		self._etiqueta_advertencia = ttk.Label(
			self, text="", foreground="#b8860b", wraplength=560, justify="left"
		)
		self._etiqueta_advertencia.pack(fill="x", padx=10, pady=(8, 0))

		self._etiqueta_resultado = ttk.Label(
			self, text="", font=fuente_matematica, foreground="#1a7f37"
		)
		self._etiqueta_resultado.pack(pady=(8, 0))

		self._etiqueta_verificacion = ttk.Label(
			self, text="", font=fuente_monoespaciada, foreground="#555555", justify="left"
		)
		self._etiqueta_verificacion.pack(fill="x", padx=10, pady=(4, 0))

		self._etiqueta_error = ttk.Label(self, text="", foreground="#c0392b", wraplength=560, justify="left")
		self._etiqueta_error.pack(fill="x", padx=10, pady=(4, 10))

	def _armar_panel_entradas(self) -> list[tuple[str, ttk.Entry]]:
		panel = ttk.Frame(self, padding=(10, 0))
		panel.pack(fill="x")
		panel.columnconfigure(1, weight=1)

		campos_de_expresion: list[tuple[str, ttk.Entry]] = []
		for fila, campo in enumerate(self._descriptor.campos):
			ttk.Label(panel, text=campo.etiqueta).grid(
				row=fila, column=0, sticky="nw", pady=2, padx=(0, 8)
			)

			if campo.tipo is TipoDeCampo.EXPRESION_MATEMATICA:
				widget = ttk.Entry(panel, width=30, font=self._fuente_matematica)
				widget.insert(0, campo.valor_por_defecto)
				widget.bind("<Return>", lambda evento: self._calcular())
				widget.grid(row=fila, column=1, sticky="we", pady=2)
				self._widgets[campo.nombre] = widget
				campos_de_expresion.append((campo.etiqueta, widget))
			elif campo.tipo is TipoDeCampo.NUMERO:
				widget = ttk.Entry(panel, width=30)
				widget.insert(0, campo.valor_por_defecto)
				widget.bind("<Return>", lambda evento: self._calcular())
				widget.grid(row=fila, column=1, sticky="we", pady=2)
				self._widgets[campo.nombre] = widget
			elif campo.tipo is TipoDeCampo.TEXTO_MULTILINEA:
				widget = tk.Text(
					panel, width=30, height=campo.cantidad_de_lineas, font=self._fuente_monoespaciada
				)
				widget.insert("1.0", campo.valor_por_defecto)
				widget.grid(row=fila, column=1, sticky="we", pady=2)
				self._widgets[campo.nombre] = widget
			elif campo.tipo is TipoDeCampo.CASILLA_DE_VERIFICACION:
				variable = tk.BooleanVar(
					value=campo.valor_por_defecto.strip().lower() in ("si", "sí", "true", "1")
				)
				ttk.Checkbutton(panel, variable=variable).grid(row=fila, column=1, sticky="w", pady=2)
				self._widgets[campo.nombre] = variable
			elif campo.tipo is TipoDeCampo.SISTEMA_DE_ECUACIONES:
				widget = _GrillaDeSistema(panel, campo.valor_por_defecto, self._fuente_monoespaciada)
				widget.grid(row=fila, column=1, sticky="w", pady=2)
				self._widgets[campo.nombre] = widget
			else:
				raise AssertionError(f"Tipo de campo no soportado: {campo.tipo}")

		return campos_de_expresion

	def _armar_tabla_iteraciones(self) -> None:
		contenedor = ttk.Frame(self)
		contenedor.pack(fill="both", expand=True, padx=10)
		contenedor.rowconfigure(0, weight=1)
		contenedor.columnconfigure(0, weight=1)

		self._tabla_iteraciones = ttk.Treeview(
			contenedor,
			columns=("iteracion", "aproximacion", "error"),
			show="headings",
			height=10,
		)
		self._tabla_iteraciones.heading("iteracion", text="Iteración")
		self._tabla_iteraciones.heading("aproximacion", text=self._descriptor.encabezado_de_aproximacion)
		self._tabla_iteraciones.heading("error", text="Error")
		self._tabla_iteraciones.column("iteracion", width=80, anchor="center")
		self._tabla_iteraciones.column("aproximacion", width=260)
		self._tabla_iteraciones.column("error", width=140, anchor="e")

		scroll_vertical = ttk.Scrollbar(contenedor, orient="vertical", command=self._tabla_iteraciones.yview)
		scroll_horizontal = ttk.Scrollbar(
			contenedor, orient="horizontal", command=self._tabla_iteraciones.xview
		)
		self._tabla_iteraciones.configure(
			yscrollcommand=scroll_vertical.set, xscrollcommand=scroll_horizontal.set
		)

		self._tabla_iteraciones.grid(row=0, column=0, sticky="nsew")
		scroll_vertical.grid(row=0, column=1, sticky="ns")
		scroll_horizontal.grid(row=1, column=0, sticky="ew")

	def _leer_valores(self) -> dict[str, object]:
		valores: dict[str, object] = {}
		for campo in self._descriptor.campos:
			widget = self._widgets[campo.nombre]
			if campo.tipo is TipoDeCampo.EXPRESION_MATEMATICA:
				texto = widget.get().strip()
				try:
					valores[campo.nombre] = compilar_funcion(texto)
				except Exception as error:
					raise EntradaInvalidaError(f"{campo.etiqueta} {texto!r}: {error}") from error
			elif campo.tipo is TipoDeCampo.NUMERO:
				texto = widget.get().strip()
				try:
					valores[campo.nombre] = float(texto)
				except ValueError as error:
					raise EntradaInvalidaError(
						f"{campo.etiqueta} {texto!r} no es un número válido"
					) from error
			elif campo.tipo is TipoDeCampo.TEXTO_MULTILINEA:
				valores[campo.nombre] = widget.get("1.0", "end")
			elif campo.tipo is TipoDeCampo.CASILLA_DE_VERIFICACION:
				valores[campo.nombre] = widget.get()
			elif campo.tipo is TipoDeCampo.SISTEMA_DE_ECUACIONES:
				valores[campo.nombre] = widget.obtener_sistema()
			else:
				raise AssertionError(f"Tipo de campo no soportado: {campo.tipo}")
		return valores

	def _calcular(self) -> None:
		self.limpiar_resultados()
		try:
			valores = self._leer_valores()
			resultado = self._descriptor.ejecutar(valores, self.registrar_iteracion)
		except (ValueError, ArithmeticError, NoConvergeError) as error:
			self._etiqueta_error.config(text=str(error))
		except Exception as error:
			self._etiqueta_error.config(text=f"No se pudo calcular: {error}")
		else:
			self._etiqueta_advertencia.config(text="\n".join(resultado.advertencias))
			self._etiqueta_resultado.config(
				text=f"{resultado.etiqueta_del_valor}: {resultado.valor_formateado}  "
				f"(en {resultado.cantidad_de_iteraciones} iteraciones)"
			)
			self._etiqueta_verificacion.config(text="\n".join(resultado.lineas_de_verificacion))

	def registrar_iteracion(self, iteracion: Iteracion) -> None:
		"""Agrega una fila a la tabla de iteraciones. Sirve como `reportar_iteracion`."""
		self._tabla_iteraciones.insert(
			"",
			"end",
			values=(
				iteracion.numero,
				formatear_aproximacion(iteracion.aproximacion),
				f"{float(iteracion.error):.6f}",
			),
		)
		self._tabla_iteraciones.yview_moveto(1)
		self.update_idletasks()

	def limpiar_resultados(self) -> None:
		"""Borra la tabla de iteraciones y los mensajes de advertencia/resultado/error previos."""
		self._tabla_iteraciones.delete(*self._tabla_iteraciones.get_children())
		self._etiqueta_advertencia.config(text="")
		self._etiqueta_resultado.config(text="")
		self._etiqueta_verificacion.config(text="")
		self._etiqueta_error.config(text="")


class VentanaMetodosNumericos(tk.Tk):
	"""La única ventana de la aplicación: un `Notebook` con una pestaña por método.

	No conoce ningún método concreto — recibe una secuencia de
	`DescriptorDeMetodo` y arma una pestaña por cada uno. El orden de la
	secuencia es el orden de las pestañas.
	"""

	def __init__(self, descriptores: Sequence[DescriptorDeMetodo]) -> None:
		super().__init__()
		self.title("Métodos Numéricos")
		self.minsize(620, 640)

		# Las fuentes necesitan un root de Tk vivo (usan tkfont.families()/
		# nametofont), por eso se crean acá y no a nivel de módulo.
		fuente_matematica = elegir_fuente_matematica()
		fuente_monoespaciada = elegir_fuente_monoespaciada()

		cuaderno = ttk.Notebook(self)
		cuaderno.pack(fill="both", expand=True)
		for descriptor in descriptores:
			panel = PanelDeMetodo(cuaderno, descriptor, fuente_matematica, fuente_monoespaciada)
			cuaderno.add(panel, text=descriptor.nombre_para_mostrar)

	def ejecutar(self) -> None:
		"""Inicia el bucle principal de la GUI. Bloquea hasta que se cierra la ventana."""
		self.mainloop()
