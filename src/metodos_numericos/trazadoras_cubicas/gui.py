"""Descriptor de las trazadoras cúbicas para la GUI unificada de métodos numéricos."""

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

from metodos_numericos.trazadoras_cubicas import MODELOS_DISPONIBLES, trazadora_cubica


def ejecutar_trazadoras_cubicas(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	"""Arma la trazadora con los puntos de la GUI y la evalúa en `valor_a_interpolar`."""
	valores_x, valores_y = valores["puntos"]
	valor_a_interpolar = valores["valor_a_interpolar"]
	_, trazadora = trazadora_cubica(
		valores_x,
		valores_y,
		valores["tipo"],
		derivada_inicial=valores["derivada_inicial"],
		derivada_final=valores["derivada_final"],
		reportar_iteracion=reportar_iteracion,
	)
	advertencias: tuple[str, ...] = ()
	if not min(valores_x) <= valor_a_interpolar <= max(valores_x):
		advertencias = (
			"x está fuera del intervalo de los puntos: se extiende el primer o el último polinomio, "
			"que solo vale en su propio tramo.",
		)
	return ResultadoDeMetodo(
		etiqueta_del_valor="S(x)",
		valor=trazadora(valor_a_interpolar),
		cantidad_de_iteraciones=len(valores_x),
		advertencias=advertencias,
		funcion_para_grafico=trazadora,
		puntos_de_datos=tuple(zip(valores_x, valores_y)),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Trazadoras cúbicas",
	capitulo="Ajuste de curvas",
	formula=r"S_i(x) = a_i + b_i(x - x_i) + c_i(x - x_i)^2 + d_i(x - x_i)^3",
	descripcion=(
		"Pasa un polinomio de tercer grado entre cada par de puntos, con la misma imagen, pendiente y "
		"curvatura en los empalmes. Natural: S″ = 0 en los bordes. Condicionada: S′ dada en x₀ y xₙ "
		"(S′(x₀) y S′(xₙ) solo se usan en esta)."
	),
	campos=(
		CampoDeEntrada("tipo", "Tipo", TipoDeCampo.SELECTOR, MODELOS_DISPONIBLES[0], opciones=MODELOS_DISPONIBLES),
		CampoDeEntrada(
			"puntos",
			"(xᵢ, yᵢ) =",
			TipoDeCampo.TABLA_DE_PUNTOS,
			"0 1\n1 2.7182\n2 7.3891\n3 20.0855",
		),
		CampoDeEntrada("valor_a_interpolar", "x =", TipoDeCampo.NUMERO, "1.5"),
		CampoDeEntrada("derivada_inicial", "S′(x₀) =", TipoDeCampo.NUMERO, "1"),
		CampoDeEntrada("derivada_final", "S′(xₙ) =", TipoDeCampo.NUMERO, "20.0855"),
	),
	ejecutar=ejecutar_trazadoras_cubicas,
	columnas=columnas_fijas(
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("valor_x", "xᵢ"),
		ColumnaDeTabla("valor_a", "aᵢ"),
		ColumnaDeTabla("h", "hᵢ"),
		ColumnaDeTabla("alfa", "αᵢ"),
		ColumnaDeTabla("l", "lᵢ"),
		ColumnaDeTabla("mu", "μᵢ"),
		ColumnaDeTabla("z", "zᵢ"),
		ColumnaDeTabla("c", "cᵢ"),
		ColumnaDeTabla("b", "bᵢ"),
		ColumnaDeTabla("d", "dᵢ"),
	),
	grafico=GraficoDeMetodo(TipoDeGrafico.DISPERSION_Y_AJUSTE),
	usa_criterio_de_parada=False,
)
