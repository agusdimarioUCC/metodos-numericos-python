"""Formato de números como en los apuntes de la cátedra: coma decimal, decimales fijos.

No importa tkinter: lo usa la GUI, pero es texto puro y se puede probar
o reusar sin abrir ninguna ventana.
"""

from __future__ import annotations

import math

SIGNO_MENOS = "−"
"""El signo menos tipográfico (−), más legible en tablas que el guion (-)."""

_SUPERINDICES = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _con_coma_y_menos(texto: str) -> str:
	return texto.replace(".", ",").replace("-", SIGNO_MENOS)


def formatear_numero(valor: float, decimales: int = 4) -> str:
	"""Formatea `valor` con `decimales` fijos y coma decimal: `0,5665`, `−1,5672`.

	Un valor que redondea a cero se muestra sin signo (`0,0000`, nunca
	`−0,0000`). Infinito y NaN se muestran como `∞`/`−∞` y `—`.
	"""
	if math.isnan(valor):
		return "—"
	if math.isinf(valor):
		return "∞" if valor > 0 else f"{SIGNO_MENOS}∞"
	texto = f"{valor:.{decimales}f}"
	if float(texto) == 0:
		texto = texto.lstrip("-")
	return _con_coma_y_menos(texto)


def formatear_numero_legible(valor: float, decimales: int = 4) -> str:
	"""Como `formatear_numero`, pero pasa a notación científica si los decimales no alcanzan.

	Pensado para verificaciones como `f(raíz)`, donde un `0,0000` esconde
	si el valor es 1e-5 o 1e-15: un valor distinto de cero que no se ve
	con `decimales` fijos (o uno muy grande) se muestra como
	`1,23 × 10⁻⁹`.
	"""
	if valor != 0 and math.isfinite(valor):
		magnitud = abs(valor)
		if magnitud < 0.5 * 10.0**-decimales or magnitud >= 1e7:
			exponente = math.floor(math.log10(magnitud))
			mantisa = valor / 10.0**exponente
			if round(abs(mantisa), 2) >= 10:
				mantisa /= 10
				exponente += 1
			return f"{_con_coma_y_menos(f'{mantisa:.2f}')} × 10{str(exponente).translate(_SUPERINDICES)}"
	return formatear_numero(valor, decimales)


def formatear_valor_corto(valor: float) -> str:
	"""El número con los dígitos justos, como lo escribiría una persona: `0,001`, `10⁻⁶`, `2,5 × 10⁻⁸`.

	Pensado para parámetros que eligió el usuario, como ε, donde `0,0010`
	(decimales fijos) se lee peor que `0,001`.
	"""
	texto = f"{valor:g}"
	if "e" not in texto:
		return _con_coma_y_menos(texto)
	mantisa, exponente = texto.split("e")
	potencia = "10" + str(int(exponente)).translate(_SUPERINDICES)
	if mantisa in ("1", "-1"):
		return (SIGNO_MENOS if mantisa.startswith("-") else "") + potencia
	return f"{_con_coma_y_menos(mantisa)} × {potencia}"


def formatear_signo(valor: float) -> str:
	"""Muestra solo el signo de `valor`, como la columna f(a)·f(c) de bisección en los apuntes."""
	if valor < 0:
		return "< 0"
	if valor > 0:
		return "> 0"
	return "= 0"


def formatear_valor_editable(valor: float) -> str:
	"""Formatea un número para precargarlo en un campo editable: `12` en vez de `12.0`, `0,4` en vez de `0.4`."""
	# 15 cifras: `:g` solo deja 6 y cada redimensionado de la grilla recortaba lo que escribió el usuario.
	return f"{valor:.15g}".replace(".", ",")


def leer_numero(texto: str) -> float:
	"""Convierte lo que el usuario escribió en un campo numérico, con coma o punto decimal.

	Acepta `0,4`, `0.4`, `1e-3`, `−2` (con el signo menos tipográfico).

	Raises:
		ValueError: Si el texto no es un número.
	"""
	normalizado = texto.strip().replace(SIGNO_MENOS, "-").replace(",", ".")
	if not normalizado:
		raise ValueError("está vacío")
	try:
		return float(normalizado)
	except ValueError:
		raise ValueError(f"«{texto.strip()}» no es un número") from None


def subindice(numero: int) -> str:
	"""Devuelve `numero` escrito con dígitos de subíndice: `subindice(12)` → `₁₂`."""
	return str(numero).translate(_SUBINDICES)
