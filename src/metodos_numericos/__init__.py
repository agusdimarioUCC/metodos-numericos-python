"""Utilidades y GUI compartidas por los métodos numéricos iterativos del repo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from metodos_numericos.descriptor import (
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
from metodos_numericos.errores import EntradaInvalidaError, NoConvergeError
from metodos_numericos.expresiones import compilar_funcion, evaluar_funcion
from metodos_numericos.formato import formatear_numero, formatear_valor_corto, leer_numero, subindice
from metodos_numericos.iteracion import Iteracion, ReportarIteracion

if TYPE_CHECKING:
	from metodos_numericos.gui import PanelDeMetodo, VentanaMetodosNumericos

_NOMBRES_DE_LA_GUI = frozenset({"PanelDeMetodo", "VentanaMetodosNumericos"})


def __getattr__(nombre: str) -> object:
	# La GUI importa tkinter y matplotlib, que tardan en cargar: se importa
	# recién cuando alguien la pide, para que los modulos de cada metodo (que tambien
	# importan este paquete) no paguen ese costo.
	if nombre in _NOMBRES_DE_LA_GUI:
		from metodos_numericos import gui

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
	"formatear_numero",
	"formatear_valor_corto",
	"leer_numero",
	"subindice",
]
