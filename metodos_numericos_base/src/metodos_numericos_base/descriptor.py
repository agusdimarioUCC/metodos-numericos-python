"""Contrato declarativo que describe un método para la GUI unificada.

No importa tkinter ni matplotlib ni ningún método concreto: es la forma
de datos que metodos_numericos_gui usa para armar dinámicamente un panel
por método (campos, tabla de iteraciones, gráfico, resultado), y que
cada método completa en su propio `gui.py` sin escribir código de
interfaz.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

from metodos_numericos_base.iteracion import ReportarIteracion


class TipoDeCampo(Enum):
	"""Qué clase de widget necesita un campo de entrada en la GUI."""

	EXPRESION_MATEMATICA = auto()
	NUMERO = auto()
	TEXTO_MULTILINEA = auto()
	CASILLA_DE_VERIFICACION = auto()
	SISTEMA_DE_ECUACIONES = auto()
	TABLA_DE_PUNTOS = auto()
	SELECTOR = auto()


@dataclass(frozen=True)
class CampoDeEntrada:
	"""Un campo del panel de entradas de un método.

	`nombre` es la clave con la que el valor ya convertido llega al
	diccionario `valores` de la función `ejecutar` del método (ver
	`DescriptorDeMetodo.ejecutar`). `etiqueta` es el texto que ve el
	usuario, con la notación de la cátedra (`"a ="`, `"x₀ ="`).
	`cantidad_de_lineas` solo se usa para `TEXTO_MULTILINEA`. Para
	`SISTEMA_DE_ECUACIONES`, `valor_por_defecto` es texto con una
	ecuación por línea, coeficientes y término independiente separados
	por espacios, con un "|" opcional antes del último valor — se usa
	una única vez, para poblar la grilla de entradas con un sistema de
	ejemplo y para inferir su tamaño inicial. Para `TABLA_DE_PUNTOS`,
	`valor_por_defecto` es texto con un punto por línea, "x y" separados
	por un espacio — misma idea, para poblar la grilla de puntos con un
	ejemplo e inferir su cantidad inicial de filas. `opciones` solo se
	usa para `SELECTOR`: la lista fija que se muestra en el desplegable
	(`valor_por_defecto` debe ser una de ellas).
	"""

	nombre: str
	etiqueta: str
	tipo: TipoDeCampo
	valor_por_defecto: str = ""
	cantidad_de_lineas: int = 6
	opciones: tuple[str, ...] = ()


class FormatoDeColumna(Enum):
	"""Cómo se muestra el valor de una columna de la tabla de iteraciones."""

	NUMERO = auto()
	"""Número con la cantidad de decimales elegida y coma decimal."""

	SIGNO = auto()
	"""Solo el signo, como la columna f(a)·f(c) de bisección en los apuntes: `< 0`, `> 0`, `= 0`."""

	ENTERO = auto()
	"""Número entero sin decimales (el número de fila, i)."""


@dataclass(frozen=True)
class ColumnaDeTabla:
	"""Una columna de la tabla de iteraciones de un método.

	`clave` indica de dónde sale el valor de cada fila: `"numero"`,
	`"aproximacion"` o `"error"` leen los campos homónimos de
	`Iteracion`; cualquier otra clave se busca en `Iteracion.detalle`.
	`es_raiz` marca la columna de la respuesta: su celda en la última
	fila se resalta en ámbar, como la celda naranja de "RAÍZ" de los
	apuntes. `es_error` marca una columna de error: la primera celda por
	debajo de la tolerancia se resalta en verde.
	"""

	clave: str
	encabezado: str
	formato: FormatoDeColumna = FormatoDeColumna.NUMERO
	es_raiz: bool = False
	es_error: bool = False


COLUMNA_DE_NUMERO_DE_FILA = ColumnaDeTabla("numero", "i", FormatoDeColumna.ENTERO)
"""La columna `i` con la que empiezan todas las tablas de la cátedra."""


class TipoDeGrafico(Enum):
	"""Qué dibujo explica el método, como los gráficos de los apuntes."""

	INTERVALOS = auto()
	"""f(x) con los intervalos [a; b] que se van achicando (bisección, fig. 8)."""

	TELARANA = auto()
	"""g(x) contra y = x con el recorrido en telaraña de x_(i+1) = g(x_i) (punto fijo)."""

	TANGENTES = auto()
	"""f(x) con la recta tangente en cada x_i (Newton-Raphson)."""

	SECANTES = auto()
	"""f(x) con la recta secante por cada par x_(i-1), x_i (secante)."""

	CONVERGENCIA = auto()
	"""|E| de cada componente contra la iteración, en escala logarítmica (métodos vectoriales)."""

	DISPERSION_Y_AJUSTE = auto()
	"""Puntos (xᵢ, yᵢ) dispersos con la curva ajustada por mínimos cuadrados superpuesta (regresión lineal)."""


@dataclass(frozen=True)
class GraficoDeMetodo:
	"""El gráfico que acompaña a un método.

	`campo_de_la_funcion` es el `nombre` del `CampoDeEntrada` cuya
	expresión se dibuja como curva (`"funcion"`, `"funcion_g"`); `None`
	para gráficos que no dibujan una curva, como `CONVERGENCIA`.
	"""

	tipo: TipoDeGrafico
	campo_de_la_funcion: str | None = None


@dataclass(frozen=True)
class Verificacion:
	"""Un valor que el usuario puede usar para comprobar el resultado.

	Por ejemplo `f(raíz)` (que debería ser casi 0), o el lado izquierdo de
	una ecuación del sistema evaluado en la solución, con `esperado`
	igual a su término independiente.
	"""

	etiqueta: str
	valor: float
	esperado: float | None = None


@dataclass(frozen=True)
class MatrizDeResultado:
	"""Una matriz (o vector columna) para mostrar entre corchetes en el resultado.

	`es_resultado` la resalta en ámbar como la respuesta del método (el
	vector x en descomposición LU).
	"""

	nombre: str
	filas: tuple[tuple[float, ...], ...]
	es_resultado: bool = False


@dataclass(frozen=True)
class ResultadoDeMetodo:
	"""Lo que devuelve `DescriptorDeMetodo.ejecutar` al terminar un cálculo exitoso.

	Todo viaja sin formatear (floats crudos): la GUI decide la cantidad
	de decimales y el separador, y puede volver a formatear sin
	recalcular cuando el usuario cambia los decimales.

	`etiquetas_de_componentes` nombra cada posición de `valor` cuando es
	una tupla (por ejemplo `("a₀", "a₁")` en vez de los genéricos
	`x₁, x₂, …` que se usan si se deja vacía). `funcion_para_grafico` y
	`puntos_de_datos` son para métodos como la regresión lineal, cuya
	curva no viene de una expresión tipeada por el usuario sino que la
	calcula el propio método: `funcion_para_grafico` es la curva ya
	ajustada en el espacio original (y = f(x)) y `puntos_de_datos` son
	los (xᵢ, yᵢ) crudos a dispersar en el gráfico (ver
	`TipoDeGrafico.DISPERSION_Y_AJUSTE`).
	"""

	etiqueta_del_valor: str
	valor: float | tuple[float, ...]
	cantidad_de_iteraciones: int
	verificaciones: tuple[Verificacion, ...] = ()
	advertencias: tuple[str, ...] = ()
	matrices: tuple[MatrizDeResultado, ...] = ()
	etiquetas_de_componentes: tuple[str, ...] = ()
	funcion_para_grafico: Callable[[float], float] | None = None
	puntos_de_datos: tuple[tuple[float, float], ...] = ()


EjecutarMetodo = Callable[[dict[str, object], ReportarIteracion], ResultadoDeMetodo]
ArmarColumnas = Callable[[dict[str, object]], Sequence[ColumnaDeTabla]]


def columnas_fijas(*columnas: ColumnaDeTabla) -> ArmarColumnas:
	"""Envuelve columnas que no dependen de los datos en el callable que pide el descriptor."""
	return lambda valores: columnas


@dataclass(frozen=True)
class DescriptorDeMetodo:
	"""Todo lo que la GUI unificada necesita saber de un método, sin conocerlo.

	`ejecutar` recibe un diccionario `{nombre_del_campo: valor_ya_convertido}`
	(las expresiones matemáticas ya vienen envueltas en funciones evaluables,
	los números como float, el texto multilínea como string, las casillas
	como bool, los sistemas como `(filas, terminos_independientes)`) y un
	`reportar_iteracion` para informar el progreso; devuelve un
	`ResultadoDeMetodo` o lanza una excepción si algo salió mal. Si
	`usa_criterio_de_parada` es verdadero, la GUI agrega su propio grupo
	"Criterio de parada" y el diccionario trae además `"tolerancia"`
	(float) y `"maximo_iteraciones"` (int).

	`capitulo` agrupa los métodos en la barra lateral, con los nombres de
	los capítulos de los apuntes. `formula` es la fórmula recurrente que
	se muestra bajo el nombre del método. `columnas` arma las columnas de
	la tabla de iteraciones a partir de los mismos `valores` (un callable,
	para que un método vectorial pueda tener una columna por componente);
	`None` si el método no muestra tabla. `grafico` es `None` si no tiene
	gráfico: en ese caso, si el resultado trae `matrices`, se muestran en
	su lugar.
	"""

	nombre_para_mostrar: str
	capitulo: str
	formula: str
	descripcion: str
	campos: tuple[CampoDeEntrada, ...]
	ejecutar: EjecutarMetodo
	columnas: ArmarColumnas | None = None
	grafico: GraficoDeMetodo | None = None
	usa_criterio_de_parada: bool = True
