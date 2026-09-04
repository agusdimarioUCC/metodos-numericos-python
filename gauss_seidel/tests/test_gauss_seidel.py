import numpy as np
import pytest

from gauss_seidel import (
    NoConvergeError,
    es_diagonalmente_dominante,
    gauss_seidel,
    leer_matriz_desde_terminal,
    reordenar_para_dominancia_diagonal,
    resolver_desde_terminal,
)


def test_resuelve_sistema_diagonalmente_dominante():
    a = [
        [10, 1, -2],
        [1, 12, 3],
        [2, -1, 15],
    ]
    b = [27, 65, 45]

    x, iteraciones = gauss_seidel(a, b)

    assert iteraciones > 0
    np.testing.assert_allclose(np.array(a) @ x, b, atol=1e-2)


def test_es_diagonalmente_dominante_true():
    a = np.array([[10, 1, -2], [1, 12, 3], [2, -1, 15]])
    assert es_diagonalmente_dominante(a) is True


def test_es_diagonalmente_dominante_false():
    a = np.array([[1, 5], [5, 1]])
    assert es_diagonalmente_dominante(a) is False


def test_matriz_no_cuadrada_lanza_error():
    with pytest.raises(ValueError, match="cuadrada"):
        gauss_seidel([[1, 2, 3], [4, 5, 6]], [1, 2])


def test_dimension_b_incorrecta_lanza_error():
    with pytest.raises(ValueError, match=r"\(2,\)"):
        gauss_seidel([[1, 0], [0, 1]], [1, 2, 3])


def test_diagonal_con_cero_lanza_error():
    with pytest.raises(ValueError, match="diagonal"):
        gauss_seidel([[0, 1], [1, 1]], [1, 2])


def test_no_converge_lanza_error_con_max_iter_bajo():
    a = [[10, 1, -2], [1, 12, 3], [2, -1, 15]]
    b = [27, 65, 45]
    with pytest.raises(NoConvergeError):
        gauss_seidel(a, b, max_iter=0)


def test_acepta_aproximacion_inicial():
    a = [[10, 1, -2], [1, 12, 3], [2, -1, 15]]
    b = [27, 65, 45]

    x, _ = gauss_seidel(a, b, x0=[1, 1, 1])
    np.testing.assert_allclose(np.array(a) @ x, b, atol=1e-2)


def test_reordenar_logra_dominancia_diagonal():
    a = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]
    b = [-51, 61, 8]

    a_reordenada, b_reordenada = reordenar_para_dominancia_diagonal(a, b)

    assert es_diagonalmente_dominante(a_reordenada) is True
    x, _ = gauss_seidel(a_reordenada, b_reordenada)
    np.testing.assert_allclose(np.array(a) @ x, b, atol=1e-2)


def test_reordenar_mantiene_las_mismas_ecuaciones():
    a = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]

    a_reordenada, _ = reordenar_para_dominancia_diagonal(a)

    filas_originales = {tuple(fila) for fila in a}
    filas_reordenadas = {tuple(fila) for fila in a_reordenada}
    assert filas_reordenadas == filas_originales


def test_reordenar_sin_b_devuelve_none():
    a = [[1, 7, -3], [4, -4, 9], [12, -1, 3]]

    _, b_reordenada = reordenar_para_dominancia_diagonal(a)

    assert b_reordenada is None


def test_reordenar_matriz_no_cuadrada_lanza_error():
    with pytest.raises(ValueError, match="cuadrada"):
        reordenar_para_dominancia_diagonal([[1, 2, 3], [4, 5, 6]])


def test_leer_matriz_desde_terminal_construye_a_y_b():
    respuestas = iter(["2", "1 2", "5", "3 4", "6"])

    a, b = leer_matriz_desde_terminal(entrada=lambda _: next(respuestas))

    np.testing.assert_array_equal(a, [[1, 2], [3, 4]])
    np.testing.assert_array_equal(b, [5, 6])


def test_leer_matriz_desde_terminal_usa_n_dado_sin_preguntarlo():
    respuestas = iter(["1 2", "5", "3 4", "6"])

    a, b = leer_matriz_desde_terminal(n=2, entrada=lambda _: next(respuestas))

    np.testing.assert_array_equal(a, [[1, 2], [3, 4]])
    np.testing.assert_array_equal(b, [5, 6])


def test_leer_matriz_desde_terminal_reintenta_fila_mal_formada():
    respuestas = iter(["1 2", "1", "5"])

    a, b = leer_matriz_desde_terminal(n=1, entrada=lambda _: next(respuestas))

    np.testing.assert_array_equal(a, [[1]])
    np.testing.assert_array_equal(b, [5])


def test_resolver_desde_terminal_permite_resolver_varios_sistemas(capsys):
    respuestas = iter(["1", "5", "10", "s", "1", "2", "4", "n"])

    resolver_desde_terminal(entrada=lambda _: next(respuestas))

    salida = capsys.readouterr().out
    assert salida.count("Solución:") == 2


def test_resolver_desde_terminal_se_detiene_si_no_se_pide_otro(capsys):
    respuestas = iter(["1", "5", "10", "n"])

    resolver_desde_terminal(entrada=lambda _: next(respuestas))

    salida = capsys.readouterr().out
    assert salida.count("Solución:") == 1
