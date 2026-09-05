"""Descriptor de Newton-Raphson para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
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
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz aproximada",
		valor_formateado=f"{raiz:.6f}",
		cantidad_de_iteraciones=iteraciones,
		lineas_de_verificacion=(f"f(raíz) = {funcion(raiz):.3e}",),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Newton-Raphson",
	descripcion="Busca una raíz de f(x) = 0 a partir de un valor inicial x0, usando f(x) y su derivada f'(x).",
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "x**2 - 2"),
		CampoDeEntrada("derivada", "f'(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "2*x"),
		CampoDeEntrada("valor_inicial", "Valor inicial (x0):", TipoDeCampo.NUMERO, "1.5"),
	),
	ejecutar=ejecutar_newton_raphson,
)
