"""Descriptor de punto fijo para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos import (
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

from metodos_numericos.punto_fijo import punto_fijo


def ejecutar_punto_fijo(valores: dict[str, object], reportar_iteracion: ReportarIteracion) -> ResultadoDeMetodo:
	"""Corre `punto_fijo` con los valores que leyó la GUI.

	Args:
		valores: Valores de los campos, ya convertidos: `"funcion_g"` (g(x)
			como función), `"valor_inicial"`, `"tolerancia"` y
			`"maximo_iteraciones"`.
		reportar_iteracion: Se le pasa tal cual a `punto_fijo`, para que la
			GUI vaya llenando la tabla y el gráfico.

	Returns:
		La raíz, la cantidad de iteraciones y la verificación g(raíz), que
		tendría que dar igual a la raíz (es un punto fijo de g).
	"""
	funcion_g = valores["funcion_g"]
	raiz, iteraciones = punto_fijo(
		funcion_g,
		float(valores["valor_inicial"]),
		tolerancia=float(valores["tolerancia"]),
		maximo_iteraciones=int(valores["maximo_iteraciones"]),
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz",
		valor=raiz,
		cantidad_de_iteraciones=iteraciones,
		verificaciones=(Verificacion("g(raíz)", funcion_g(raiz), esperado=raiz),),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Punto fijo",
	capitulo="Raíces de funciones",
	formula=r"x_{i+1} = g(x_i)",
	descripcion=(
		"Busca dónde g(x) corta a la recta y = x, con g(x) despejada de f(x) = 0. "
		"Converge si |g′(x)| < 1 cerca de la raíz."
	),
	campos=(
		CampoDeEntrada("funcion_g", "g(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "exp(-x)"),
		CampoDeEntrada("valor_inicial", "x₀ =", TipoDeCampo.NUMERO, "0,4"),
	),
	ejecutar=ejecutar_punto_fijo,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("aproximacion", "xᵢ", es_raiz=True),
		ColumnaDeTabla("valor_g", "g(xᵢ)"),
		ColumnaDeTabla("error", "|E|", es_error=True),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.TELARANA, "funcion_g"),
)
