"""Descriptor de bisección para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	COLUMNA_DE_NUMERO_DE_FILA,
	CampoDeEntrada,
	ColumnaDeTabla,
	DescriptorDeMetodo,
	FormatoDeColumna,
	GraficoDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
	TipoDeGrafico,
	Verificacion,
	columnas_fijas,
)

from biseccion import biseccion


def ejecutar_biseccion(valores: dict[str, object], reportar_iteracion: ReportarIteracion) -> ResultadoDeMetodo:
	funcion = valores["funcion"]
	raiz, iteraciones = biseccion(
		funcion,
		float(valores["extremo_inferior"]),
		float(valores["extremo_superior"]),
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
	nombre_para_mostrar="Bisección",
	capitulo="Raíces de funciones",
	formula="c = (a + b) / 2",
	descripcion=(
		"Parte el intervalo [a; b] a la mitad en cada paso y se queda con la mitad donde f "
		"cambia de signo. Necesita f(a)·f(b) < 0."
	),
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "exp(-x) - x"),
		CampoDeEntrada("extremo_inferior", "a =", TipoDeCampo.NUMERO, "0,4"),
		CampoDeEntrada("extremo_superior", "b =", TipoDeCampo.NUMERO, "0,8"),
	),
	ejecutar=ejecutar_biseccion,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("extremo_inferior", "a"),
		ColumnaDeTabla("extremo_superior", "b"),
		ColumnaDeTabla("aproximacion", "c", es_raiz=True),
		ColumnaDeTabla("valor_extremo_inferior", "f(a)"),
		ColumnaDeTabla("valor_punto_medio", "f(c)"),
		ColumnaDeTabla("producto", "f(a)·f(c)", FormatoDeColumna.SIGNO),
		ColumnaDeTabla("error", "|E|", es_error=True),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.INTERVALOS, "funcion"),
)
