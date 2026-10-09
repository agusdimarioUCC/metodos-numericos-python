"""Descriptor de bisección para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos import (
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

from metodos_numericos.biseccion import biseccion


def ejecutar_biseccion(valores: dict[str, object], reportar_iteracion: ReportarIteracion) -> ResultadoDeMetodo:
	"""Corre `biseccion` con los valores que leyó la GUI.

	Args:
		valores: Valores de los campos, ya convertidos: `"funcion"` (f(x)
			como función), `"extremo_inferior"`, `"extremo_superior"`,
			`"tolerancia"` y `"maximo_iteraciones"`.
		reportar_iteracion: Se le pasa tal cual a `biseccion`, para que la
			GUI vaya llenando la tabla y el gráfico.

	Returns:
		La raíz, la cantidad de iteraciones y la verificación f(raíz), que
		tendría que dar cerca de 0.
	"""
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
	formula=r"c = \dfrac{a + b}{2}",
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
