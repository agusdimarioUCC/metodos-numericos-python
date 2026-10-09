"""Identidad visual de la GUI: "apunte de cátedra".

Los colores salen del código de colores de los apuntes del taller: f(x) en
rojo, g(x) en verde, la recta y = x en azul, la celda de la raíz resaltada
en ámbar y los errores por debajo de ε en verde claro. Todo lo demás es
tinta azul-negra sobre papel. El ámbar se reserva para una sola cosa, la
respuesta (celda de la raíz, banda del resultado, punto en el gráfico),
para que siempre se lea igual.

Tipografía: Bahnschrift (DIN, la letra de los planos técnicos) para la
interfaz, y Cambria para todo lo matemático — números, fórmulas y
expresiones —, que es la familia con la que los apuntes tipografían sus
ecuaciones y, a diferencia de Bahnschrift, tiene dígitos de ancho fijo
para que las columnas de la tabla queden alineadas. No se usa Cambria
Math: reserva ~5 veces más interlineado (para integrales y radicales
apilados) y infla cualquier campo o etiqueta donde se la ponga.
"""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import ttk

PAPEL = "#F6F7F4"
LATERAL = "#ECEEEA"
LATERAL_RESALTADO = "#E2E5E0"
SUPERFICIE = "#FFFFFF"
TINTA = "#1B2330"
TINTA_SUAVE = "#5B6472"
TINTA_TENUE = "#9AA1AA"
LINEA = "#D5D9DE"
LINEA_FUERTE = "#AEB5BD"
AZUL = "#1F5FAD"
AZUL_OSCURO = "#174A88"
AZUL_TENUE = "#E3ECF8"
ROJO = "#C62828"
VERDE = "#2E8B3E"
VERDE_CELDA = "#92D050"
AMBAR = "#FFC000"
OCRE = "#7A4E00"
CUADRICULA = "#DCE4EE"
CUADRICULA_MENOR = "#EEF2F7"

COLORES_DE_COMPONENTES = (
	AZUL,
	ROJO,
	VERDE,
	"#B26B00",
	"#6A3FA0",
	"#0F7C8C",
	"#8C4A2F",
	TINTA_SUAVE,
)
"""Un color por incógnita en los gráficos de convergencia (sobran para el tope de la grilla de sistemas)."""

_FAMILIAS_DE_INTERFAZ = ("Bahnschrift", "Segoe UI")
_FAMILIAS_DE_INTERFAZ_DESTACADA = ("Bahnschrift SemiBold", "Segoe UI Semibold")
_FAMILIAS_MATEMATICAS = ("Cambria", "STIX Two Text", "Georgia", "DejaVu Serif")


def activar_nitidez_en_pantallas_escaladas() -> None:
	"""Le avisa a Windows que la app maneja su propio escalado, para que no la dibuje borrosa.

	Sin esto, con el escalado de pantalla en 125 % o 150 % (lo habitual
	en notebooks) Windows dibuja la ventana a 96 dpi y la estira como una
	imagen. Tiene que llamarse antes de crear la ventana de Tk. En otros
	sistemas no hace nada.
	"""
	if sys.platform != "win32":
		return
	try:
		ctypes.windll.shcore.SetProcessDpiAwareness(1)
	except (AttributeError, OSError):
		try:
			ctypes.windll.user32.SetProcessDPIAware()
		except (AttributeError, OSError):
			pass


def _primera_familia_disponible(preferidas: tuple[str, ...]) -> str:
	disponibles = set(tkfont.families())
	for familia in preferidas:
		if familia in disponibles:
			return familia
	return tkfont.nametofont("TkDefaultFont").actual("family")


@dataclass(frozen=True)
class Tema:
	"""Fuentes y escala de una ventana ya creada (las fuentes de Tk necesitan un root vivo)."""

	escala: float
	interfaz: tkfont.Font
	interfaz_chica: tkfont.Font
	interfaz_destacada: tkfont.Font
	marca: tkfont.Font
	titulo: tkfont.Font
	matematica: tkfont.Font
	formula: tkfont.Font
	numeros: tkfont.Font
	numeros_destacados: tkfont.Font
	resultado: tkfont.Font
	resultado_vectorial: tkfont.Font
	familia_matematica: str
	familia_de_interfaz: str

	def px(self, pixeles: float) -> int:
		"""Convierte una medida pensada para 96 dpi a los píxeles reales de esta pantalla."""
		return round(pixeles * self.escala)


def crear_tema(raiz: tk.Tk) -> Tema:
	"""Crea las fuentes, configura los estilos ttk y devuelve el `Tema` de la ventana."""
	familia_de_interfaz = _primera_familia_disponible(_FAMILIAS_DE_INTERFAZ)
	familia_destacada = _primera_familia_disponible(_FAMILIAS_DE_INTERFAZ_DESTACADA)
	familia_matematica = _primera_familia_disponible(_FAMILIAS_MATEMATICAS)

	tema = Tema(
		escala=raiz.winfo_fpixels("1i") / 96,
		interfaz=tkfont.Font(raiz, family=familia_de_interfaz, size=10),
		interfaz_chica=tkfont.Font(raiz, family=familia_de_interfaz, size=9),
		interfaz_destacada=tkfont.Font(raiz, family=familia_destacada, size=10),
		marca=tkfont.Font(raiz, family=familia_destacada, size=12),
		titulo=tkfont.Font(raiz, family=familia_destacada, size=18),
		matematica=tkfont.Font(raiz, family=familia_matematica, size=12),
		formula=tkfont.Font(raiz, family=familia_matematica, size=13, slant="italic"),
		numeros=tkfont.Font(raiz, family=familia_matematica, size=11),
		numeros_destacados=tkfont.Font(raiz, family=familia_matematica, size=11, weight="bold"),
		resultado=tkfont.Font(raiz, family=familia_matematica, size=26),
		resultado_vectorial=tkfont.Font(raiz, family=familia_matematica, size=15),
		familia_matematica=familia_matematica,
		familia_de_interfaz=familia_de_interfaz,
	)
	for nombre in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
		tkfont.nametofont(nombre).configure(family=familia_de_interfaz, size=10)
	raiz.configure(background=PAPEL)
	_configurar_estilos(ttk.Style(raiz), tema)
	# La lista desplegable de un Combobox es un Listbox clásico de Tk, no un
	# widget ttk: los estilos ttk no la alcanzan, hay que pintarla vía la
	# option database.
	raiz.option_add("*TCombobox*Listbox.font", tema.matematica)
	raiz.option_add("*TCombobox*Listbox.background", SUPERFICIE)
	raiz.option_add("*TCombobox*Listbox.foreground", TINTA)
	raiz.option_add("*TCombobox*Listbox.selectBackground", AZUL_TENUE)
	raiz.option_add("*TCombobox*Listbox.selectForeground", TINTA)
	return tema


def _configurar_estilos(estilo: ttk.Style, tema: Tema) -> None:
	# "clam" es el único tema incluido en Tk que respeta colores y bordes
	# propios; el nativo de Windows ("vista") ignora casi todo.
	estilo.theme_use("clam")
	px = tema.px

	estilo.configure(
		".",
		background=PAPEL,
		foreground=TINTA,
		font=tema.interfaz,
		bordercolor=LINEA_FUERTE,
		lightcolor=PAPEL,
		darkcolor=PAPEL,
		troughcolor=PAPEL,
		focuscolor=AZUL,
		selectbackground=AZUL_TENUE,
		selectforeground=TINTA,
		fieldbackground=SUPERFICIE,
		insertcolor=TINTA,
	)
	estilo.configure("TFrame", background=PAPEL)
	estilo.configure("Superficie.TFrame", background=SUPERFICIE)
	estilo.configure("Lateral.TFrame", background=LATERAL)

	estilo.configure("TLabel", background=PAPEL, foreground=TINTA)
	estilo.configure("Suave.TLabel", foreground=TINTA_SUAVE)
	estilo.configure("Chica.TLabel", foreground=TINTA_SUAVE, font=tema.interfaz_chica)
	estilo.configure("Titulo.TLabel", font=tema.titulo)
	estilo.configure("Formula.TLabel", font=tema.formula, foreground=TINTA_SUAVE)
	estilo.configure("Seccion.TLabel", font=tema.interfaz_destacada)
	estilo.configure("Etiqueta.TLabel", font=tema.matematica)
	estilo.configure("Encabezado.TLabel", font=tema.numeros_destacados, foreground=TINTA_SUAVE)
	estilo.configure("Termino.TLabel", font=tema.numeros_destacados, foreground=ROJO)

	for nombre_de_estilo, fuente in (("TEntry", tema.interfaz), ("Matematica.TEntry", tema.matematica)):
		estilo.configure(
			nombre_de_estilo,
			padding=(px(7), px(4)),
			fieldbackground=SUPERFICIE,
			bordercolor=LINEA_FUERTE,
			lightcolor=SUPERFICIE,
			darkcolor=SUPERFICIE,
			font=fuente,
		)
		estilo.map(
			nombre_de_estilo,
			bordercolor=[("focus", AZUL)],
			lightcolor=[("focus", AZUL)],
		)
	# Estado inválido: borde rojo, se quita apenas el usuario vuelve a escribir.
	for nombre_de_estilo in ("Invalido.TEntry", "InvalidoMatematica.TEntry"):
		estilo.configure(nombre_de_estilo, bordercolor=ROJO, lightcolor=ROJO, darkcolor=SUPERFICIE)
		estilo.map(nombre_de_estilo, bordercolor=[("focus", ROJO)], lightcolor=[("focus", ROJO)])

	for nombre_de_estilo, color in (("Celda.TEntry", TINTA), ("CeldaTermino.TEntry", ROJO)):
		estilo.configure(
			nombre_de_estilo,
			padding=(px(4), px(3)),
			foreground=color,
			fieldbackground=SUPERFICIE,
			bordercolor=LINEA,
			lightcolor=SUPERFICIE,
			darkcolor=SUPERFICIE,
		)
		estilo.map(nombre_de_estilo, bordercolor=[("focus", AZUL)], lightcolor=[("focus", AZUL)])
	estilo.configure("CeldaInvalida.TEntry", padding=(px(4), px(3)), bordercolor=ROJO, lightcolor=ROJO)

	estilo.configure(
		"TCombobox",
		padding=(px(7), px(4)),
		fieldbackground=SUPERFICIE,
		background=SUPERFICIE,
		bordercolor=LINEA_FUERTE,
		lightcolor=SUPERFICIE,
		darkcolor=SUPERFICIE,
		arrowcolor=TINTA_SUAVE,
		foreground=TINTA,
		font=tema.matematica,
	)
	estilo.map(
		"TCombobox",
		bordercolor=[("focus", AZUL)],
		lightcolor=[("focus", AZUL)],
		fieldbackground=[("readonly", SUPERFICIE)],
		selectbackground=[("readonly", SUPERFICIE)],
		selectforeground=[("readonly", TINTA)],
	)

	estilo.configure(
		"TSpinbox",
		padding=(px(6), px(3)),
		fieldbackground=SUPERFICIE,
		bordercolor=LINEA_FUERTE,
		lightcolor=SUPERFICIE,
		darkcolor=SUPERFICIE,
		background=PAPEL,
		arrowcolor=TINTA_SUAVE,
		arrowsize=px(11),
	)
	estilo.map("TSpinbox", bordercolor=[("focus", AZUL)], lightcolor=[("focus", AZUL)])

	estilo.configure(
		"TCheckbutton",
		background=PAPEL,
		foreground=TINTA,
		indicatorbackground=SUPERFICIE,
		indicatorforeground=AZUL,
		upperbordercolor=LINEA_FUERTE,
		lowerbordercolor=LINEA_FUERTE,
		indicatormargin=(0, 0, px(8), 0),
		padding=(0, px(2)),
	)
	estilo.map(
		"TCheckbutton",
		background=[("active", PAPEL)],
		indicatorbackground=[("pressed", AZUL_TENUE)],
		upperbordercolor=[("focus", AZUL)],
		lowerbordercolor=[("focus", AZUL)],
	)

	estilo.configure(
		"Primario.TButton",
		font=tema.interfaz_destacada,
		padding=(px(18), px(9)),
		background=AZUL,
		foreground=SUPERFICIE,
		bordercolor=AZUL,
		lightcolor=AZUL,
		darkcolor=AZUL,
		focuscolor=SUPERFICIE,
		focusthickness=1,
	)
	estilo.map(
		"Primario.TButton",
		background=[("pressed", AZUL_OSCURO), ("active", AZUL_OSCURO)],
		lightcolor=[("pressed", AZUL_OSCURO), ("active", AZUL_OSCURO)],
		darkcolor=[("pressed", AZUL_OSCURO), ("active", AZUL_OSCURO)],
		bordercolor=[("focus", AZUL_OSCURO)],
	)

	estilo.configure(
		"Tecla.TButton",
		font=tema.interfaz,
		padding=(px(2), px(3)),
		width=5,
		background=SUPERFICIE,
		foreground=TINTA,
		bordercolor=LINEA,
		lightcolor=SUPERFICIE,
		darkcolor=SUPERFICIE,
	)
	estilo.map(
		"Tecla.TButton",
		background=[("pressed", AZUL_TENUE), ("active", "#F0F4FA")],
		bordercolor=[("active", LINEA_FUERTE)],
	)

	for orientacion in ("Vertical", "Horizontal"):
		estilo.configure(
			f"{orientacion}.TScrollbar",
			background=LINEA,
			troughcolor=SUPERFICIE,
			bordercolor=SUPERFICIE,
			lightcolor=LINEA,
			darkcolor=LINEA,
			arrowcolor=TINTA_SUAVE,
			gripcount=0,
			arrowsize=px(12),
		)
		estilo.map(
			f"{orientacion}.TScrollbar",
			background=[("active", LINEA_FUERTE)],
			lightcolor=[("active", LINEA_FUERTE)],
			darkcolor=[("active", LINEA_FUERTE)],
		)

	estilo.configure("TPanedwindow", background=SUPERFICIE)
	estilo.configure(
		"Sash", sashthickness=px(9), gripcount=0, background=SUPERFICIE, lightcolor=SUPERFICIE, bordercolor=SUPERFICIE
	)
	estilo.configure("TSeparator", background=LINEA)


def mostrar_barra_solo_si_hace_falta(barra: ttk.Scrollbar) -> Callable[[str, str], None]:
	"""Devuelve un `xscrollcommand`/`yscrollcommand` que oculta `barra` cuando todo el contenido entra.

	La barra tiene que estar ubicada con `grid`: se usa `grid_remove`,
	que recuerda dónde estaba para volver a mostrarla.
	"""

	def ajustar(primera: str, ultima: str) -> None:
		if float(primera) <= 0.0 and float(ultima) >= 1.0:
			barra.grid_remove()
		else:
			barra.grid()
		barra.set(primera, ultima)

	return ajustar
