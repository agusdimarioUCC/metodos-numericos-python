"""Descriptor de la interpolación de Newton para la GUI unificada de métodos numéricos."""

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
	subindice,
)

from interpolacion_newton import interpolacion_newton


def ejecutar_interpolacion_newton(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	valores_x, valores_y = valores["puntos"]
	valor_a_interpolar = valores["valor_a_interpolar"]
	coeficientes, polinomio = interpolacion_newton(valores_x, valores_y, reportar_iteracion=reportar_iteracion)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Coeficientes del polinomio",
		valor=coeficientes,
		etiquetas_de_componentes=tuple(f"b{subindice(orden)}" for orden in range(len(coeficientes))),
		cantidad_de_iteraciones=len(valores_x),
		verificaciones=(Verificacion(f"P{subindice(len(coeficientes) - 1)}(x)", polinomio(valor_a_interpolar)),),
		funcion_para_grafico=polinomio,
		puntos_de_datos=tuple(zip(valores_x, valores_y)),
	)


def _encabezado_de_orden(orden: int) -> str:
	"""f[xᵢ₊₁;xᵢ], f[xᵢ₊₂;xᵢ₊₁;xᵢ], y de orden 3 en adelante f[xᵢ₊ₖ;…;xᵢ], como en la pizarra."""
	if orden == 1:
		return "f[xᵢ₊₁;xᵢ]"
	if orden == 2:
		return "f[xᵢ₊₂;xᵢ₊₁;xᵢ]"
	return f"f[xᵢ₊{subindice(orden)};…;xᵢ]"


def armar_columnas(valores: dict[str, object]) -> tuple[ColumnaDeTabla, ...]:
	"""i, xᵢ, yᵢ y una columna escalonada de diferencias divididas por orden, hasta n.

	El orden k va corrido k/2 filas, así cada diferencia queda a la altura
	media de los puntos de los que sale, como la tabla de la pizarra.
	"""
	valores_x, _ = valores["puntos"]
	return (
		COLUMNA_DE_NUMERO_DE_FILA,
		ColumnaDeTabla("valor_x", "xᵢ"),
		ColumnaDeTabla("valor_y", "yᵢ"),
		*(
			ColumnaDeTabla(f"orden_{orden}", _encabezado_de_orden(orden), desplazamiento_en_filas=orden / 2)
			for orden in range(1, len(valores_x))
		),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Interpolación de Newton",
	capitulo="Ajuste de curvas",
	formula="Pₙ(x) = b₀ + b₁(x − x₀) + … + bₙ(x − x₀)…(x − xₙ₋₁)",
	descripcion=(
		"Arma la tabla de diferencias divididas y usa su primera fila (bₖ = f[xₖ;…;x₀]) como "
		"coeficientes del polinomio que pasa exactamente por todos los puntos."
	),
	campos=(
		CampoDeEntrada(
			"puntos",
			"(xᵢ, yᵢ) =",
			TipoDeCampo.TABLA_DE_PUNTOS,
			"1 0\n4 1.386294\n6 1.791759\n5 1.609438",
		),
		CampoDeEntrada("valor_a_interpolar", "x =", TipoDeCampo.NUMERO, "2"),
	),
	ejecutar=ejecutar_interpolacion_newton,
	columnas=armar_columnas,
	grafico=GraficoDeMetodo(TipoDeGrafico.DISPERSION_Y_AJUSTE),
	usa_criterio_de_parada=False,
)
