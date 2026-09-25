"""Utilidades y GUI compartidas por los métodos numéricos iterativos del repo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from metodos_numericos_base.descriptor import (
	COLUMNA_DE_NUMERO_DE_FILA,
	CampoDeEntrada,
	ColumnaDeTabla,
	DescriptorDeMetodo,
	FormatoDeColumna,
	GraficoDeMetodo,
	MatrizDeResultado,
	ResultadoDeMetodo,
	TipoDeCampo,
	TipoDeGrafico,
	Verificacion,
	columnas_fijas,
)
from metodos_numericos_base.errores import EntradaInvalidaError, NoConvergeError
from metodos_numericos_base.expresiones import compilar_funcion, evaluar_funcion
from metodos_numericos_base.formato import formatear_numero, formatear_valor_corto, leer_numero, subindice
from metodos_numericos_base.iteracion import (
	Iteracion,
	ReportarIteracion,
	formatear_aproximacion,
	imprimir_iteracion,
)
from metodos_numericos_base.terminal import (
	leer_funcion_desde_terminal,
	leer_opcion_desde_terminal,
	leer_puntos_desde_terminal,
	leer_valor_inicial_desde_terminal,
)

if TYPE_CHECKING:
	from metodos_numericos_base.gui import PanelDeMetodo, VentanaMetodosNumericos

_NOMBRES_DE_LA_GUI = frozenset({"PanelDeMetodo", "VentanaMetodosNumericos"})


def __getattr__(nombre: str) -> object:
	# La GUI importa tkinter y matplotlib, que tardan en cargar: se importa
	# recién cuando alguien la pide, para que los scripts de terminal de
	# cada método (que también importan este paquete) no paguen ese costo.
	if nombre in _NOMBRES_DE_LA_GUI:
		from metodos_numericos_base import gui

		return getattr(gui, nombre)
	raise AttributeError(f"module {__name__!r} has no attribute {nombre!r}")


__all__ = [
	"COLUMNA_DE_NUMERO_DE_FILA",
	"CampoDeEntrada",
	"ColumnaDeTabla",
	"DescriptorDeMetodo",
	"EntradaInvalidaError",
	"FormatoDeColumna",
	"GraficoDeMetodo",
	"Iteracion",
	"MatrizDeResultado",
	"NoConvergeError",
	"PanelDeMetodo",
	"ReportarIteracion",
	"ResultadoDeMetodo",
	"TipoDeCampo",
	"TipoDeGrafico",
	"VentanaMetodosNumericos",
	"Verificacion",
	"columnas_fijas",
	"compilar_funcion",
	"evaluar_funcion",
	"formatear_aproximacion",
	"formatear_numero",
	"formatear_valor_corto",
	"imprimir_iteracion",
	"leer_funcion_desde_terminal",
	"leer_numero",
	"leer_opcion_desde_terminal",
	"leer_puntos_desde_terminal",
	"leer_valor_inicial_desde_terminal",
	"subindice",
]
