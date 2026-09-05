"""Descriptor de Gauss-Seidel para la GUI unificada de métodos numéricos."""

from __future__ import annotations

import numpy as np
from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
	formatear_aproximacion,
)

from gauss_seidel import es_diagonalmente_dominante, gauss_seidel, reordenar_para_dominancia_diagonal


def ejecutar_gauss_seidel(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	matriz_coeficientes, terminos_independientes = valores["sistema"]
	matriz_coeficientes = np.array(matriz_coeficientes, dtype=np.float64)
	terminos_independientes = np.array(terminos_independientes, dtype=np.float64)

	advertencias: list[str] = []
	if valores["reordenar"] and not es_diagonalmente_dominante(matriz_coeficientes):
		matriz_coeficientes, terminos_independientes = reordenar_para_dominancia_diagonal(
			matriz_coeficientes, terminos_independientes
		)
		if es_diagonalmente_dominante(matriz_coeficientes):
			advertencias.append("A no era diagonalmente dominante: se reordenaron las filas.")
		else:
			advertencias.append(
				"A no era diagonalmente dominante y no se encontró un orden que lo logre; "
				"puede no converger."
			)

	solucion, iteraciones = gauss_seidel(
		matriz_coeficientes, terminos_independientes, reportar_iteracion=reportar_iteracion
	)

	verificacion = matriz_coeficientes @ solucion
	lineas_de_verificacion = (
		f"A · x =            {formatear_aproximacion(tuple(verificacion))}",
		f"Término independiente = {formatear_aproximacion(tuple(terminos_independientes))}",
	)

	return ResultadoDeMetodo(
		etiqueta_del_valor="Solución",
		valor_formateado=formatear_aproximacion(tuple(solucion)),
		cantidad_de_iteraciones=iteraciones,
		lineas_de_verificacion=lineas_de_verificacion,
		advertencias=tuple(advertencias),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Gauss-Seidel",
	descripcion="Resuelve un sistema Ax = b. Elegí el tamaño n y completá cada coeficiente y término independiente.",
	campos=(
		CampoDeEntrada(
			"sistema",
			"Sistema:",
			TipoDeCampo.SISTEMA_DE_ECUACIONES,
			"12 -1 3 | 8\n1 7 -3 | -51\n4 -4 9 | 61",
		),
		CampoDeEntrada(
			"reordenar",
			"Reordenar filas automáticamente si hace falta:",
			TipoDeCampo.CASILLA_DE_VERIFICACION,
			"si",
		),
	),
	ejecutar=ejecutar_gauss_seidel,
	encabezado_de_aproximacion="Aproximación (x₁ … xₙ)",
)
