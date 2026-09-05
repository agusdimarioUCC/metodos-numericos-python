"""Descriptor de bisección para la GUI unificada de métodos numéricos."""

from __future__ import annotations

from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
)

from biseccion import biseccion


def ejecutar_biseccion(valores: dict[str, object], reportar_iteracion: ReportarIteracion) -> ResultadoDeMetodo:
	funcion = valores["funcion"]
	raiz, iteraciones = biseccion(
		funcion,
		float(valores["extremo_inferior"]),
		float(valores["extremo_superior"]),
		reportar_iteracion=reportar_iteracion,
	)
	return ResultadoDeMetodo(
		etiqueta_del_valor="Raíz aproximada",
		valor_formateado=f"{raiz:.6f}",
		cantidad_de_iteraciones=iteraciones,
		lineas_de_verificacion=(f"f(raíz) = {funcion(raiz):.3e}",),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Bisección",
	descripcion="Busca una raíz de f(x) = 0 en [extremo inferior, extremo superior]. f(x) debe cambiar de signo en el intervalo.",
	campos=(
		CampoDeEntrada("funcion", "f(x) =", TipoDeCampo.EXPRESION_MATEMATICA, "x**2 - 2"),
		CampoDeEntrada("extremo_inferior", "Extremo inferior:", TipoDeCampo.NUMERO, "1"),
		CampoDeEntrada("extremo_superior", "Extremo superior:", TipoDeCampo.NUMERO, "2"),
	),
	ejecutar=ejecutar_biseccion,
)
