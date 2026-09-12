"""Descriptor de la secante para la GUI unificada de métodos numéricos."""

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

from secante import secante


def ejecutar_secante(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	funcion = valores["funcion"]
	raiz, iteraciones = secante(
		funcion,
		float(valores["primera_aproximacion"]),
		float(valores["segunda_aproximacion"]),
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
	nombre_para_mostrar="Secante",
	capitulo="Raíces de funciones",
	formula="xᵢ₊₁ = xᵢ − f(xᵢ)·(xᵢ₋₁ − xᵢ) / (f(xᵢ₋₁) − f(xᵢ))",
	descripcion=(
		"Como Newton-Raphson, pero reemplaza la tangente por la recta que pasa por los dos "
		"últimos puntos. No necesita la derivada ni que f cambie de signo entre x₀ y x₁."
	),
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "exp(-x) - x"),
		CampoDeEntrada("primera_aproximacion", "x₀ =", TipoDeCampo.NUMERO, "0,4"),
		CampoDeEntrada("segunda_aproximacion", "x₁ =", TipoDeCampo.NUMERO, "0,8"),
	),
	ejecutar=ejecutar_secante,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("aproximacion", "xᵢ", es_raiz=True),
		ColumnaDeTabla("valor_funcion", "f(xᵢ)"),
		ColumnaDeTabla("error", "|E|", es_error=True),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.SECANTES, "funcion"),
)
