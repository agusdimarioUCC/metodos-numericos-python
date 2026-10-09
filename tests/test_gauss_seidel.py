import numpy as np
import pytest

from metodos_numericos.gauss_seidel import (
	NoConvergeError,
	es_diagonalmente_dominante,
	gauss_seidel,
	reordenar_para_dominancia_diagonal,
)


def test_resuelve_sistema_diagonalmente_dominante():
	matriz_coeficientes = [
		[10, 1, -2],
		[1, 12, 3],
		[2, -1, 15],
	]
	terminos_independientes = [27, 65, 45]

	x, iteraciones = gauss_seidel(matriz_coeficientes, terminos_independientes)

	assert iteraciones > 0
	np.testing.assert_allclose(np.array(matriz_coeficientes) @ x, terminos_independientes, atol=1e-2)


def test_es_diagonalmente_dominante_true():
	matriz_coeficientes = np.array([[10, 1, -2], [1, 12, 3], [2, -1, 15]])
	assert es_diagonalmente_dominante(matriz_coeficientes) is True


def test_es_diagonalmente_dominante_false():
	matriz_coeficientes = np.array([[1, 5], [5, 1]])
	assert es_diagonalmente_dominante(matriz_coeficientes) is False


def test_matriz_no_cuadrada_lanza_error():
	with pytest.raises(ValueError, match="cuadrada"):
		gauss_seidel([[1, 2, 3], [4, 5, 6]], [1, 2])


def test_dimension_terminos_independientes_incorrecta_lanza_error():
	with pytest.raises(ValueError, match=r"\(2,\)"):
		gauss_seidel([[1, 0], [0, 1]], [1, 2, 3])


def test_diagonal_con_cero_lanza_error():
	with pytest.raises(ValueError, match="diagonal"):
		gauss_seidel([[0, 1], [1, 1]], [1, 2])


def test_no_converge_lanza_error_con_maximo_iteraciones_bajo():
	matriz_coeficientes = [[10, 1, -2], [1, 12, 3], [2, -1, 15]]
	terminos_independientes = [27, 65, 45]
	with pytest.raises(NoConvergeError):
		gauss_seidel(matriz_coeficientes, terminos_independientes, maximo_iteraciones=0)


def test_acepta_aproximacion_inicial():
	matriz_coeficientes = [[10, 1, -2], [1, 12, 3], [2, -1, 15]]
	terminos_independientes = [27, 65, 45]

	x, _ = gauss_seidel(matriz_coeficientes, terminos_independientes, aproximacion_inicial=[1, 1, 1])
	np.testing.assert_allclose(np.array(matriz_coeficientes) @ x, terminos_independientes, atol=1e-2)


def test_reordenar_logra_dominancia_diagonal():
	matriz_coeficientes = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]
	terminos_independientes = [-51, 61, 8]

	matriz_reordenada, terminos_independientes_reordenados = reordenar_para_dominancia_diagonal(
		matriz_coeficientes, terminos_independientes
	)

	assert es_diagonalmente_dominante(matriz_reordenada) is True
	x, _ = gauss_seidel(matriz_reordenada, terminos_independientes_reordenados)
	np.testing.assert_allclose(np.array(matriz_coeficientes) @ x, terminos_independientes, atol=1e-2)


def test_reordenar_mantiene_las_mismas_ecuaciones():
	matriz_coeficientes = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]

	matriz_reordenada, _ = reordenar_para_dominancia_diagonal(matriz_coeficientes)

	filas_originales = {tuple(fila) for fila in matriz_coeficientes}
	filas_reordenadas = {tuple(fila) for fila in matriz_reordenada}
	assert filas_reordenadas == filas_originales


def test_reordenar_sin_terminos_independientes_devuelve_none():
	matriz_coeficientes = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]

	_, terminos_independientes_reordenados = reordenar_para_dominancia_diagonal(matriz_coeficientes)

	assert terminos_independientes_reordenados is None


def test_reordenar_matriz_no_cuadrada_lanza_error():
	with pytest.raises(ValueError, match="cuadrada"):
		reordenar_para_dominancia_diagonal([[1, 2, 3], [4, 5, 6]])
