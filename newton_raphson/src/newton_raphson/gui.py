"""Descriptor de Newton-Raphson para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	COLUMNA_DE_NUMERO_DE_FILA,
	CampoDeEntrada,
	ColumnaDeTabla,
	DescriptorDeMetodo,
	GraficoDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
	TipoDeGrafico,
	Verificacion,
	columnas_fijas,
)

from newton_raphson import newton_raphson


def ejecutar_newton_raphson(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	funcion = valores["funcion"]
	raiz, iteraciones = newton_raphson(
		funcion,
		valores["derivada"],
		float(valores["valor_inicial"]),
		tolerancia=float(valores["tolerancia"]),
		maximo_iteraciones=int(valores["maximo_iteraciones"]),
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz",
		valor=raiz,
		cantidad_de_iteraciones=iteraciones,
		verificaciones=(Verificacion("f(raíz)", funcion(raiz)),),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Newton-Raphson",
	capitulo="Raíces de funciones",
	formula="xᵢ₊₁ = xᵢ − f(xᵢ) / f′(xᵢ)",
	descripcion=(
		"Sigue la recta tangente a f en cada xᵢ hasta donde corta al eje x. "
		"Necesita la derivada f′(x) escrita a mano."
	),
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "exp(-x) - x"),
		CampoDeEntrada("derivada", "f′(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "-exp(-x) - 1"),
		CampoDeEntrada("valor_inicial", "x₀ =", TipoDeCampo.NUMERO, "0,4"),
	),
	ejecutar=ejecutar_newton_raphson,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("aproximacion", "xᵢ", es_raiz=True),
		ColumnaDeTabla("valor_funcion", "f(xᵢ)"),
		ColumnaDeTabla("valor_derivada", "f′(xᵢ)"),
		ColumnaDeTabla("error", "|E|", es_error=True),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.TANGENTES, "funcion"),
)
