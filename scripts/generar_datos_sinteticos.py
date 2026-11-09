"""Genera datos históricos SINTÉTICOS de la planta KRETZ (no son datos reales).

Sirven para probar el modelo y armar la comparación con "la realidad" mientras no
lleguen los datos reales de KRETZ. Escribe en Datos/Sinteticos/:

- empleados.csv                 dotación (41 empleados) con especialidad y línea
- planilla_ausencias.csv        una fila por ausencia (legajo, fecha, motivo)
- resumen_ausentismo.csv        tasa de ausencia por especialidad y día de la semana
- ordenes_fabricacion.csv       OF diaria por modelo: pedido, producido en el turno, faltante
- cumplimiento_diario.csv       totales por jornada, ausentes y observaciones
- horas_extra_fin_de_semana.csv recuperación semanal: horas, horas-hombre y costo

Los números salen de un modelo simple de capacidad por especialidad (minutos
disponibles de los presentes contra minutos que pide la OF), con tiempos de SAP,
ausentismo y variabilidad. La semilla es fija: correr el script de nuevo da los
mismos archivos.

    py -3 scripts/generar_datos_sinteticos.py
"""

from datetime import date, timedelta
from pathlib import Path
import csv
import math
import random

SEMILLA = 2026
INICIO = date(2026, 3, 2)       # lunes
SEMANAS = 26                    # marzo a agosto de 2026
TURNO_MIN = 480
VALOR_HORA = 6500               # $/h con cargas (mismo supuesto que el modelo)
RECARGO = 2
PROB_AUSENCIA = 0.06
EFICIENCIA = 0.93               # fracción del turno que rinde (caminatas, esperas, arranque y cierre)
FACTOR_DIA = [1.25, 1.0, 0.9, 0.9, 1.1]          # lunes a viernes, igual que el modelo
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
FERIADOS = {date(2026, 3, 23), date(2026, 3, 24), date(2026, 4, 2), date(2026, 4, 3), date(2026, 5, 1),
            date(2026, 5, 25), date(2026, 6, 15), date(2026, 7, 9), date(2026, 7, 10), date(2026, 8, 17)}

MODELOS = ["AILA 30KG", "REPORT LT", "NOVEL ECO", "LURA", "AURA"]
ESPECIALIDADES = ["Armador", "Ajustador", "Controlador", "Embalador"]
# Minutos por unidad y especialidad (Tabla 1 de SAP). El retiro en depósito (2 min) más
# ~1,5 min de caminata se carga a quien hace el primer puesto: Armador, o Ajustador en LURA.
MIN_POR_UNIDAD = {
    "AILA 30KG": {"Armador": 25 + 3.5, "Ajustador": 5, "Controlador": 4.5, "Embalador": 10},
    "REPORT LT": {"Armador": 11 + 3.5, "Ajustador": 12, "Controlador": 12, "Embalador": 12},
    "NOVEL ECO": {"Armador": 3.15 + 3.5, "Ajustador": 3, "Controlador": 2.25, "Embalador": 3},
    "LURA": {"Armador": 0, "Ajustador": 4 + 3.5, "Controlador": 3.15, "Embalador": 3.15},
    "AURA": {"Armador": 3.15 + 3.5, "Ajustador": 3, "Controlador": 2.5, "Embalador": 2.88},
}
# Mezclas típicas de OF (unidades por día), cerca de las OF de ejemplo del modelo
ESCALA_OF = 1.15               # OF un 15 % más grandes, igual que la OF de ejemplo del modelo (307 u/día)
MEZCLAS = [(n, [c * ESCALA_OF for c in base]) for n, base in [
    ("Equilibrada", [34, 46, 72, 46, 60]),
    ("Mucha REPORT LT", [20, 64, 48, 34, 46]),
    ("Equipos cortos", [40, 28, 92, 60, 72]),
]]
MOTIVOS = [("Enfermedad", 0.50), ("Razones particulares", 0.20), ("Trámite", 0.10),
           ("Licencia por examen", 0.05), ("Sin aviso", 0.15)]
EVENTOS = ["Demora en la entrega de materiales al rack", "Corte de energía", "Falla de la impresora de etiquetas",
           "Reunión de seguridad e higiene", "Falta de componentes de un proveedor"]


def num(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


def escribir(ruta, encabezado, filas):
    with ruta.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(encabezado)
        w.writerows(filas)


def crear_empleados(rng):
    empleados = []
    legajo = 1001
    def alta(esp, linea, puesto):
        nonlocal legajo
        # Propensión individual a faltar: la mayoría cerca de la media y unos pocos más altos
        tasa = min(0.25, rng.gammavariate(2.0, PROB_AUSENCIA / 2.0))
        empleados.append({"legajo": legajo, "especialidad": esp, "linea": linea, "puesto": puesto, "tasa": tasa})
        legajo += 1
    for l in range(1, 5):
        for p in range(1, 5):
            alta("Armador", f"Armado {l}", f"Armado {p}")
        alta("Ajustador", f"Armado {l}", "Ajuste")
    for l in range(1, 3):
        for p in range(1, 3):
            alta("Controlador", f"Control Final {l}", f"Control {p}")
        for p in range(1, 4):
            alta("Embalador", f"Control Final {l}", f"Embalaje {p}")
    for p in range(1, 11):
        alta("Depósito", "Depósito", f"Depósito {p}")
    alta("Inspector de calidad", "Depósito", "Calidad")
    return empleados


def motivo(rng):
    r, acum = rng.random(), 0
    for m, p in MOTIVOS:
        acum += p
        if r < acum:
            return m
    return MOTIVOS[-1][0]


def main():
    rng = random.Random(SEMILLA)
    salida = Path(__file__).resolve().parent.parent / "Datos" / "Sinteticos"
    salida.mkdir(parents=True, exist_ok=True)

    empleados = crear_empleados(rng)
    linea = [e for e in empleados if e["especialidad"] in ESPECIALIDADES]

    ausencias, of_filas, diario, semanal = [], [], [], []
    enfermos = {}                      # legajo -> días de enfermedad que le quedan
    conteo = {}                        # (especialidad, día) -> [ausencias, días-persona]
    n_of = 0

    for s in range(SEMANAS):
        lunes = INICIO + timedelta(weeks=s)
        falt_semana = {m: 0 for m in MODELOS}
        pendiente = {m: 0 for m in MODELOS}   # unidades atrasadas: se hacen primero al día siguiente
        pedido_semana = producido_semana = 0
        for d in range(5):
            fecha = lunes + timedelta(days=d)
            if fecha in FERIADOS:
                continue
            # --- Asistencia ---
            ausentes = set()
            for e in empleados:
                leg = e["legajo"]
                if enfermos.get(leg, 0) > 0:
                    enfermos[leg] -= 1
                    ausentes.add(leg)
                    ausencias.append([leg, e["especialidad"], e["linea"], fecha.isoformat(), DIAS[d], "Enfermedad", 1])
                elif rng.random() < min(0.9, e["tasa"] * FACTOR_DIA[d] * 0.75):
                    mot = motivo(rng)
                    if mot == "Enfermedad":     # una enfermedad suele durar más de un día
                        enfermos[leg] = min(4, int(rng.expovariate(1 / 0.8)))
                    ausentes.add(leg)
                    ausencias.append([leg, e["especialidad"], e["linea"], fecha.isoformat(), DIAS[d], mot, 1])
                c = conteo.setdefault((e["especialidad"], d), [0, 0])
                c[0] += leg in ausentes
                c[1] += 1

            # --- OF del día ---
            n_of += 1
            nombre_mezcla, base = rng.choice(MEZCLAS)
            pedido = {m: max(0, 2 * round(b * rng.gauss(1, 0.10) / 2)) for m, b in zip(MODELOS, base)}
            if rng.random() < 0.08:          # a veces un modelo no entra en la OF del día
                pedido[rng.choice(MODELOS)] = 0

            # --- Capacidad por especialidad ---
            presentes = {esp: sum(1 for e in linea if e["especialidad"] == esp and e["legajo"] not in ausentes)
                         for esp in ESPECIALIDADES}
            eficiencia = rng.gauss(EFICIENCIA, 0.02)       # caminatas, esperas y arranque/cierre de turno
            variab = rng.gauss(1.0, 0.10)            # tiempos reales frente a SAP
            evento = ""
            if rng.random() < 0.04:
                evento = rng.choice(EVENTOS)
                eficiencia *= rng.uniform(0.80, 0.92)
            ratios = {}
            for esp in ESPECIALIDADES:
                carga = sum((pedido[m] + pendiente[m]) * MIN_POR_UNIDAD[m][esp] for m in MODELOS) * variab
                personas = presentes[esp]
                # Sin cobertura entre especialidades (igual que el escenario actual del modelo): si falta un
                # ajustador, otro ajustador reparte su tiempo entre dos líneas y la capacidad de ajuste baja
                capacidad = personas * TURNO_MIN * eficiencia
                ratios[esp] = capacidad / carga if carga else math.inf
            cuello = min(ratios, key=ratios.get)
            r = min(1.0, ratios[cuello])

            # --- Producción en el turno y faltante por modelo ---
            # Primero se terminan las unidades atrasadas del día anterior; lo que no entra en el
            # turno queda pendiente y son siempre unidades de la OF del día.
            atrasadas = sum(pendiente.values())
            perdido = sum((pedido[m] + pendiente[m]) * MIN_POR_UNIDAD[m][cuello] for m in MODELOS) * (1 - r)
            pesos = {m: pedido[m] * MIN_POR_UNIDAD[m][cuello] * rng.gammavariate(2, 0.5) for m in MODELOS}
            total_p = sum(pesos.values()) or 1
            faltante = {}
            for m in MODELOS:
                t = MIN_POR_UNIDAD[m][cuello]
                faltante[m] = 0 if r >= 1 or t == 0 else min(pedido[m], round(perdido * pesos[m] / total_p / t))
            if r >= 1 and rng.random() < 0.06:        # unidades que quedan en proceso al cierre
                m = rng.choice([m for m in MODELOS if pedido[m]])
                faltante[m] = min(pedido[m], rng.randint(1, 3))
            pendiente = dict(faltante)

            of_id = f"OF-2026-{n_of:04d}"
            tot_ped = sum(pedido.values())
            tot_falt = sum(faltante.values())
            for m in MODELOS:
                if pedido[m] == 0:
                    continue
                prod = pedido[m] - faltante[m]
                of_filas.append([of_id, fecha.isoformat(), DIAS[d], m, pedido[m], prod, faltante[m],
                                 num(100 * prod / pedido[m], 1), "Sí" if faltante[m] == 0 else "No"])
            aus_linea = sum(1 for e in linea if e["legajo"] in ausentes)
            diario.append([of_id, fecha.isoformat(), DIAS[d], nombre_mezcla, tot_ped, tot_ped - tot_falt, tot_falt,
                           num(100 * (tot_ped - tot_falt) / tot_ped, 1), "Sí" if tot_falt == 0 else "No",
                           len(ausentes), aus_linea, presentes["Ajustador"], presentes["Controlador"],
                           cuello if tot_falt else "", atrasadas, evento])
            pedido_semana += tot_ped
            producido_semana += tot_ped - tot_falt

        # --- Recuperación de fin de semana: lo que sigue pendiente al cierre del viernes ---
        falt_semana = pendiente
        falt_total = sum(falt_semana.values())
        sabado = lunes + timedelta(days=5)
        if falt_total == 0:
            semanal.append([s + 1, sabado.isoformat(), pedido_semana, producido_semana, 0, 0, num(0, 1), 0, 0])
            continue
        minutos_trabajo = sum(falt_semana[m] * sum(MIN_POR_UNIDAD[m].values()) for m in MODELOS)
        convocados = max(3, min(12, math.ceil(falt_total / 4)))
        asisten = max(1, sum(1 for _ in range(convocados) if rng.random() > 0.10))
        horas = minutos_trabajo / (asisten * 60 * rng.gauss(0.95, 0.04))
        horas = max(4.0, math.ceil(horas * 2) / 2)    # se convoca por un mínimo de 4 h
        hh = horas * asisten
        semanal.append([s + 1, sabado.isoformat(), pedido_semana, producido_semana, falt_total, asisten,
                        num(horas, 1), num(hh, 1), round(hh * VALOR_HORA * RECARGO)])

    # --- Archivos ---
    escribir(salida / "empleados.csv", ["Legajo", "Especialidad", "Linea", "Puesto_habitual"],
             [[e["legajo"], e["especialidad"], e["linea"], e["puesto"]] for e in empleados])
    escribir(salida / "planilla_ausencias.csv",
             ["Legajo", "Especialidad", "Linea", "Fecha", "Dia", "Motivo", "Dias"], ausencias)
    resumen = []
    for esp in ESPECIALIDADES + ["Depósito", "Inspector de calidad"]:
        fila = [esp]
        tot_a = tot_n = 0
        for d in range(5):
            a, n = conteo.get((esp, d), [0, 0])
            tot_a, tot_n = tot_a + a, tot_n + n
            fila.append(num(100 * a / n if n else 0, 1))
        fila.append(num(100 * tot_a / tot_n if tot_n else 0, 1))
        resumen.append(fila)
    escribir(salida / "resumen_ausentismo.csv",
             ["Especialidad"] + [f"{DIAS[d]}_pct" for d in range(5)] + ["Total_pct"], resumen)
    escribir(salida / "ordenes_fabricacion.csv",
             ["OF", "Fecha", "Dia", "Modelo", "Cantidad_pedida", "Producida_en_turno", "Faltante",
              "Cumplimiento_pct", "Cumplida"], of_filas)
    escribir(salida / "cumplimiento_diario.csv",
             ["OF", "Fecha", "Dia", "Mezcla", "Pedido_total", "Producido_total", "Faltante_total",
              "Cumplimiento_pct", "OF_cumplida", "Ausentes_planta", "Ausentes_lineas", "Ajustadores_presentes",
              "Controladores_presentes", "Especialidad_cuello", "Atrasadas_dia_anterior", "Observaciones"], diario)
    escribir(salida / "horas_extra_fin_de_semana.csv",
             ["Semana", "Fecha_sabado", "Pedido_semana", "Producido_en_turno", "Faltante_a_recuperar",
              "Personas_convocadas_presentes", "Horas_jornada", "Horas_hombre", "Costo_pesos"], semanal)

    # --- Resumen por consola para controlar la calibración ---
    dias = len(diario)
    sin_cumplir = sum(1 for f in diario if f[8] == "No")
    print(f"Jornadas: {dias} | sin cumplir la OF: {sin_cumplir} ({100 * sin_cumplir / dias:.0f} %)")
    print(f"Cumplimiento medio: {sum(f[5] for f in diario) / sum(f[4] for f in diario) * 100:.1f} %")
    print(f"Ausencias: {len(ausencias)} | tasa total de líneas: {resumen[0][-1]} (armador) .. ver resumen_ausentismo.csv")
    hh = [float(f[7].replace(',', '.')) if isinstance(f[7], str) else f[7] for f in semanal]
    print(f"Semanas con recuperación: {sum(1 for f in semanal if f[4])} de {len(semanal)} | "
          f"h-hombre medias por semana: {sum(hh) / len(hh):.1f}")
    print(f"Archivos en {salida}")


if __name__ == "__main__":
    main()
