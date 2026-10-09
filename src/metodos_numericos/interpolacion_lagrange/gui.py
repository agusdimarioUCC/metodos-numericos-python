"""Descriptor de la interpolación de Lagrange para la GUI unificada de métodos numéricos."""

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
	columnas_fijas,
)

from metodos_numericos.interpolacion_lagrange import desarrollar_polinomio, interpolacion_lagrange


def ejecutar_interpolacion_lagrange(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	"""Evalúa Pₙ(x) con los puntos de la GUI y deja el polinomio para el gráfico."""
	valores_x, valores_y = valores["puntos"]
	valor, polinomio = interpolacion_lagrange(
		valores_x, valores_y, valores["valor_a_interpolar"], reportar_iteracion=reportar_iteracion
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="P(x)",
		valor=valor,
		cantidad_de_iteraciones=len(valores_x),
		funcion_para_grafico=polinomio,
		puntos_de_datos=tuple(zip(valores_x, valores_y)),
		punto_de_resultado=(valores["valor_a_interpolar"], valor),
		polinomio_desarrollado=desarrollar_polinomio(valores_x, valores_y),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Interpolación de Lagrange",
	capitulo="Ajuste de curvas",
	formula=r"P_n(x) = \sum_{i=0}^{n} L_i(x)\,y_i, \quad L_i(x) = \prod_{j=0,\ j \neq i}^{n} \dfrac{x - x_j}{x_i - x_j}",
	descripcion=(
		"Arma un polinomio Lᵢ(x) por punto que vale 1 en xᵢ y 0 en los demás nodos; la suma de "
		"Lᵢ(x)·yᵢ es el polinomio que pasa exactamente por todos los puntos, sin diferencias divididas."
	),
	campos=(
		CampoDeEntrada(
			"puntos",
			"(xᵢ, yᵢ) =",
			TipoDeCampo.TABLA_DE_PUNTOS,
			"0 1\n1 2.7182\n2 7.3891\n3 20.0855",
		),
		CampoDeEntrada("valor_a_interpolar", "x =", TipoDeCampo.NUMERO, "1.5"),
	),
	ejecutar=ejecutar_interpolacion_lagrange,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("valor_x", "xᵢ"),
		ColumnaDeTabla("valor_y", "yᵢ"),
		ColumnaDeTabla("base", "Lᵢ(x)"),
		ColumnaDeTabla("termino", "Lᵢ(x)·yᵢ"),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.DISPERSION_Y_AJUSTE),
	usa_criterio_de_parada=False,
)
