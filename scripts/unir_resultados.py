"""Une los resultados de cada experimento de réplicas en una sola carpeta.

Cada experimento de AnyLogic se corrió por separado y sus CSV se guardaron en una
subcarpeta de Resultados/. Este script junta todos los resultados_corridas.csv y
resultados_semanas.csv en Resultados/consolidado/, que es lo que lee
analizar_resultados.py:

    py -3 scripts/unir_resultados.py
    py -3 scripts/analizar_resultados.py --resultados Resultados/consolidado
"""
from pathlib import Path
import sys

raiz = Path(__file__).resolve().parent.parent
resultados = raiz / "Resultados"
destino = resultados / "consolidado"
destino.mkdir(exist_ok=True)

for nombre in ("resultados_corridas.csv", "resultados_semanas.csv"):
    encabezado, filas = None, []
    for carpeta in sorted(p for p in resultados.iterdir() if p.is_dir() and p != destino):
        archivo = carpeta / nombre
        if not archivo.exists():
            continue
        lineas = archivo.read_text(encoding="utf-8-sig").splitlines()
        if encabezado is None:
            encabezado = lineas[0]
        elif lineas[0] != encabezado:
            sys.exit(f"{archivo}: el encabezado no coincide con el de los demás archivos")
        nuevas = [l for l in lineas[1:] if l.strip()]
        filas += nuevas
        print(f"{carpeta.name}: {len(nuevas)} filas de {nombre}")
    (destino / nombre).write_text(encabezado + "\n" + "\n".join(filas) + "\n", encoding="utf-8")
    print(f"-> {destino / nombre}: {len(filas)} filas\n")
