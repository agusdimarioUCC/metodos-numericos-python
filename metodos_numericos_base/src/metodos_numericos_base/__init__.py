"""Utilidades y GUI compartidas por los métodos numéricos iterativos del repo."""

from __future__ import annotations

from metodos_numericos_base.descriptor import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ResultadoDeMetodo,
	TipoDeCampo,
)
from metodos_numericos_base.errores import EntradaInvalidaError, NoConvergeError
from metodos_numericos_base.expresiones import compilar_funcion, evaluar_funcion
from metodos_numericos_base.gui import (
	PanelDeMetodo,
	VentanaMetodosNumericos,
	elegir_fuente_matematica,
	elegir_fuente_monoespaciada,
)
from metodos_numericos_base.iteracion import (
	Iteracion,
	ReportarIteracion,
	formatear_aproximacion,
	imprimir_iteracion,
)
from metodos_numericos_base.terminal import (
	leer_funcion_desde_terminal,
	leer_valor_inicial_desde_terminal,
)

__all__ = [
	"CampoDeEntrada",
	"DescriptorDeMetodo",
	"EntradaInvalidaError",
	"Iteracion",
	"NoConvergeError",
	"PanelDeMetodo",
	"ReportarIteracion",
	"ResultadoDeMetodo",
	"TipoDeCampo",
	"VentanaMetodosNumericos",
	"compilar_funcion",
	"elegir_fuente_matematica",
	"elegir_fuente_monoespaciada",
	"evaluar_funcion",
	"formatear_aproximacion",
	"imprimir_iteracion",
	"leer_funcion_desde_terminal",
	"leer_valor_inicial_desde_terminal",
]
