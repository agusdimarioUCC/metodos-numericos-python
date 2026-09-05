"""Descriptor de la secante para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
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
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz aproximada",
		valor_formateado=f"{raiz:.6f}",
		cantidad_de_iteraciones=iteraciones,
		lineas_de_verificacion=(f"f(raíz) = {funcion(raiz):.3e}",),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Secante",
	descripcion="Busca una raíz de f(x) = 0 a partir de dos aproximaciones iniciales x0 y x1, sin usar la derivada.",
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "x**2 - 2"),
		CampoDeEntrada("primera_aproximacion", "Primera aproximación (x0):", TipoDeCampo.NUMERO, "1"),
		CampoDeEntrada("segunda_aproximacion", "Segunda aproximación (x1):", TipoDeCampo.NUMERO, "2"),
	),
	ejecutar=ejecutar_secante,
)
