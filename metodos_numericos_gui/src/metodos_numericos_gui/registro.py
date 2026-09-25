"""Registro explícito de los métodos disponibles en la GUI unificada.

Registro explícito (importar cada descriptor a mano) en vez de
descubrimiento automático por entry points: agregar un método exige
acordarse de tocar este archivo, pero si te olvidás el método
simplemente no aparece — sin la degradación silenciosa que traería un
`uv sync` corrido desde el directorio de un solo miembro con
descubrimiento automático.

Para agregar un método nuevo: importar su `DESCRIPTOR` acá y sumarlo a
`METODOS_DISPONIBLES`, en la posición donde se quiera la pestaña.
"""

from __future__ import annotations

from biseccion.gui import DESCRIPTOR as descriptor_de_biseccion
from descomposicion_lu.gui import DESCRIPTOR as descriptor_de_descomposicion_lu
from gauss_seidel.gui import DESCRIPTOR as descriptor_de_gauss_seidel
from metodos_numericos_base import DescriptorDeMetodo
from newton_raphson.gui import DESCRIPTOR as descriptor_de_newton_raphson
from punto_fijo.gui import DESCRIPTOR as descriptor_de_punto_fijo
from regresion_lineal.gui import DESCRIPTOR as descriptor_de_regresion_lineal
from secante.gui import DESCRIPTOR as descriptor_de_secante

METODOS_DISPONIBLES: tuple[DescriptorDeMetodo, ...] = (
	descriptor_de_biseccion,
	descriptor_de_punto_fijo,
	descriptor_de_newton_raphson,
	descriptor_de_secante,
	descriptor_de_gauss_seidel,
	descriptor_de_descomposicion_lu,
	descriptor_de_regresion_lineal,
)
