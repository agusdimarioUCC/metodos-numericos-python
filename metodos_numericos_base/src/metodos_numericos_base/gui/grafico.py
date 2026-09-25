"""El gráfico de cada método, dibujado como las figuras de los apuntes.

Un dibujante por `TipoDeGrafico`: bisección muestra los intervalos [a; b]
apilados debajo de la curva como en la fig. 8 ("iteración 1, 2, 3"); punto
fijo, la telaraña entre g(x) y y = x; Newton-Raphson, las tangentes;
secante, las secantes; Gauss-Seidel, cómo baja |Eⱼ| de cada incógnita. Se
dibuja sobre papel milimetrado, con f(x) en rojo, g(x) en verde, y = x en
azul y la raíz en ámbar, los mismos colores de los apuntes.

La curva se vuelve a muestrear sobre la vista actual cada vez que se
dibuja, así que acercar o alejar con la rueda (o arrastrar) siempre
muestra la función completa en el rango visible.
"""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from tkinter import ttk

import numpy as np
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from metodos_numericos_base.descriptor import GraficoDeMetodo, TipoDeGrafico
from metodos_numericos_base.formato import SIGNO_MENOS, subindice
from metodos_numericos_base.gui import tema as colores
from metodos_numericos_base.gui.tema import Tema
from metodos_numericos_base.iteracion import Iteracion

_PUNTOS_DE_LA_CURVA = 700
_FACTOR_DE_ZOOM = 1.25
_SUPERINDICES = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


@dataclass(frozen=True)
class _Vista:
	x_minimo: float
	x_maximo: float
	y_minimo: float
	y_maximo: float


def _evaluar_con_cuidado(funcion: Callable[[float], float], valor_x: float) -> float:
	"""Evalúa `funcion`, devolviendo NaN donde no está definida (log de un negativo, 1/0...)."""
	try:
		valor = float(funcion(valor_x))
	except (ValueError, ArithmeticError, TypeError):
		return math.nan
	return valor if math.isfinite(valor) else math.nan


def _formatear_marca(valor: float, posicion: int | None = None) -> str:
	"""Rótulo de un eje con coma decimal y signo menos tipográfico."""
	texto = f"{valor:.10g}"
	if "e" in texto:
		texto = f"{valor:.2g}"
	return texto.replace(".", ",").replace("-", SIGNO_MENOS)


def _formatear_potencia_de_diez(valor: float, posicion: int | None = None) -> str:
	if valor <= 0:
		return ""
	exponente = math.log10(valor)
	if abs(exponente - round(exponente)) > 1e-9:
		return ""
	return "10" + str(round(exponente)).translate(_SUPERINDICES)


class LienzoDelGrafico(ttk.Frame):
	"""Área de gráfico de un panel: vista previa de la curva, resultado y paso resaltado.

	Tres estados: vacío (un mensaje que guía), vista previa (solo la
	curva, mientras el usuario escribe los datos, para elegir el
	intervalo o el valor inicial "a ojo") y resultado (la curva más cada
	paso del método, con el paso elegido en la tabla resaltado).
	"""

	def __init__(self, contenedor: tk.Widget, tema: Tema, grafico: GraficoDeMetodo, mensaje_vacio: str) -> None:
		super().__init__(contenedor, style="Superficie.TFrame")
		self._tema = tema
		self._tipo = grafico.tipo
		self._mensaje_vacio = mensaje_vacio
		# Matplotlib no lee bien la Cambria regular de Windows (viene dentro de un .ttc y
		# dibuja solo algunos signos), pero sí la itálica, que es un .ttf aparte: los rótulos
		# matemáticos van en Cambria itálica y los números de los ejes en la letra de la
		# interfaz. DejaVu (incluida con matplotlib) cubre cualquier glifo que falte.
		self._familia_de_texto = [tema.familia_de_interfaz, "Segoe UI", "DejaVu Sans"]
		self._familia_matematica = [tema.familia_matematica, "DejaVu Serif"]

		self._funcion: Callable[[float], float] | None = None
		self._iteraciones: list[Iteracion] = []
		self._puntos_de_datos: list[tuple[float, float]] = []
		self._tolerancia: float | None = None
		self._exito = False
		self._resaltado: int | None = None
		self._abscisas_de_referencia: list[float] = []
		self._vista: _Vista | None = None
		self._vista_completa: _Vista | None = None
		self._arrastre: tuple[float, float, _Vista, float, float] | None = None
		self._redibujo_pendiente: str | None = None
		self._ejes_principales: Axes | None = None

		self._ayuda = ttk.Label(
			self,
			text="Rueda: acercar. Arrastrar: mover. Doble clic: ver todo.",
			style="Chica.TLabel",
			background=colores.SUPERFICIE,
		)
		self._figura = Figure(dpi=96, facecolor=colores.SUPERFICIE, layout="constrained")
		self._figura.get_layout_engine().set(w_pad=tema.px(8) / 96, h_pad=tema.px(8) / 96)
		self._lienzo = FigureCanvasTkAgg(self._figura, master=self)
		self._widget_del_lienzo = self._lienzo.get_tk_widget()
		self._widget_del_lienzo.configure(background=colores.SUPERFICIE, highlightthickness=0, borderwidth=0)
		self._widget_del_lienzo.pack(fill="both", expand=True)

		self._lienzo.mpl_connect("scroll_event", self._al_girar_rueda)
		self._lienzo.mpl_connect("button_press_event", self._al_presionar)
		self._lienzo.mpl_connect("motion_notify_event", self._al_mover)
		self._lienzo.mpl_connect("button_release_event", self._al_soltar)

		self._dibujar()

	# --- API pública -------------------------------------------------------

	@property
	def dibuja_una_curva(self) -> bool:
		return self._tipo not in (TipoDeGrafico.CONVERGENCIA, TipoDeGrafico.DISPERSION_Y_AJUSTE)

	def mostrar_vista_previa(self, funcion: Callable[[float], float], abscisas: Sequence[float]) -> None:
		"""Muestra solo la curva, alrededor de los valores numéricos que el usuario ya escribió."""
		self._funcion = funcion
		self._iteraciones = []
		self._puntos_de_datos = []
		self._resaltado = None
		self._exito = False
		self._abscisas_de_referencia = list(abscisas)
		self._reiniciar_vista()

	def mostrar_resultado(
			self,
			funcion: Callable[[float], float] | None,
			iteraciones: Sequence[Iteracion],
			tolerancia: float | None,
			exito: bool,
			puntos_de_datos: Sequence[tuple[float, float]] = (),
	) -> None:
		"""Dibuja la curva y todos los pasos del método, con el último resaltado."""
		self._funcion = funcion
		self._iteraciones = list(iteraciones)
		self._puntos_de_datos = list(puntos_de_datos)
		self._tolerancia = tolerancia
		self._exito = exito
		self._resaltado = len(self._iteraciones) - 1 if self._iteraciones else None
		self._abscisas_de_referencia = []
		self._reiniciar_vista()

	def resaltar_paso(self, indice: int | None) -> None:
		"""Resalta el paso de la fila `indice` de la tabla; acerca la vista si ese paso se ve muy chico."""
		self._resaltado = indice
		caja = self._caja_del_paso(indice)
		if caja is not None and self._vista is not None:
			ancho_de_la_vista = self._vista.x_maximo - self._vista.x_minimo
			ancho_del_paso = caja[1] - caja[0]
			if 0 < ancho_del_paso < 0.06 * ancho_de_la_vista:
				centro = (caja[0] + caja[1]) / 2
				self._vista = self._vista_para_rango_x(centro - 2.5 * ancho_del_paso, centro + 2.5 * ancho_del_paso)
		self._dibujar()

	def limpiar(self) -> None:
		"""Vuelve al estado vacío."""
		self._funcion = None
		self._iteraciones = []
		self._puntos_de_datos = []
		self._resaltado = None
		self._vista = self._vista_completa = None
		self._dibujar()

	# --- Vistas ------------------------------------------------------------

	def _reiniciar_vista(self) -> None:
		self._vista_completa = self._calcular_vista_completa()
		self._vista = self._vista_completa
		self._dibujar()

	def _abscisas_relevantes(self) -> list[float]:
		"""Los valores de x que la vista completa tiene que mostrar."""
		if not self._iteraciones:
			return self._abscisas_de_referencia

		valores: list[float] = []
		for iteracion in self._iteraciones:
			if self._tipo is TipoDeGrafico.INTERVALOS:
				valores.extend(
					float(iteracion.detalle[clave])
					for clave in ("extremo_inferior", "extremo_superior")
					if iteracion.detalle.get(clave) is not None
				)
			elif isinstance(iteracion.aproximacion, (int, float)):
				valores.append(float(iteracion.aproximacion))
				valor_g = iteracion.detalle.get("valor_g")
				if self._tipo is TipoDeGrafico.TELARANA and valor_g is not None:
					valores.append(float(valor_g))
		return _descartar_divergencia([valor for valor in valores if math.isfinite(valor)])

	def _calcular_vista_completa(self) -> _Vista | None:
		if self._tipo is TipoDeGrafico.CONVERGENCIA:
			return self._vista_de_convergencia()
		if self._tipo is TipoDeGrafico.DISPERSION_Y_AJUSTE:
			return self._vista_de_dispersion()
		if self._funcion is None:
			return None

		abscisas = self._abscisas_relevantes()
		if abscisas:
			minimo, maximo = min(abscisas), max(abscisas)
		else:
			minimo, maximo = -5.0, 5.0
		ancho = maximo - minimo
		if ancho < 1e-12:
			ancho = max(1.0, abs(minimo))
			minimo, maximo = minimo - ancho / 2, maximo + ancho / 2
		margen = 0.3 * ancho
		return self._vista_para_rango_x(minimo - margen, maximo + margen)

	def _vista_para_rango_x(self, x_minimo: float, x_maximo: float) -> _Vista:
		"""Una vista con ese rango de x y un rango de y que muestra bien la curva (y el eje x)."""
		if self._tipo is TipoDeGrafico.TELARANA:
			# Mismo rango en ambos ejes: y = x queda a 45° y la telaraña se lee bien.
			return _Vista(x_minimo, x_maximo, x_minimo, x_maximo)

		valores_y = [0.0]
		if self._funcion is not None:
			muestras = np.linspace(x_minimo, x_maximo, 200)
			finitos = [
				valor for valor in (_evaluar_con_cuidado(self._funcion, x) for x in muestras) if math.isfinite(valor)
			]
			if finitos:
				# Percentiles en vez de mínimo/máximo: una asíntota (tan, 1/x) no aplasta el resto.
				valores_y.extend(np.percentile(finitos, [2, 98]).tolist())
		if self._puntos_de_datos:
			valores_y.extend(y for _, y in self._puntos_de_datos)
		y_minimo, y_maximo = min(valores_y), max(valores_y)
		alto = y_maximo - y_minimo or 1.0
		return _Vista(x_minimo, x_maximo, y_minimo - 0.12 * alto, y_maximo + 0.12 * alto)

	def _vista_de_dispersion(self) -> _Vista | None:
		if not self._puntos_de_datos:
			return None
		valores_x = [x for x, _ in self._puntos_de_datos]
		minimo, maximo = min(valores_x), max(valores_x)
		ancho = maximo - minimo
		if ancho < 1e-12:
			ancho = max(1.0, abs(minimo))
			minimo, maximo = minimo - ancho / 2, maximo + ancho / 2
		margen = 0.15 * ancho
		return self._vista_para_rango_x(minimo - margen, maximo + margen)

	def _vista_de_convergencia(self) -> _Vista | None:
		errores = [
			float(valor)
			for iteracion in self._iteraciones
			for clave, valor in iteracion.detalle.items()
			if clave.startswith("error_") and valor is not None and valor > 0
		]
		if not errores:
			return None
		referencias = errores + ([self._tolerancia] if self._tolerancia else [])
		ultimo = max(iteracion.numero for iteracion in self._iteraciones)
		return _Vista(-0.3, max(1, ultimo) + 0.3, min(referencias) / 3, max(referencias) * 3)

	def _caja_del_paso(self, indice: int | None) -> tuple[float, float] | None:
		"""El rango de x que ocupa el paso `indice`, para acercar la vista si se ve muy chico."""
		if indice is None or not (0 <= indice < len(self._iteraciones)):
			return None
		iteracion = self._iteraciones[indice]
		if self._tipo is TipoDeGrafico.INTERVALOS:
			return float(iteracion.detalle["extremo_inferior"]), float(iteracion.detalle["extremo_superior"])
		if self._tipo is TipoDeGrafico.CONVERGENCIA or not isinstance(iteracion.aproximacion, (int, float)):
			return None
		puntos = [float(iteracion.aproximacion)]
		if self._tipo is TipoDeGrafico.TELARANA and iteracion.detalle.get("valor_g") is not None:
			puntos.append(float(iteracion.detalle["valor_g"]))
		if self._tipo is TipoDeGrafico.TANGENTES and indice + 1 < len(self._iteraciones):
			puntos.append(float(self._iteraciones[indice + 1].aproximacion))
		if self._tipo is TipoDeGrafico.SECANTES:
			puntos.extend(float(self._iteraciones[anterior].aproximacion) for anterior in range(max(0, indice - 2), indice))
		return min(puntos), max(puntos)

	# --- Dibujo -------------------------------------------------------------

	def _programar_redibujo(self) -> None:
		if self._redibujo_pendiente is None:
			self._redibujo_pendiente = self.after(15, self._dibujar)

	def _dibujar(self) -> None:
		self._redibujo_pendiente = None
		self._figura.clear()
		self._ejes_principales = None

		hay_contenido = self._vista is not None and (self._funcion is not None or self._iteraciones)
		if not hay_contenido:
			self._ayuda.pack_forget()
			self._dibujar_mensaje(self._mensaje_vacio)
			self._lienzo.draw_idle()
			return
		if not self._ayuda.winfo_ismapped():
			# Antes del lienzo en el orden de empaquetado, para que el lienzo (que se
			# expande) no lo deje sin lugar.
			self._ayuda.pack(
				side="bottom", anchor="e", padx=self._tema.px(12), pady=(0, self._tema.px(4)),
				before=self._widget_del_lienzo,
			)

		if self._tipo is TipoDeGrafico.INTERVALOS and self._iteraciones:
			grilla = self._figura.add_gridspec(2, 1, height_ratios=(3, 1.25))
			ejes = self._figura.add_subplot(grilla[0])
			ejes_de_intervalos = self._figura.add_subplot(grilla[1], sharex=ejes)
		else:
			ejes = self._figura.add_subplot()
			ejes_de_intervalos = None
		self._ejes_principales = ejes

		vista = self._vista
		escala_logaritmica = self._tipo is TipoDeGrafico.CONVERGENCIA
		self._estilizar(ejes, escala_logaritmica)
		ejes.set_xlim(vista.x_minimo, vista.x_maximo)
		ejes.set_ylim(vista.y_minimo, vista.y_maximo)

		if self._tipo is TipoDeGrafico.CONVERGENCIA:
			self._dibujar_convergencia(ejes)
		elif self._tipo is TipoDeGrafico.DISPERSION_Y_AJUSTE:
			self._dibujar_ejes_cartesianos(ejes)
			self._dibujar_curva(ejes)
			self._dibujar_dispersion(ejes)
		else:
			self._dibujar_ejes_cartesianos(ejes)
			if self._tipo is TipoDeGrafico.TELARANA:
				self._dibujar_identidad(ejes)
			self._dibujar_curva(ejes)
			dibujantes = {
				TipoDeGrafico.INTERVALOS: self._dibujar_intervalo_resaltado,
				TipoDeGrafico.TELARANA: self._dibujar_telarana,
				TipoDeGrafico.TANGENTES: self._dibujar_tangentes,
				TipoDeGrafico.SECANTES: self._dibujar_secantes,
			}
			if self._iteraciones:
				dibujantes[self._tipo](ejes)
				self._dibujar_raiz(ejes)

		if ejes_de_intervalos is not None:
			self._dibujar_intervalos_apilados(ejes_de_intervalos)
			ejes.tick_params(labelbottom=False)
		self._lienzo.draw_idle()

	def _dibujar_mensaje(self, mensaje: str) -> None:
		ejes = self._figura.add_subplot()
		ejes.set_axis_off()
		ejes.text(
			0.5, 0.5, mensaje,
			ha="center", va="center", wrap=True,
			color=colores.TINTA_SUAVE, fontsize=10, fontfamily=self._familia_de_texto,
			transform=ejes.transAxes,
		)

	def _estilizar(self, ejes: Axes, escala_logaritmica: bool = False) -> None:
		ejes.set_facecolor(colores.SUPERFICIE)
		for lado in ("top", "right"):
			ejes.spines[lado].set_visible(False)
		for lado in ("left", "bottom"):
			ejes.spines[lado].set_color(colores.LINEA_FUERTE)
		ejes.tick_params(colors=colores.TINTA_SUAVE, labelsize=9, length=3, labelfontfamily=self._familia_de_texto)
		ejes.set_axisbelow(True)
		ejes.xaxis.set_major_formatter(ticker.FuncFormatter(_formatear_marca))
		if escala_logaritmica:
			ejes.set_yscale("log")
			ejes.yaxis.set_major_locator(ticker.LogLocator(base=10))
			ejes.yaxis.set_major_formatter(ticker.FuncFormatter(_formatear_potencia_de_diez))
			ejes.yaxis.set_minor_formatter(ticker.NullFormatter())
			ejes.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
			ejes.grid(True, which="major", color=colores.CUADRICULA, linewidth=0.8)
		else:
			ejes.yaxis.set_major_formatter(ticker.FuncFormatter(_formatear_marca))
			ejes.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
			ejes.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
			ejes.grid(True, which="major", color=colores.CUADRICULA, linewidth=0.8)
			ejes.grid(True, which="minor", color=colores.CUADRICULA_MENOR, linewidth=0.5)

	def _texto_matematico(self, ejes: Axes, x: float, y: float, texto: str, **opciones: object) -> None:
		opciones.setdefault("fontsize", 11)
		opciones.setdefault("color", colores.TINTA)
		opciones.setdefault("clip_on", True)
		rotulo = ejes.text(x, y, texto, fontfamily=self._familia_matematica, style="italic", **opciones)
		# Fuera del cálculo del layout: un rótulo que cae fuera de la vista no debe achicar los ejes.
		rotulo.set_in_layout(False)

	def _recortar(self, anotacion: object, ejes: Axes) -> None:
		"""Las flechas de `annotate` no se recortan solas: sin esto se salen del gráfico al acercar."""
		anotacion.arrow_patch.set_clip_path(ejes.patch)

	def _rotular_abscisas(self, ejes: Axes, rotulos: Sequence[tuple[float, str, bool]]) -> None:
		"""Rotula x₀, x₁, ... bajo el eje, salteando los que quedarían encimados con uno anterior."""
		vista = self._vista
		separacion_minima = 0.05 * (vista.x_maximo - vista.x_minimo)
		# Sobre el eje x si se ve; si no (la telaraña suele estar lejos del 0), al pie del gráfico.
		altura = 0.0 if vista.y_minimo <= 0 <= vista.y_maximo else vista.y_minimo
		alineacion_vertical = "top" if altura == 0.0 else "bottom"
		ubicados: list[float] = []
		for x, texto, resaltado in sorted(rotulos, key=lambda rotulo: not rotulo[2]):
			if not (vista.x_minimo <= x <= vista.x_maximo):
				continue
			if not resaltado and any(abs(x - otro) < separacion_minima for otro in ubicados):
				continue
			ubicados.append(x)
			self._texto_matematico(
				ejes, x, altura, texto, ha="center", va=alineacion_vertical, fontsize=10,
				color=colores.TINTA if resaltado else colores.TINTA_SUAVE,
			)

	def _dibujar_ejes_cartesianos(self, ejes: Axes) -> None:
		ejes.axhline(0, color=colores.TINTA, linewidth=1.0, zorder=1.5)
		ejes.axvline(0, color=colores.TINTA, linewidth=1.0, zorder=1.5)
		vista = self._vista
		self._texto_matematico(
			ejes, vista.x_maximo, 0, "x ", ha="right", va="bottom", color=colores.TINTA_SUAVE, clip_on=True
		)

	def _dibujar_curva(self, ejes: Axes) -> None:
		if self._funcion is None:
			return
		vista = self._vista
		xs = np.linspace(vista.x_minimo, vista.x_maximo, _PUNTOS_DE_LA_CURVA)
		ys = np.array([_evaluar_con_cuidado(self._funcion, x) for x in xs])
		# Corta la línea en las asíntotas: un salto más grande que la vista entera entre dos
		# muestras consecutivas no es la curva, es un polo (tan x, 1/x).
		alto = vista.y_maximo - vista.y_minimo
		saltos = np.abs(np.diff(ys)) > 2 * alto
		ys[1:][saltos] = np.nan
		es_g = self._tipo is TipoDeGrafico.TELARANA
		color = colores.VERDE if es_g else colores.ROJO
		ejes.plot(xs, ys, color=color, linewidth=2.2, zorder=3, solid_capstyle="round")

		x_del_rotulo = vista.x_minimo + 0.96 * (vista.x_maximo - vista.x_minimo)
		y_del_rotulo = _evaluar_con_cuidado(self._funcion, x_del_rotulo)
		if math.isfinite(y_del_rotulo) and vista.y_minimo < y_del_rotulo < vista.y_maximo:
			self._texto_matematico(
				ejes, x_del_rotulo, y_del_rotulo, "g(x)" if es_g else "f(x)",
				color=color, ha="right", va="bottom", fontsize=12,
			)

	def _dibujar_identidad(self, ejes: Axes) -> None:
		vista = self._vista
		extremos = (min(vista.x_minimo, vista.y_minimo), max(vista.x_maximo, vista.y_maximo))
		ejes.plot(extremos, extremos, color=colores.AZUL, linewidth=1.6, zorder=2.5)
		x_del_rotulo = vista.x_minimo + 0.96 * (vista.x_maximo - vista.x_minimo)
		self._texto_matematico(ejes, x_del_rotulo, x_del_rotulo, "y = x  ", color=colores.AZUL, ha="right", va="top")

	def _dibujar_raiz(self, ejes: Axes) -> None:
		if not self._exito or not self._iteraciones:
			return
		ultima = self._iteraciones[-1]
		raiz = float(ultima.aproximacion)
		y = raiz if self._tipo is TipoDeGrafico.TELARANA else 0.0
		ejes.plot(
			[raiz], [y], marker="o", markersize=9, color=colores.AMBAR,
			markeredgecolor=colores.TINTA, markeredgewidth=1.2, zorder=6, linestyle="none",
		)

	def _dibujar_dispersion(self, ejes: Axes) -> None:
		"""Los puntos (xᵢ, yᵢ) originales, con el elegido en la tabla resaltado en ámbar."""
		if not self._puntos_de_datos:
			return
		xs = [x for x, _ in self._puntos_de_datos]
		ys = [y for _, y in self._puntos_de_datos]
		ejes.scatter(xs, ys, color=colores.AZUL, s=36, zorder=5, edgecolor=colores.SUPERFICIE, linewidth=0.8)
		if self._resaltado is not None and 0 <= self._resaltado < len(self._puntos_de_datos):
			x, y = self._puntos_de_datos[self._resaltado]
			ejes.scatter(
				[x], [y], color=colores.AMBAR, s=70, zorder=6, edgecolor=colores.TINTA, linewidth=1.2
			)

	# Bisección ---------------------------------------------------------------

	def _dibujar_intervalo_resaltado(self, ejes: Axes) -> None:
		indice = self._resaltado if self._resaltado is not None else len(self._iteraciones) - 1
		iteracion = self._iteraciones[indice]
		extremo_inferior = float(iteracion.detalle["extremo_inferior"])
		extremo_superior = float(iteracion.detalle["extremo_superior"])
		punto_medio = float(iteracion.aproximacion)

		ejes.axvspan(extremo_inferior, extremo_superior, color=colores.AZUL_TENUE, zorder=0.5, linewidth=0)
		for extremo in (extremo_inferior, extremo_superior):
			valor = _evaluar_con_cuidado(self._funcion, extremo)
			if math.isfinite(valor):
				ejes.plot([extremo, extremo], [0, valor], color=colores.TINTA_SUAVE, linestyle=(0, (4, 3)), linewidth=1, zorder=2)
		valor_medio = _evaluar_con_cuidado(self._funcion, punto_medio)
		if math.isfinite(valor_medio):
			ejes.plot([punto_medio, punto_medio], [0, valor_medio], color=colores.AZUL, linestyle=(0, (4, 3)), linewidth=1.2, zorder=2)
			ejes.plot([punto_medio], [valor_medio], marker="o", markersize=5, color=colores.AZUL, zorder=5)
		self._rotular_abscisas(
			ejes, [(punto_medio, "c", True), (extremo_inferior, "a", False), (extremo_superior, "b", False)]
		)

	def _dibujar_intervalos_apilados(self, ejes: Axes) -> None:
		"""Una flecha ↔ por iteración, de a hasta b, apiladas hacia abajo como en la fig. 8."""
		ejes.set_facecolor(colores.SUPERFICIE)
		for lado in ("top", "right", "left"):
			ejes.spines[lado].set_visible(False)
		ejes.spines["bottom"].set_color(colores.LINEA_FUERTE)
		ejes.tick_params(axis="x", colors=colores.TINTA_SUAVE, labelsize=9, length=3, labelfontfamily=self._familia_de_texto)
		ejes.tick_params(axis="y", left=False, labelleft=False)
		ejes.xaxis.set_major_formatter(ticker.FuncFormatter(_formatear_marca))
		ejes.grid(True, axis="x", which="major", color=colores.CUADRICULA, linewidth=0.8)
		ejes.set_axisbelow(True)

		cantidad = len(self._iteraciones)
		ejes.set_ylim(-cantidad - 0.7, -0.3)
		# Solo se numeran las flechas que todavía se ven anchas (y la elegida): las demás
		# se amontonan en un punto hasta que se acerca la vista.
		ancho_minimo_para_numerar = 0.04 * (self._vista.x_maximo - self._vista.x_minimo)
		for indice, iteracion in enumerate(self._iteraciones):
			altura = -(indice + 1)
			resaltado = indice == self._resaltado
			color = colores.AZUL if resaltado else colores.LINEA_FUERTE
			extremo_inferior = float(iteracion.detalle["extremo_inferior"])
			extremo_superior = float(iteracion.detalle["extremo_superior"])
			flecha = ejes.annotate(
				"", xy=(extremo_superior, altura), xytext=(extremo_inferior, altura),
				arrowprops={
					"arrowstyle": "<|-|>", "color": color, "linewidth": 1.8 if resaltado else 1.1,
					"shrinkA": 0, "shrinkB": 0, "mutation_scale": 8,
				},
				annotation_clip=False,
			)
			self._recortar(flecha, ejes)
			ejes.plot([float(iteracion.aproximacion)], [altura], marker="|", markersize=7, color=color)
			if resaltado or extremo_superior - extremo_inferior >= ancho_minimo_para_numerar:
				ejes.annotate(
					f"{iteracion.numero}", xy=(extremo_superior, altura), xytext=(6, 0), textcoords="offset points",
					va="center", fontsize=8, color=colores.TINTA if resaltado else colores.TINTA_SUAVE,
					fontfamily=self._familia_de_texto, annotation_clip=True,
				)
		ejes.set_ylabel("iteración", fontsize=8, color=colores.TINTA_SUAVE, fontfamily=self._familia_de_texto)

	# Punto fijo --------------------------------------------------------------

	def _dibujar_telarana(self, ejes: Axes) -> None:
		"""Desde (x₀, x₀) sobre y = x: vertical hasta g(x₀), horizontal hasta y = x, y así, con flechas rojas."""
		limite = self._resaltado if self._resaltado is not None else len(self._iteraciones) - 1
		rotulos = []
		for indice, iteracion in enumerate(self._iteraciones):
			x = float(iteracion.aproximacion)
			rotulos.append((x, f"x{subindice(iteracion.numero)}", indice == limite))
			valor_g = iteracion.detalle.get("valor_g")
			if valor_g is None:
				continue
			valor_g = float(valor_g)
			opacidad = 1.0 if indice <= limite else 0.22
			ancho = 1.7 if indice == limite else 1.1
			for desde, hasta in (((x, x), (x, valor_g)), ((x, valor_g), (valor_g, valor_g))):
				flecha = ejes.annotate(
					"", xy=hasta, xytext=desde,
					arrowprops={
						"arrowstyle": "-|>", "color": colores.ROJO, "linewidth": ancho, "alpha": opacidad,
						"shrinkA": 0, "shrinkB": 0, "mutation_scale": 9,
					},
					annotation_clip=False, zorder=4,
				)
				self._recortar(flecha, ejes)
		actual = float(self._iteraciones[limite].aproximacion)
		ejes.plot(
			[actual, actual], [self._vista.y_minimo, actual],
			color=colores.TINTA_SUAVE, linestyle=(0, (4, 3)), linewidth=1, zorder=2,
		)
		self._rotular_abscisas(ejes, rotulos)

	# Newton-Raphson -------------------------------------------------------------

	def _dibujar_tangentes(self, ejes: Axes) -> None:
		rotulos = []
		for indice, iteracion in enumerate(self._iteraciones):
			x = float(iteracion.aproximacion)
			valor_funcion = iteracion.detalle.get("valor_funcion")
			valor_derivada = iteracion.detalle.get("valor_derivada")
			resaltado = indice == self._resaltado
			rotulos.append((x, f"X{subindice(iteracion.numero)}", resaltado))
			if valor_funcion is None or valor_derivada is None or indice + 1 >= len(self._iteraciones):
				continue
			siguiente = float(self._iteraciones[indice + 1].aproximacion)
			extension = 0.15 * abs(siguiente - x)
			direccion = 1 if siguiente > x else -1
			xs = np.array([x + direccion * extension, siguiente - direccion * extension])
			ys = float(valor_funcion) + float(valor_derivada) * (xs - x)
			ejes.plot(
				xs, ys, color=colores.TINTA if resaltado else colores.LINEA_FUERTE,
				linewidth=1.6 if resaltado else 1.0, zorder=3.5,
			)
			ejes.plot([x, x], [0, float(valor_funcion)], color=colores.TINTA_SUAVE, linestyle=(0, (4, 3)), linewidth=1, zorder=2)
			ejes.plot(
				[x], [float(valor_funcion)], marker="o", markersize=5 if resaltado else 3.5,
				color=colores.TINTA if resaltado else colores.TINTA_SUAVE, zorder=5,
			)
		self._rotular_abscisas(ejes, rotulos)

	# Secante -------------------------------------------------------------------

	def _dibujar_secantes(self, ejes: Axes) -> None:
		puntos = [
			(float(iteracion.aproximacion), iteracion.detalle.get("valor_funcion")) for iteracion in self._iteraciones
		]
		for indice in range(2, len(puntos)):
			(x_anterior, f_anterior), (x_actual, f_actual) = puntos[indice - 2], puntos[indice - 1]
			if f_anterior is None or f_actual is None or x_anterior == x_actual:
				continue
			x_nuevo = puntos[indice][0]
			resaltado = indice == self._resaltado
			pendiente = (f_actual - f_anterior) / (x_actual - x_anterior)
			extremos = [min(x_anterior, x_actual, x_nuevo), max(x_anterior, x_actual, x_nuevo)]
			margen = 0.08 * (extremos[1] - extremos[0])
			xs = np.array([extremos[0] - margen, extremos[1] + margen])
			ejes.plot(
				xs, f_actual + pendiente * (xs - x_actual),
				color=colores.TINTA if resaltado else colores.LINEA_FUERTE,
				linewidth=1.6 if resaltado else 1.0, zorder=3.5,
			)
		rotulos = []
		for indice, (x, valor_funcion) in enumerate(puntos):
			resaltado = indice == self._resaltado
			rotulos.append((x, f"X{subindice(self._iteraciones[indice].numero)}", resaltado))
			if valor_funcion is not None:
				ejes.plot([x, x], [0, valor_funcion], color=colores.TINTA_SUAVE, linestyle=(0, (4, 3)), linewidth=1, zorder=2)
				ejes.plot(
					[x], [valor_funcion], marker="o", markersize=5 if resaltado else 3.5,
					color=colores.TINTA if resaltado else colores.TINTA_SUAVE, zorder=5,
				)
		self._rotular_abscisas(ejes, rotulos)

	# Gauss-Seidel ----------------------------------------------------------------

	def _dibujar_convergencia(self, ejes: Axes) -> None:
		cantidad_de_componentes = sum(1 for clave in self._iteraciones[0].detalle if clave.startswith("error_"))
		if self._tolerancia:
			ejes.axhline(self._tolerancia, color=colores.TINTA_SUAVE, linestyle=(0, (5, 4)), linewidth=1.1, zorder=2)
			self._texto_matematico(
				ejes, self._vista.x_maximo, self._tolerancia, "ε ", ha="right", va="bottom", color=colores.TINTA_SUAVE
			)
		if self._resaltado is not None:
			numero = self._iteraciones[self._resaltado].numero
			ejes.axvspan(numero - 0.18, numero + 0.18, color=colores.AZUL_TENUE, zorder=0.5, linewidth=0)

		for componente in range(1, cantidad_de_componentes + 1):
			color = colores.COLORES_DE_COMPONENTES[(componente - 1) % len(colores.COLORES_DE_COMPONENTES)]
			puntos = [
				(iteracion.numero, float(iteracion.detalle[f"error_{componente}"]))
				for iteracion in self._iteraciones
				if iteracion.detalle.get(f"error_{componente}") is not None and iteracion.detalle[f"error_{componente}"] > 0
			]
			if not puntos:
				continue
			numeros, errores = zip(*puntos)
			ejes.plot(numeros, errores, color=color, linewidth=1.6, marker="o", markersize=4, zorder=3,
				label=f"|E{subindice(componente)}|")
			if self._tolerancia:
				bajo_tolerancia = next(((numero, error) for numero, error in puntos if error < self._tolerancia), None)
				if bajo_tolerancia is not None:
					ejes.plot([bajo_tolerancia[0]], [bajo_tolerancia[1]], marker="o", markersize=9,
						markerfacecolor=colores.VERDE_CELDA, markeredgecolor=color, markeredgewidth=1.4, zorder=4)
		propiedades = {"family": self._familia_matematica, "style": "italic", "size": 11}
		if cantidad_de_componentes <= 4:
			leyenda = ejes.legend(loc="upper right", frameon=False, ncol=cantidad_de_componentes, prop=propiedades)
		else:
			# Con muchas incógnitas la leyenda taparía las curvas: va afuera, a la derecha.
			leyenda = ejes.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, prop=propiedades)
		for texto in leyenda.get_texts():
			texto.set_color(colores.TINTA)
		ejes.set_xlabel("iteración", fontsize=9, color=colores.TINTA_SUAVE, fontfamily=self._familia_de_texto)

	# --- Zoom y desplazamiento ------------------------------------------------------

	def _al_girar_rueda(self, evento: MouseEvent) -> None:
		if self._vista is None or evento.inaxes is None or evento.xdata is None:
			return
		factor = 1 / _FACTOR_DE_ZOOM if evento.button == "up" else _FACTOR_DE_ZOOM
		vista = self._vista
		solo_x = evento.inaxes is not self._ejes_principales
		x_minimo, x_maximo = _escalar(vista.x_minimo, vista.x_maximo, evento.xdata, factor)
		if solo_x:
			y_minimo, y_maximo = vista.y_minimo, vista.y_maximo
		elif self._tipo is TipoDeGrafico.CONVERGENCIA:
			y_minimo, y_maximo = _escalar_logaritmico(vista.y_minimo, vista.y_maximo, evento.ydata, factor)
		else:
			y_minimo, y_maximo = _escalar(vista.y_minimo, vista.y_maximo, evento.ydata, factor)
		self._vista = _Vista(x_minimo, x_maximo, y_minimo, y_maximo)
		self._dibujar()

	def _al_presionar(self, evento: MouseEvent) -> None:
		if self._vista is None or evento.inaxes is None:
			return
		if evento.dblclick:
			self._vista = self._vista_completa
			self._dibujar()
			return
		if evento.button == 1:
			caja = evento.inaxes.bbox
			self._arrastre = (evento.x, evento.y, self._vista, caja.width, caja.height)
			self._lienzo.get_tk_widget().configure(cursor="fleur")

	def _al_mover(self, evento: MouseEvent) -> None:
		if self._arrastre is None:
			return
		x_inicial, y_inicial, vista, ancho, alto = self._arrastre
		desplazamiento_x = (evento.x - x_inicial) / ancho * (vista.x_maximo - vista.x_minimo)
		if self._tipo is TipoDeGrafico.CONVERGENCIA:
			logaritmos = (math.log10(vista.y_minimo), math.log10(vista.y_maximo))
			desplazamiento = (evento.y - y_inicial) / alto * (logaritmos[1] - logaritmos[0])
			y_minimo, y_maximo = 10 ** (logaritmos[0] - desplazamiento), 10 ** (logaritmos[1] - desplazamiento)
		else:
			desplazamiento_y = (evento.y - y_inicial) / alto * (vista.y_maximo - vista.y_minimo)
			y_minimo, y_maximo = vista.y_minimo - desplazamiento_y, vista.y_maximo - desplazamiento_y
		self._vista = _Vista(vista.x_minimo - desplazamiento_x, vista.x_maximo - desplazamiento_x, y_minimo, y_maximo)
		self._programar_redibujo()

	def _al_soltar(self, evento: MouseEvent) -> None:
		if self._arrastre is not None:
			self._arrastre = None
			self._lienzo.get_tk_widget().configure(cursor="")


def _escalar(minimo: float, maximo: float, centro: float, factor: float) -> tuple[float, float]:
	return centro - (centro - minimo) * factor, centro + (maximo - centro) * factor


def _escalar_logaritmico(minimo: float, maximo: float, centro: float, factor: float) -> tuple[float, float]:
	logaritmos = _escalar(math.log10(minimo), math.log10(maximo), math.log10(centro), factor)
	return 10 ** logaritmos[0], 10 ** logaritmos[1]


def _descartar_divergencia(valores: list[float]) -> list[float]:
	"""Deja afuera los valores de una sucesión que se dispara, para que la vista muestre los primeros pasos.

	Los tres primeros valores siempre entran; de ahí en más, solo los que
	quedan a menos de 10 veces la dispersión inicial del primero. En una
	sucesión que converge no se descarta nada.
	"""
	if len(valores) <= 3:
		return valores
	primeros = valores[:3]
	dispersion = max(max(primeros) - min(primeros), 1e-9)
	return primeros + [valor for valor in valores[3:] if abs(valor - primeros[0]) <= 10 * dispersion]
