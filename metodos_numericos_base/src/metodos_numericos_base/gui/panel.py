"""El panel de un método: datos a la izquierda, gráfico y tabla (o matrices) a la derecha."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk

from metodos_numericos_base.descriptor import DescriptorDeMetodo, ResultadoDeMetodo, TipoDeCampo
from metodos_numericos_base.errores import EntradaInvalidaError, NoConvergeError
from metodos_numericos_base.expresiones import compilar_funcion
from metodos_numericos_base.formato import (
	formatear_numero,
	formatear_numero_legible,
	formatear_valor_corto,
	leer_numero,
	subindice,
)
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.campos import GrillaDeSistema, TecladoMatematico
from metodos_numericos_base.gui.grafico import LienzoDelGrafico
from metodos_numericos_base.gui.matrices import VistaDeMatrices
from metodos_numericos_base.gui.tabla import TablaDeIteraciones
from metodos_numericos_base.gui.tema import Tema, mostrar_barra_solo_si_hace_falta
from metodos_numericos_base.iteracion import Iteracion

TOLERANCIA_POR_DEFECTO = "0,001"
MAXIMO_DE_ITERACIONES_POR_DEFECTO = "100"
DECIMALES_POR_DEFECTO = 4
DECIMALES_MAXIMOS = 10
_ESPERA_DE_LA_VISTA_PREVIA_EN_MS = 400


class PanelDeMetodo(ttk.Frame):
	"""Todo lo de un método: encabezado, datos, criterio de parada, resultado, gráfico y tabla.

	Se construye una única vez a partir de un `DescriptorDeMetodo` y nunca
	reconstruye sus widgets después: cambiar de método en la barra
	lateral solo trae este panel al frente. Guarda los valores e
	iteraciones crudas del último cálculo, así que cambiar los decimales
	vuelve a formatear tabla, matrices y resultado sin recalcular.

	El único `try/except` de toda la GUI está en `_calcular`: los errores
	de entrada (`EntradaInvalidaError`) marcan el campo en rojo; los del
	método se muestran en el bloque de resultado, traducidos a qué hacer.
	"""

	def __init__(self, contenedor: tk.Widget, descriptor: DescriptorDeMetodo, tema: Tema) -> None:
		super().__init__(contenedor)
		self._descriptor = descriptor
		self._tema = tema
		self._widgets: dict[str, object] = {}
		self._entradas: dict[str, ttk.Entry] = {}
		self._estilos_de_entrada: dict[str, str] = {}
		self._iteraciones: list[Iteracion] = []
		self._valores: dict[str, object] | None = None
		self._resultado: ResultadoDeMetodo | None = None
		self._mensaje_de_error: str | None = None
		self._datos_del_ultimo_calculo: dict[str, str] | None = None
		self._vista_previa_pendiente: str | None = None
		self._variable_decimales = tk.StringVar(value=str(DECIMALES_POR_DEFECTO))

		self._grafico: LienzoDelGrafico | None = None
		self._tabla: TablaDeIteraciones | None = None
		self._matrices: VistaDeMatrices | None = None

		px = tema.px
		self.columnconfigure(1, weight=1)
		self.rowconfigure(1, weight=1)

		encabezado = ttk.Frame(self, padding=(px(28), px(20), px(28), px(16)))
		encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
		ttk.Label(encabezado, text=descriptor.nombre_para_mostrar, style="Titulo.TLabel").pack(anchor="w")
		ttk.Label(encabezado, text=descriptor.formula, style="Formula.TLabel").pack(anchor="w", pady=(px(2), 0))
		ttk.Label(
			encabezado, text=descriptor.descripcion, style="Suave.TLabel", wraplength=px(720), justify="left"
		).pack(anchor="w", pady=(px(8), 0))

		datos = self._armar_columna_desplazable()
		self._armar_columna_de_datos(datos)

		# El área de trabajo es una "hoja" blanca apoyada sobre el papel del fondo.
		hoja = tk.Frame(
			self, background=colores.SUPERFICIE, highlightthickness=1, highlightbackground=colores.LINEA
		)
		hoja.grid(row=1, column=1, sticky="nsew", padx=(0, px(20)), pady=(0, px(20)))
		self._armar_area_de_trabajo(hoja)

		self._mostrar_bloque_de_resultado()
		self.after_idle(self._actualizar_vista_previa)

	# --- Construcción ---------------------------------------------------------

	def _armar_columna_desplazable(self) -> ttk.Frame:
		"""La columna de datos, dentro de un `Canvas` que se desplaza si no entra en la ventana.

		Un sistema de 5×5 con su resultado y sus verificaciones puede ser más
		alto que una pantalla de notebook. La rueda del mouse desplaza la columna
		cuando el puntero está sobre ella, y al pasar de campo en campo con
		Tab la columna se mueve para que el campo enfocado quede a la vista.
		"""
		px = self._tema.px
		columna = ttk.Frame(self)
		columna.grid(row=1, column=0, sticky="nsw")
		columna.rowconfigure(0, weight=1)
		lienzo = tk.Canvas(columna, background=colores.PAPEL, highlightthickness=0, borderwidth=0)
		barra = ttk.Scrollbar(columna, orient="vertical", command=lienzo.yview)
		lienzo.configure(yscrollcommand=mostrar_barra_solo_si_hace_falta(barra))
		lienzo.grid(row=0, column=0, sticky="ns")
		barra.grid(row=0, column=1, sticky="ns", pady=(0, px(20)))

		datos = ttk.Frame(lienzo, padding=(px(28), 0, px(24), px(20)))
		lienzo.create_window(0, 0, window=datos, anchor="nw")

		def ajustar_al_contenido(evento: object = None) -> None:
			ancho, alto = datos.winfo_reqwidth(), datos.winfo_reqheight()
			lienzo.configure(width=ancho, scrollregion=(0, 0, ancho, alto))

		datos.bind("<Configure>", ajustar_al_contenido)
		self._lienzo_de_datos = lienzo
		self._columna_de_datos = columna
		self._datos = datos
		self.bind_all("<MouseWheel>", self._girar_rueda_sobre_los_datos, add="+")
		self.bind_all("<FocusIn>", self._mostrar_campo_enfocado, add="+")
		return datos

	def _contiene(self, contenedor: tk.Widget, widget: object) -> bool:
		return isinstance(widget, tk.Misc) and str(widget).startswith(str(contenedor))

	def _girar_rueda_sobre_los_datos(self, evento: tk.Event) -> None:
		debajo = self.winfo_containing(evento.x_root, evento.y_root)
		if self._contiene(self._columna_de_datos, debajo) and self._lienzo_de_datos.yview() != (0.0, 1.0):
			self._lienzo_de_datos.yview_scroll(-round(evento.delta / 120) * 3, "units")

	def _mostrar_campo_enfocado(self, evento: tk.Event) -> None:
		widget = evento.widget
		if not self._contiene(self._datos, widget) or self._lienzo_de_datos.yview() == (0.0, 1.0):
			return
		alto_total = max(1, self._datos.winfo_reqheight())
		arriba = (widget.winfo_rooty() - self._datos.winfo_rooty()) / alto_total
		abajo = arriba + widget.winfo_height() / alto_total
		primera, ultima = self._lienzo_de_datos.yview()
		if arriba < primera:
			self._lienzo_de_datos.yview_moveto(arriba)
		elif abajo > ultima:
			self._lienzo_de_datos.yview_moveto(abajo - (ultima - primera))

	def _armar_columna_de_datos(self, datos: ttk.Frame) -> None:
		px = self._tema.px
		campos = ttk.Frame(datos)
		campos.pack(fill="x")
		campos.columnconfigure(1, weight=1)

		campos_de_expresion: list[tuple[str, ttk.Entry]] = []
		for fila, campo in enumerate(self._descriptor.campos):
			separacion = (px(3), px(3))
			if campo.tipo is TipoDeCampo.CASILLA_DE_VERIFICACION:
				variable = tk.BooleanVar(value=campo.valor_por_defecto.strip().lower() in ("si", "sí", "true", "1"))
				ttk.Checkbutton(campos, text=campo.etiqueta, variable=variable).grid(
					row=fila, column=0, columnspan=2, sticky="w", pady=(px(10), px(2))
				)
				self._widgets[campo.nombre] = variable
				continue
			if campo.tipo is TipoDeCampo.SISTEMA_DE_ECUACIONES:
				grilla = GrillaDeSistema(campos, campo.valor_por_defecto, self._tema)
				grilla.grid(row=fila, column=0, columnspan=2, sticky="w", pady=separacion)
				self._widgets[campo.nombre] = grilla
				continue

			ttk.Label(campos, text=campo.etiqueta, style="Etiqueta.TLabel").grid(
				row=fila, column=0, sticky="w", padx=(0, px(10)), pady=separacion
			)
			if campo.tipo is TipoDeCampo.TEXTO_MULTILINEA:
				widget = tk.Text(
					campos, width=28, height=campo.cantidad_de_lineas, font=self._tema.numeros,
					relief="solid", borderwidth=1,
				)
				widget.insert("1.0", campo.valor_por_defecto)
				widget.grid(row=fila, column=1, sticky="we", pady=separacion)
				self._widgets[campo.nombre] = widget
				continue

			es_expresion = campo.tipo is TipoDeCampo.EXPRESION_MATEMATICA
			entrada = self._armar_entrada(campos, campo.nombre, campo.valor_por_defecto, 24 if es_expresion else 10)
			entrada.grid(row=fila, column=1, sticky="we" if es_expresion else "w", pady=separacion)
			self._widgets[campo.nombre] = entrada
			if es_expresion:
				campos_de_expresion.append((campo.etiqueta.rstrip(" ="), entrada))

		if campos_de_expresion:
			TecladoMatematico(datos, campos_de_expresion).pack(anchor="w", pady=(px(10), 0))

		if self._descriptor.usa_criterio_de_parada:
			criterio = ttk.Frame(datos)
			criterio.pack(fill="x", pady=(px(20), 0))
			ttk.Label(criterio, text="Criterio de parada", style="Seccion.TLabel").grid(
				row=0, column=0, columnspan=4, sticky="w", pady=(0, px(4))
			)
			ttk.Label(criterio, text="ε =", style="Etiqueta.TLabel").grid(row=1, column=0, sticky="w", padx=(0, px(10)))
			self._armar_entrada(criterio, "tolerancia", TOLERANCIA_POR_DEFECTO, 8).grid(row=1, column=1, sticky="w")
			ttk.Label(criterio, text="Máx. iteraciones").grid(row=1, column=2, sticky="w", padx=(px(18), px(8)))
			self._armar_entrada(criterio, "maximo_iteraciones", MAXIMO_DE_ITERACIONES_POR_DEFECTO, 6).grid(
				row=1, column=3, sticky="w"
			)

		ttk.Button(datos, text="Calcular", style="Primario.TButton", command=self._calcular).pack(
			fill="x", pady=(px(20), 0)
		)
		self._bloque_de_resultado = ttk.Frame(datos)
		self._bloque_de_resultado.pack(fill="x", pady=(px(18), 0))

	def _armar_entrada(self, contenedor: tk.Widget, nombre: str, valor_por_defecto: str, ancho: int) -> ttk.Entry:
		entrada = ttk.Entry(contenedor, width=ancho, style="Matematica.TEntry", font=self._tema.matematica)
		entrada.insert(0, valor_por_defecto)
		entrada.bind("<Return>", lambda evento: self._calcular())
		entrada.bind("<KeyRelease>", lambda evento: self._al_editar(nombre), add="+")
		entrada.bind("<<Editado>>", lambda evento: self._al_editar(nombre), add="+")
		entrada.bind("<Key>", lambda evento: self._quitar_marca_de_invalido(nombre), add="+")
		self._entradas[nombre] = entrada
		self._estilos_de_entrada[nombre] = "Matematica.TEntry"
		return entrada

	def _armar_area_de_trabajo(self, hoja: tk.Frame) -> None:
		px = self._tema.px
		descriptor = self._descriptor
		barra = tk.Frame(hoja, background=colores.SUPERFICIE)

		def armar_barra(titulo: str) -> None:
			ttk.Label(barra, text=titulo, style="Seccion.TLabel", background=colores.SUPERFICIE).pack(side="left")
			selector = ttk.Spinbox(
				barra, from_=1, to=DECIMALES_MAXIMOS, width=3, textvariable=self._variable_decimales,
				command=self._aplicar_decimales, font=self._tema.interfaz,
			)
			selector.pack(side="right")
			selector.bind("<Return>", lambda evento: self._aplicar_decimales())
			selector.bind("<FocusOut>", lambda evento: self._aplicar_decimales())
			ttk.Label(barra, text="Decimales", background=colores.SUPERFICIE).pack(side="right", padx=(0, px(8)))

		if descriptor.grafico is None and descriptor.columnas is None:
			armar_barra("Matrices")
			barra.pack(fill="x", padx=px(16), pady=(px(12), px(4)))
			self._matrices = VistaDeMatrices(hoja, self._tema, "Calculá para ver L, U, y, x y A⁻¹.")
			self._matrices.pack(fill="both", expand=True, padx=px(4), pady=(0, px(4)))
			return

		divisor = ttk.Panedwindow(hoja, orient="vertical")
		divisor.pack(fill="both", expand=True, padx=px(4), pady=px(4))
		if descriptor.grafico is not None:
			mensaje = (
				"Calculá para ver cómo baja el error de cada incógnita."
				if descriptor.grafico.campo_de_la_funcion is None
				else "Escribí la función para ver su curva."
			)
			self._grafico = LienzoDelGrafico(divisor, self._tema, descriptor.grafico, mensaje)
			divisor.add(self._grafico, weight=3)

		if descriptor.columnas is not None:
			contenedor_de_tabla = ttk.Frame(divisor, style="Superficie.TFrame")
			if self._grafico is not None:
				tk.Frame(contenedor_de_tabla, height=1, background=colores.LINEA).pack(fill="x", padx=px(12))
			barra = tk.Frame(contenedor_de_tabla, background=colores.SUPERFICIE)
			armar_barra("Iteraciones")
			barra.pack(fill="x", padx=px(12), pady=(px(8), px(6)))
			self._tabla = TablaDeIteraciones(contenedor_de_tabla, self._tema, "Las iteraciones aparecen acá al calcular.")
			self._tabla.pack(fill="both", expand=True, padx=px(8), pady=(0, px(4)))
			self._tabla.al_seleccionar = self._al_seleccionar_fila
			divisor.add(contenedor_de_tabla, weight=2)

	# --- Lectura de datos -------------------------------------------------------

	def _leer_valores(self) -> dict[str, object]:
		valores: dict[str, object] = {}
		for campo in self._descriptor.campos:
			widget = self._widgets[campo.nombre]
			nombre_visible = campo.etiqueta.rstrip(" =:")
			if campo.tipo is TipoDeCampo.EXPRESION_MATEMATICA:
				valores[campo.nombre] = self._leer_expresion(campo.nombre, nombre_visible, widget.get())
			elif campo.tipo is TipoDeCampo.NUMERO:
				valores[campo.nombre] = self._leer_numero_de_campo(campo.nombre, nombre_visible)
			elif campo.tipo is TipoDeCampo.TEXTO_MULTILINEA:
				valores[campo.nombre] = widget.get("1.0", "end")
			elif campo.tipo is TipoDeCampo.CASILLA_DE_VERIFICACION:
				valores[campo.nombre] = widget.get()
			elif campo.tipo is TipoDeCampo.SISTEMA_DE_ECUACIONES:
				try:
					valores[campo.nombre] = widget.obtener_sistema()
				except ValueError as error:
					raise EntradaInvalidaError(str(error)) from error
			else:
				raise AssertionError(f"Tipo de campo no soportado: {campo.tipo}")

		if self._descriptor.usa_criterio_de_parada:
			tolerancia = self._leer_numero_de_campo("tolerancia", "ε")
			if tolerancia <= 0:
				raise EntradaInvalidaError("ε tiene que ser mayor que 0.", "tolerancia")
			texto_maximo = self._entradas["maximo_iteraciones"].get().strip()
			if not texto_maximo.isdigit() or int(texto_maximo) < 1:
				raise EntradaInvalidaError(
					f"Máx. iteraciones: «{texto_maximo}» tiene que ser un número entero mayor que 0.",
					"maximo_iteraciones",
				)
			valores["tolerancia"] = tolerancia
			valores["maximo_iteraciones"] = int(texto_maximo)
		return valores

	def _leer_expresion(self, nombre: str, nombre_visible: str, texto: str) -> object:
		texto = texto.strip()
		if not texto:
			raise EntradaInvalidaError(f"{nombre_visible}: la expresión está vacía.", nombre)
		if "^" in texto:
			raise EntradaInvalidaError(
				f"{nombre_visible}: para las potencias se usa ** (x**2), no ^.", nombre
			)
		try:
			return compilar_funcion(texto)
		except NameError as error:
			desconocido = getattr(error, "name", None) or str(error)
			raise EntradaInvalidaError(
				f"{nombre_visible}: no se reconoce «{desconocido}». Se puede usar x, números, pi, e y "
				"funciones como exp, sin, cos, log o sqrt (o el teclado de abajo).",
				nombre,
			) from error
		except SyntaxError as error:
			raise EntradaInvalidaError(
				f"{nombre_visible}: «{texto}» está mal escrita. Revisá los paréntesis y que cada "
				"multiplicación lleve * (2*x, no 2x).",
				nombre,
			) from error

	def _leer_numero_de_campo(self, nombre: str, nombre_visible: str) -> float:
		try:
			return leer_numero(self._entradas[nombre].get())
		except ValueError as error:
			raise EntradaInvalidaError(f"{nombre_visible}: {error}.", nombre) from error

	def _textos_de_los_datos(self) -> dict[str, str]:
		return {nombre: entrada.get() for nombre, entrada in self._entradas.items()}

	# --- Cálculo ----------------------------------------------------------------

	def _calcular(self) -> None:
		for nombre in self._entradas:
			self._quitar_marca_de_invalido(nombre)
		try:
			valores = self._leer_valores()
		except EntradaInvalidaError as error:
			self._resultado = None
			self._mensaje_de_error = str(error)
			self._marcar_invalido(error.nombre_del_campo)
			self._mostrar_bloque_de_resultado()
			return

		self._subir_decimales_para(valores.get("tolerancia"))
		self._valores = valores
		self._datos_del_ultimo_calculo = self._textos_de_los_datos()
		self._iteraciones = []
		self._resultado = None
		self._mensaje_de_error = None
		tolerancia = valores.get("tolerancia")
		if self._tabla is not None:
			self._tabla.configurar(self._descriptor.columnas(valores), tolerancia)

		try:
			self._resultado = self._descriptor.ejecutar(valores, self.registrar_iteracion)
		except NoConvergeError as error:
			self._mensaje_de_error = (
				f"{error} Mirá la tabla y el gráfico para ver cómo evolucionó: podés subir el máximo "
				"de iteraciones o probar con otros valores iniciales."
			)
		except OverflowError:
			self._mensaje_de_error = (
				"Los valores crecieron sin control: el método diverge con estos datos. Mirá la tabla "
				"y el gráfico para ver cómo evolucionó."
			)
		except ZeroDivisionError:
			self._mensaje_de_error = "Hubo una división por cero al evaluar una de las funciones."
		except ValueError as error:
			if "math domain error" in str(error):
				self._mensaje_de_error = (
					"Una de las funciones no está definida en un punto que el método necesitó evaluar "
					"(por ejemplo, la raíz o el logaritmo de un número negativo)."
				)
			else:
				self._mensaje_de_error = str(error)
		except (ArithmeticError, TypeError) as error:
			self._mensaje_de_error = f"No se pudo evaluar la expresión: {error}"
		except Exception as error:
			self._mensaje_de_error = f"No se pudo calcular: {error}"

		exito = self._resultado is not None
		if self._tabla is not None:
			self._tabla.finalizar(resaltar_raiz=exito)
			if self._iteraciones:
				self._tabla.seleccionar(len(self._iteraciones) - 1)
		if self._grafico is not None:
			campo_de_la_funcion = self._descriptor.grafico.campo_de_la_funcion
			funcion = valores.get(campo_de_la_funcion) if campo_de_la_funcion else None
			self._grafico.mostrar_resultado(funcion, self._iteraciones, tolerancia, exito)
		if self._matrices is not None:
			self._matrices.mostrar(self._resultado.matrices if exito else ())
		self._mostrar_bloque_de_resultado()

	def registrar_iteracion(self, iteracion: Iteracion) -> None:
		"""Agrega una fila a la tabla mientras el método corre. Sirve como `reportar_iteracion`."""
		self._iteraciones.append(iteracion)
		if self._tabla is not None:
			self._tabla.agregar_fila(iteracion)
			cantidad = len(self._iteraciones)
			if cantidad < 40 or cantidad % 25 == 0:
				self.update_idletasks()

	# --- Decimales --------------------------------------------------------------

	def _decimales(self) -> int:
		try:
			return max(1, min(DECIMALES_MAXIMOS, int(self._variable_decimales.get())))
		except ValueError:
			return DECIMALES_POR_DEFECTO

	def _aplicar_decimales(self) -> None:
		decimales = self._decimales()
		self._variable_decimales.set(str(decimales))
		if self._tabla is not None:
			self._tabla.establecer_decimales(decimales)
		if self._matrices is not None:
			self._matrices.establecer_decimales(decimales)
		self._mostrar_bloque_de_resultado()

	def _subir_decimales_para(self, tolerancia: float | None) -> None:
		"""Con ε = 10⁻ⁿ hacen falta al menos n + 1 decimales para ver |E| < ε (4 para ε = 0,001)."""
		if not tolerancia:
			return
		necesarios = min(DECIMALES_MAXIMOS, max(1, math.ceil(-math.log10(tolerancia) - 1e-9) + 1))
		if necesarios > self._decimales():
			self._variable_decimales.set(str(necesarios))
			self._aplicar_decimales()

	# --- Resultado ----------------------------------------------------------------

	def _mostrar_bloque_de_resultado(self) -> None:
		bloque = self._bloque_de_resultado
		for widget in bloque.winfo_children():
			widget.destroy()
		px = self._tema.px
		decimales = self._decimales()
		ancho_de_texto = px(320)

		if self._resultado is not None:
			resultado = self._resultado
			ttk.Label(bloque, text=resultado.etiqueta_del_valor, style="Suave.TLabel").pack(anchor="w")
			banda = tk.Frame(bloque, background=colores.AMBAR, padx=px(14), pady=px(4))
			banda.pack(anchor="w", pady=(px(4), px(8)))
			if isinstance(resultado.valor, tuple):
				columnas = 2 if len(resultado.valor) > 4 else 1
				for indice, componente in enumerate(resultado.valor):
					tk.Label(
						banda, text=f"x{subindice(indice + 1)} = {formatear_numero(componente, decimales)}",
						font=self._tema.resultado_vectorial, background=colores.AMBAR, foreground=colores.TINTA,
					).grid(row=indice // columnas, column=indice % columnas, sticky="w", padx=(0, px(18) if columnas > 1 else 0))
			else:
				tk.Label(
					banda, text=formatear_numero(resultado.valor, decimales),
					font=self._tema.resultado, background=colores.AMBAR, foreground=colores.TINTA,
				).pack()

			if self._descriptor.usa_criterio_de_parada:
				ttk.Label(bloque, text=self._resumen_de_iteraciones(decimales), wraplength=ancho_de_texto, justify="left").pack(anchor="w")
			for verificacion in resultado.verificaciones:
				texto = f"{verificacion.etiqueta} = {formatear_numero_legible(verificacion.valor, decimales)}"
				if verificacion.esperado is not None:
					texto += f"   (esperado {formatear_numero_legible(verificacion.esperado, decimales)})"
				ttk.Label(bloque, text=texto, style="Suave.TLabel", font=self._tema.numeros).pack(anchor="w", pady=(px(2), 0))
			for advertencia in resultado.advertencias:
				self._armar_aviso(bloque, advertencia, colores.OCRE, ancho_de_texto)
		elif self._mensaje_de_error is None:
			ttk.Label(
				bloque, text="Presioná Calcular (o Enter en cualquier campo) para resolver.",
				style="Chica.TLabel", wraplength=ancho_de_texto, justify="left",
			).pack(anchor="w")

		if self._mensaje_de_error is not None:
			self._armar_aviso(bloque, self._mensaje_de_error, colores.ROJO, ancho_de_texto)
		if self._datos_cambiaron():
			ttk.Label(
				bloque, text="Cambiaste los datos: calculá de nuevo para actualizar el resultado.",
				style="Chica.TLabel", wraplength=ancho_de_texto, justify="left",
			).pack(anchor="w", pady=(px(10), 0))

	def _resumen_de_iteraciones(self, decimales: int) -> str:
		cantidad = self._resultado.cantidad_de_iteraciones
		texto = f"en {cantidad} {'iteración' if cantidad == 1 else 'iteraciones'}"
		ultimo_error = self._iteraciones[-1].error if self._iteraciones else None
		tolerancia = self._valores.get("tolerancia") if self._valores else None
		if ultimo_error is not None and tolerancia is not None:
			texto += (
				f", con |E| = {formatear_numero_legible(ultimo_error, decimales)} "
				f"< ε = {formatear_valor_corto(tolerancia)}"
			)
		return texto

	def _armar_aviso(self, contenedor: tk.Widget, texto: str, color: str, ancho: int) -> None:
		px = self._tema.px
		aviso = ttk.Frame(contenedor)
		aviso.pack(anchor="w", fill="x", pady=(px(10), 0))
		tk.Frame(aviso, width=px(3), background=color).pack(side="left", fill="y")
		ttk.Label(aviso, text=texto, foreground=color, wraplength=ancho, justify="left").pack(
			side="left", padx=(px(10), 0)
		)

	# --- Edición, vista previa y marcas -------------------------------------------------

	def _datos_cambiaron(self) -> bool:
		if self._datos_del_ultimo_calculo is None or (self._resultado is None and not self._iteraciones):
			return False
		return self._textos_de_los_datos() != self._datos_del_ultimo_calculo

	def _al_editar(self, nombre: str) -> None:
		if self._datos_del_ultimo_calculo is not None:
			self._mostrar_bloque_de_resultado()
		if nombre not in ("tolerancia", "maximo_iteraciones"):
			if self._datos_del_ultimo_calculo is None or self._textos_de_los_datos() != self._datos_del_ultimo_calculo:
				self._programar_vista_previa()

	def _programar_vista_previa(self) -> None:
		if self._grafico is None or not self._grafico.dibuja_una_curva:
			return
		if self._vista_previa_pendiente is not None:
			self.after_cancel(self._vista_previa_pendiente)
		self._vista_previa_pendiente = self.after(_ESPERA_DE_LA_VISTA_PREVIA_EN_MS, self._actualizar_vista_previa)

	def _actualizar_vista_previa(self) -> None:
		self._vista_previa_pendiente = None
		if self._grafico is None or not self._grafico.dibuja_una_curva:
			return
		texto = self._entradas[self._descriptor.grafico.campo_de_la_funcion].get()
		if "^" in texto:
			return
		try:
			funcion = compilar_funcion(texto)
		except (SyntaxError, NameError):
			return
		abscisas = []
		for campo in self._descriptor.campos:
			if campo.tipo is TipoDeCampo.NUMERO:
				try:
					abscisas.append(leer_numero(self._entradas[campo.nombre].get()))
				except ValueError:
					pass
		self._grafico.mostrar_vista_previa(funcion, abscisas)

	def _marcar_invalido(self, nombre: str | None) -> None:
		entrada = self._entradas.get(nombre) if nombre else None
		if entrada is None:
			return
		entrada.configure(style="InvalidoMatematica.TEntry")
		entrada.focus_set()
		entrada.select_range(0, "end")

	def _quitar_marca_de_invalido(self, nombre: str) -> None:
		entrada = self._entradas[nombre]
		if str(entrada.cget("style")) != self._estilos_de_entrada[nombre]:
			entrada.configure(style=self._estilos_de_entrada[nombre])

	def _al_seleccionar_fila(self, indice: int) -> None:
		if self._grafico is not None:
			self._grafico.resaltar_paso(indice)

	# --- API pública ----------------------------------------------------------------

	def limpiar_resultados(self) -> None:
		"""Borra la tabla, el gráfico del último cálculo, las matrices y el bloque de resultado."""
		self._iteraciones = []
		self._resultado = None
		self._mensaje_de_error = None
		self._datos_del_ultimo_calculo = None
		if self._tabla is not None:
			self._tabla.limpiar()
		if self._matrices is not None:
			self._matrices.mostrar(())
		self._mostrar_bloque_de_resultado()
		self._actualizar_vista_previa()

	def grillas_de_sistema(self) -> list[GrillaDeSistema]:
		"""Devuelve las grillas de sistema Ax = b de este panel (puede estar vacía).

		Usado por `vincular_grillas_de_sistema` para encontrar, entre
		todos los paneles, cuáles tienen un campo `SISTEMA_DE_ECUACIONES`
		que sincronizar.
		"""
		return [widget for widget in self._widgets.values() if isinstance(widget, GrillaDeSistema)]
