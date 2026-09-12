"""Descriptor de descomposición LU para la GUI unificada de métodos numéricos."""

from __future__ import annotations

import numpy as np
from metodos_numericos_base import (
	CampoDeEntrada,
	DescriptorDeMetodo,
	MatrizDeResultado,
	ReportarIteracion,
	ResultadoDeMetodo,
	TipoDeCampo,
	Verificacion,
)

from descomposicion_lu import descomponer_lu, descomposicion_lu, sustitucion_adelante

UMBRAL_MAL_CONDICIONADO = 100
"""Cond[A] por encima de esto se reporta como mal condicionado.

No hay un valor fijo en el libro (sección 10.3): solo se indica que un
número de condición "considerablemente mayor" a la unidad es señal de mal
condicionamiento. 100 es un umbral arbitrario pero razonable para avisar al
usuario sin generar falsos positivos en sistemas normales.
"""


def _como_filas(matriz: np.ndarray) -> tuple[tuple[float, ...], ...]:
	return tuple(tuple(float(valor) for valor in fila) for fila in matriz)


def _como_columna(vector: np.ndarray) -> tuple[tuple[float, ...], ...]:
	return tuple((float(valor),) for valor in vector)


def ejecutar_descomposicion_lu(
		valores: dict[str, object], reportar_iteracion: ReportarIteracion
) -> ResultadoDeMetodo:
	filas, terminos = valores["sistema"]
	matriz_coeficientes = np.array(filas, dtype=np.float64)
	terminos_independientes = np.array(terminos, dtype=np.float64)

	# La tabla de iteraciones no se muestra para LU (es un método directo):
	# el paso a paso que importa son las matrices L, U, y, x de los apuntes.
	x, inversa, condicion, _ = descomposicion_lu(matriz_coeficientes, terminos_independientes)
	triangular_inferior, triangular_superior = descomponer_lu(matriz_coeficientes)
	vector_intermedio = sustitucion_adelante(triangular_inferior, terminos_independientes)

	lado_izquierdo = matriz_coeficientes @ x
	verificaciones = [Verificacion("Cond[A]", condicion)]
	verificaciones.extend(
		Verificacion(f"Ecuación {numero}", float(valor), esperado=float(termino))
		for numero, (valor, termino) in enumerate(zip(lado_izquierdo, terminos_independientes), start=1)
	)

	advertencias: list[str] = []
	if condicion > UMBRAL_MAL_CONDICIONADO:
		advertencias.append(
			f"Cond[A] = {condicion:.2f} es mucho mayor que 1: el sistema puede estar mal "
			"condicionado y la solución ser sensible a pequeños cambios en A o b."
		)

	return ResultadoDeMetodo(
		etiqueta_del_valor="Solución",
		valor=tuple(float(componente) for componente in x),
		cantidad_de_iteraciones=0,
		verificaciones=tuple(verificaciones),
		advertencias=tuple(advertencias),
		matrices=(
			MatrizDeResultado("L", _como_filas(triangular_inferior)),
			MatrizDeResultado("U", _como_filas(triangular_superior)),
			MatrizDeResultado("y", _como_columna(vector_intermedio)),
			MatrizDeResultado("x", _como_columna(x), es_resultado=True),
			MatrizDeResultado("A⁻¹", _como_filas(inversa)),
		),
	)


DESCRIPTOR = DescriptorDeMetodo(
	nombre_para_mostrar="Descomposición LU",
	capitulo="Sistemas de ecuaciones lineales",
	formula="[L][U][x] = [b]",
	descripcion=(
		"Factoriza A = LU con la eliminación de Gauss, resuelve L·y = b hacia adelante y "
		"U·x = y hacia atrás. También calcula A⁻¹ y el número de condición."
	),
	campos=(
		CampoDeEntrada(
			"sistema",
			"[A | b] =",
			TipoDeCampo.SISTEMA_DE_ECUACIONES,
			"3 -0.1 -0.2 | 7.85\n0.1 7 -0.3 | 19.3\n0.3 -0.2 10 | 71.4",
		),
	),
	ejecutar=ejecutar_descomposicion_lu,
	usa_criterio_de_parada=False,
)
