"""Descriptor de Gauss-Seidel para la GUI unificada de métodos numéricos."""

from __future__ import annotations

import numpy as np
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

from gauss_seidel import es_diagonalmente_dominante, gauss_seidel, reordenar_para_dominancia_diagonal


def ejecutar_gauss_seidel(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	filas, terminos = valores["sistema"]
	matriz_original = np.array(filas, dtype=np.float64)
	terminos_originales = np.array(terminos, dtype=np.float64)
	matriz_coeficientes, terminos_independientes = matriz_original, terminos_originales

	advertencias: list[str] = []
	if valores["reordenar"] and not es_diagonalmente_dominante(matriz_coeficientes):
		matriz_coeficientes, terminos_independientes = reordenar_para_dominancia_diagonal(
			matriz_coeficientes, terminos_independientes
		)
		if es_diagonalmente_dominante(matriz_coeficientes):
			advertencias.append("A no era diagonalmente dominante: se reordenaron las ecuaciones.")
		else:
			advertencias.append(
				"A no es diagonalmente dominante y ningún orden de las ecuaciones lo logra: "
				"puede no converger."
			)

	solucion, iteraciones = gauss_seidel(
		matriz_coeficientes,
		terminos_independientes,
		tolerancia=float(valores["tolerancia"]),
		maximo_iteraciones=int(valores["maximo_iteraciones"]),
		reportar_iteracion=reportar_iteracion,
	)

	lado_izquierdo = matriz_original @ solucion
	verificaciones = tuple(
		Verificacion(f"Ecuación {numero}", float(valor), esperado=float(termino))
		for numero, (valor, termino) in enumerate(zip(lado_izquierdo, terminos_originales), start=1)
	)

	return ResultadoDeMetodo(
		etiqueta_del_valor="Solución",
		valor=tuple(float(componente) for componente in solucion),
		cantidad_de_iteraciones=iteraciones,
		verificaciones=verificaciones,
		advertencias=tuple(advertencias),
	)


def armar_columnas(valores: dict[str, object]) -> tuple[ColumnaDeTabla, ...]:
	"""Una columna Xⱼ y una |Eⱼ| por incógnita, como la tabla de Gauss-Seidel de los apuntes."""
	filas, _ = valores["sistema"]
	columnas = [COLUMNA_DE_NUMERO_DE_FILA]
	for indice in range(1, len(filas) + 1):
		columnas.append(ColumnaDeTabla(f"componente_{indice}", f"X{subindice(indice)}", es_raiz=True))
		columnas.append(ColumnaDeTabla(f"error_{indice}", f"|E{subindice(indice)}|", es_error=True))
	return tuple(columnas)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Gauss-Seidel",
	capitulo="Sistemas de ecuaciones lineales",
	formula="xᵢ = (bᵢ − Σⱼ≠ᵢ aᵢⱼ·xⱼ) / aᵢᵢ",
	descripcion=(
		"Despeja cada incógnita de su ecuación y usa enseguida los valores nuevos, partiendo "
		"de x = 0. Para cuando todos los |Eⱼ| quedan por debajo de ε."
	),
	campos=(
		CampoDeEntrada(
			"sistema",
			"[A | b] =",
			TipoDeCampo.SISTEMA_DE_ECUACIONES,
			"3 -0.1 -0.2 | 7.85\n0.1 7 -0.3 | 19.3\n0.3 -0.2 10 | 71.4",
		),
		CampoDeEntrada(
			"reordenar",
			"Reordenar si A no es diagonalmente dominante",
			TipoDeCampo.CASILLA_DE_VERIFICACION,
			"si",
		),
	),
	ejecutar=ejecutar_gauss_seidel,
	columnas=armar_columnas,
	grafico=GraficoDeMetodo(TipoDeGrafico.CONVERGENCIA),
)
