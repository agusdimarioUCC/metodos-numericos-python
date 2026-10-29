"""Maneja la GUI de métodos numéricos sin mano humana: elige método, carga campos, calcula y captura.

Uso (desde metodos-numericos-python/):
	uv run python .claude/skills/run-metodos-numericos/driver.py --listar
	uv run python .claude/skills/run-metodos-numericos/driver.py "Bisección" a=1 b=2 --salida captura.png
Los campos son los `nombre` de cada CampoDeEntrada (más `tolerancia` y `maximo_iteraciones`).
"""

import argparse

from PIL import ImageGrab

from metodos_numericos.gui import VentanaMetodosNumericos
from metodos_numericos.registro import METODOS_DISPONIBLES


def textos_de(widget):
	"""Recorre el árbol de widgets y junta el texto de las etiquetas."""
	encontrados = []
	if "text" in widget.keys() and str(widget.cget("text")).strip():
		encontrados.append(str(widget.cget("text")))
	for hijo in widget.winfo_children():
		encontrados += textos_de(hijo)
	return encontrados


def principal():
	analizador = argparse.ArgumentParser()
	analizador.add_argument("metodo", nargs="?", help="parte del nombre del método (p.ej. Secante)")
	analizador.add_argument("campos", nargs="*", help="nombre=valor")
	analizador.add_argument("--listar", action="store_true")
	analizador.add_argument("--salida", default="captura.png")
	argumentos = analizador.parse_args()

	if argumentos.listar or not argumentos.metodo:
		for descriptor in METODOS_DISPONIBLES:
			print(descriptor.nombre_para_mostrar, [campo.nombre for campo in descriptor.campos], sep=" -> ")
		return

	indice = next((i for i, d in enumerate(METODOS_DISPONIBLES) if argumentos.metodo.lower() in d.nombre_para_mostrar.lower()), None)
	if indice is None:
		raise SystemExit(f"Ningún método contiene {argumentos.metodo!r}; ver --listar")
	ventana = VentanaMetodosNumericos(METODOS_DISPONIBLES)
	ventana.attributes("-topmost", True)  # ImageGrab captura la pantalla: sin esto sale lo que tape a la ventana
	ventana.lift()
	ventana.mostrar_metodo(indice)
	panel = ventana.paneles[indice]
	for asignacion in argumentos.campos:
		nombre, valor = asignacion.split("=", 1)
		if nombre not in panel._entradas:
			ventana.destroy()
			raise SystemExit(f"{nombre!r} no es una entrada de texto; se puede pisar: {', '.join(panel._entradas)}")
		entrada = panel._entradas[nombre]
		entrada.delete(0, "end")
		entrada.insert(0, valor)
	panel._calcular()
	ventana.update()
	ventana.after(800, ventana.quit)  # deja dibujar el gráfico y la tabla
	ventana.mainloop()
	print("RESULTADO:", " | ".join(textos_de(panel._bloque_de_resultado)))
	caja = (ventana.winfo_rootx(), ventana.winfo_rooty(), ventana.winfo_rootx() + ventana.winfo_width(), ventana.winfo_rooty() + ventana.winfo_height())
	ImageGrab.grab(bbox=caja, all_screens=True).save(argumentos.salida)
	print("CAPTURA:", argumentos.salida)
	ventana.destroy()


principal()
