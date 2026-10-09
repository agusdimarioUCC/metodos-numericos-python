"""Registro explícito de los métodos disponibles en la GUI unificada.

Registro explícito (importar cada descriptor a mano) en vez de
descubrimiento automático por entry points: agregar un método exige
acordarse de tocar este archivo, pero si te olvidás el método
simplemente no aparece — sin la degradación silenciosa que traería un
`uv sync` corrido desde el directorio de un solo miembro con
descubrimiento automático.

Para agregar un método nuevo: importar su `DESCRIPTOR` acá y sumarlo a
`METODOS_DISPONIBLES` en la posición donde se quiera verlo en la barra
lateral, junto a los demás métodos de su mismo `capitulo` (la barra
escribe un encabezado cada vez que el capítulo cambia respecto del
método anterior, así que un método separado de los de su capítulo
repite el encabezado).
"""

from __future__ import annotations

from metodos_numericos.biseccion.gui import DESCRIPTOR as descriptor_de_biseccion
from metodos_numericos.descomposicion_lu.gui import DESCRIPTOR as descriptor_de_descomposicion_lu
from metodos_numericos.gauss_seidel.gui import DESCRIPTOR as descriptor_de_gauss_seidel
from metodos_numericos.interpolacion_newton.gui import DESCRIPTOR as descriptor_de_interpolacion_newton
from metodos_numericos.interpolacion_lagrange.gui import DESCRIPTOR as descriptor_de_interpolacion_lagrange
from metodos_numericos import DescriptorDeMetodo
from metodos_numericos.newton_raphson.gui import DESCRIPTOR as descriptor_de_newton_raphson
from metodos_numericos.punto_fijo.gui import DESCRIPTOR as descriptor_de_punto_fijo
from metodos_numericos.regresion_lineal.gui import DESCRIPTOR as descriptor_de_regresion_lineal
from metodos_numericos.secante.gui import DESCRIPTOR as descriptor_de_secante
from metodos_numericos.trazadoras_cubicas.gui import DESCRIPTOR as descriptor_de_trazadoras_cubicas

METODOS_DISPONIBLES: tuple[DescriptorDeMetodo, ...] = (
	descriptor_de_biseccion,
	descriptor_de_punto_fijo,
	descriptor_de_newton_raphson,
	descriptor_de_secante,
	descriptor_de_gauss_seidel,
	descriptor_de_descomposicion_lu,
	descriptor_de_regresion_lineal,
	descriptor_de_interpolacion_newton,
	descriptor_de_interpolacion_lagrange,
	descriptor_de_trazadoras_cubicas,
)
