"""Descriptor de la regresión lineal para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from dataclasses import replace

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
)
from metodos_numericos.formato import SIGNO_MENOS, formatear_numero, formatear_polinomio

from metodos_numericos.regresion_lineal import MODELOS_DISPONIBLES, regresion_lineal


def ejecutar_regresion_lineal(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	"""Ajusta el modelo elegido a los puntos de la GUI.

	Para el modelo Lineal devuelve (a₀, a₁); para los linealizados devuelve
	(A, B), o (A, b) en Crecimiento, y deja a₀, a₁ como verificaciones.
	"""
	tipo_modelo = valores["modelo"]
	valores_x, valores_y = valores["puntos"]
	parametros, funcion = regresion_lineal(
		tipo_modelo, valores_x, valores_y, reportar_iteracion=reportar_iteracion
	)

	if tipo_modelo == "Lineal":
		etiquetas_de_componentes = ("a₀", "a₁")
		valor = (parametros["a0"], parametros["a1"])
		verificaciones: tuple[Verificacion, ...] = ()
	else:
		segundo_parametro = "b" if tipo_modelo == "Crecimiento" else "B"
		etiquetas_de_componentes = ("A", segundo_parametro)
		valor = (parametros["A"], parametros[segundo_parametro])
		verificaciones = (
			Verificacion("a₀", parametros["a0"]),
			Verificacion("a₁", parametros["a1"]),
		)

	return ResultadoDeMetodo(
		etiqueta_del_valor="Parámetros ajustados",
		valor=valor,
		etiquetas_de_componentes=etiquetas_de_componentes,
		cantidad_de_iteraciones=len(valores_x),
		verificaciones=verificaciones,
		funcion_para_grafico=funcion,
		puntos_de_datos=tuple(zip(valores_x, valores_y)),
		expresiones=lambda decimales: (escribir_modelo(tipo_modelo, parametros, decimales),),
	)


def escribir_modelo(tipo_modelo: str, parametros: dict[str, float], decimales: int) -> str:
	"""La curva ajustada como la escriben los apuntes: `y = 0,8393x + 0,0714`, `y = 0,3430·e^(0,6853x)`."""
	if tipo_modelo == "Lineal":
		return f"y = {formatear_polinomio((parametros['a0'], parametros['a1']), decimales)}"
	coeficiente = formatear_numero(parametros["A"], decimales)
	if tipo_modelo == "Exponencial":
		return f"y = {coeficiente}·e^({formatear_numero(parametros['B'], decimales)}x)"
	if tipo_modelo == "Potencial":
		return f"y = {coeficiente}·x^({formatear_numero(parametros['B'], decimales)})"
	desplazamiento = parametros["b"]
	signo = SIGNO_MENOS if desplazamiento < 0 else "+"
	return f"y = {coeficiente}·x / (x {signo} {formatear_numero(abs(desplazamiento), decimales)})"


def armar_columnas(valores: dict[str, object]) -> tuple[ColumnaDeTabla, ...]:
	"""Arma la tabla de sumatorias de los apuntes, con las columnas que corresponden al modelo elegido."""
	tipo_modelo = valores["modelo"]
	columnas = [COLUMNA_DE_NUMERO_DE_FILA, ColumnaDeTabla("valor_x", "Xᵢ"), ColumnaDeTabla("valor_y", "Yᵢ")]
	if tipo_modelo == "Lineal":
		columnas += [ColumnaDeTabla("u_cuadrado", "Xᵢ²"), ColumnaDeTabla("uv", "XᵢYᵢ")]
	elif tipo_modelo == "Exponencial":
		columnas += [
			ColumnaDeTabla("v", "LnYᵢ"),
			ColumnaDeTabla("u_cuadrado", "Xᵢ²"),
			ColumnaDeTabla("uv", "XᵢLnYᵢ"),
		]
	elif tipo_modelo == "Potencial":
		columnas += [
			ColumnaDeTabla("u", "LogXᵢ"),
			ColumnaDeTabla("v", "LogYᵢ"),
			ColumnaDeTabla("u_cuadrado", "(LogXᵢ)²"),
			ColumnaDeTabla("uv", "(LogXᵢ)(LogYᵢ)"),
		]
	else:  # Crecimiento
		columnas += [
			ColumnaDeTabla("u", "1/Xᵢ"),
			ColumnaDeTabla("v", "1/Yᵢ"),
			ColumnaDeTabla("u_cuadrado", "(1/Xᵢ)²"),
			ColumnaDeTabla("uv", "(1/Xᵢ)(1/Yᵢ)"),
		]
	# Todas menos i llevan su Σ al pie: son las sumatorias de las fórmulas de a₁ y a₀.
	return (columnas[0], *(replace(columna, sumar=True) for columna in columnas[1:]))


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Regresión lineal",
	capitulo="Ajuste de curvas",
	formula=r"y = a_0 + a_1 x",
	descripcion=(
		"Ajusta y = a₀ + a₁x (o una versión linealizada de un modelo exponencial, potencial o de "
		"crecimiento) a un conjunto de puntos por mínimos cuadrados."
	),
	campos=(
		CampoDeEntrada(
			"modelo", "Modelo", TipoDeCampo.SELECTOR, MODELOS_DISPONIBLES[0], opciones=MODELOS_DISPONIBLES
		),
		CampoDeEntrada(
			"puntos",
			"(Xᵢ, Yᵢ) =",
			TipoDeCampo.TABLA_DE_PUNTOS,
			"1 0.5\n2 2.5\n3 2.0\n4 4.0\n5 3.5\n6 6.0\n7 5.5",
		),
	),
	ejecutar=ejecutar_regresion_lineal,
	columnas=armar_columnas,
	grafico=GraficoDeMetodo(TipoDeGrafico.DISPERSION_Y_AJUSTE),
	usa_criterio_de_parada=False,
)
