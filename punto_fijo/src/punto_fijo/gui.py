"""Descriptor de punto fijo para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
)

from punto_fijo import punto_fijo


def ejecutar_punto_fijo(valores: dict[str, object], reportar_iteracion: ReportarIteracion) -> ResultadoDeMetodo:
	raiz, iteraciones = punto_fijo(
		valores["funcion_g"],
		float(valores["valor_inicial"]),
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz aproximada",
		valor_formateado=f"{raiz:.6f}",
		cantidad_de_iteraciones=iteraciones,
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Punto Fijo",
	descripcion="Busca una raíz de f(x) = 0 iterando x_(n+1) = g(x_n), donde g(x) es el despeje de x en f(x) = 0.",
	campos=(
		CampoDeEntrada("funcion_g", "g(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "sqrt(x + 2)"),
		CampoDeEntrada("valor_inicial", "Valor inicial (x0):", TipoDeCampo.NUMERO, "1.5"),
	),
	ejecutar=ejecutar_punto_fijo,
)
