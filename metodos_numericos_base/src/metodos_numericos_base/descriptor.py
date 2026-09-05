"""Contrato declarativo que describe un método para la GUI unificada.

No importa tkinter ni ningún método concreto: es la forma de datos que
metodos_numericos_gui usa para armar dinámicamente una pestaña por método,
y que cada método (biseccion, punto_fijo, newton_raphson, gauss_seidel)
completa en su propio `gui.py` sin escribir código de interfaz.
"""

from __future__ import annotations

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


@dataclass(frozen=True)
class CampoDeEntrada:
	"""Un campo del panel de entradas de un método.

	`nombre` es la clave con la que el valor ya convertido llega al
	diccionario `valores` de la función `ejecutar` del método (ver
	`DescriptorDeMetodo.ejecutar`). `etiqueta` es el texto que ve el
	usuario. `cantidad_de_lineas` solo se usa para `TEXTO_MULTILINEA`.
	Para `SISTEMA_DE_ECUACIONES`, `valor_por_defecto` es texto con el
	mismo formato que aceptaba `TEXTO_MULTILINEA` (una ecuación por
	línea, coeficientes y término independiente separados por espacios,
	con un "|" opcional antes del último valor) — se usa una única vez,
	para poblar la grilla de entradas con un sistema de ejemplo y para
	inferir su tamaño inicial.
	"""

	nombre: str
	etiqueta: str
	tipo: TipoDeCampo
	valor_por_defecto: str = ""
	cantidad_de_lineas: int = 6


@dataclass(frozen=True)
class ResultadoDeMetodo:
	"""Lo que devuelve `DescriptorDeMetodo.ejecutar` al terminar un cálculo exitoso."""

	etiqueta_del_valor: str
	valor_formateado: str
	cantidad_de_iteraciones: int
	lineas_de_verificacion: tuple[str, ...] = ()
	advertencias: tuple[str, ...] = ()


EjecutarMetodo = Callable[[dict[str, object], ReportarIteracion], ResultadoDeMetodo]


@dataclass(frozen=True)
class DescriptorDeMetodo:
	"""Todo lo que la GUI unificada necesita saber de un método, sin conocerlo.

	`ejecutar` recibe un diccionario `{nombre_del_campo: valor_ya_convertido}`
	(las expresiones matemáticas ya vienen envueltas en funciones evaluables,
	los números como float, el texto multilínea como string, las casillas
	como bool) y un `reportar_iteracion` para informar el progreso; devuelve
	un `ResultadoDeMetodo` o lanza una excepción si algo salió mal.
	"""

	nombre_para_mostrar: str
	descripcion: str
	campos: tuple[CampoDeEntrada, ...]
	ejecutar: EjecutarMetodo
	encabezado_de_aproximacion: str = "Aproximación"
