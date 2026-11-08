"""Gráficos del modelo KRETZ: pestaña de gráficos de Main y experimentos de réplicas.

Lo usan editar_alp.py (para armar los elementos en el .alp a partir de las plantillas
agregadas en AnyLogic) y desarrollar_modelo.py (para compilar las expresiones en el arnés).
"""

# Pestañas (View Areas de Main): nombre -> (x, y, ancho, alto, título)
VISTAS = {
    "vistaPlanta": (0, 0, 1640, 900, "Planta"),
    "vistaGraficos": (0, -1000, 1640, 900, "Gráficos"),
}

# Colores (los mismos de la planta: cajas por modelo y bordes por especialidad)
COLORES_MODELO = ["2563EB", "EA580C", "16A34A", "9333EA", "DC2626"]
NOMBRES_MODELO = ["AILA 30KG", "REPORT LT", "NOVEL ECO", "LURA", "AURA"]
COLORES_ESPECIALIDAD = ["2563EB", "9333EA", "0D9488", "B45309"]

# Grilla de la pestaña: 3 columnas x 2 filas de tarjetas
X0, Y0 = 0, -1000
COLUMNAS = [30, 560, 1090]
FILAS = [-900, -470]
ANCHO_TARJETA, ALTO_TARJETA = 510, 410

# Cada gráfico: (nombre, tipo, columna, fila, título, subtítulo, opciones)
#   series de Plot / TimePlot: (data set, título, color)
#   barras de BarChart: (expresión, título, color)
GRAFICOS = [
    ("graficoCumplimiento", "Plot", 0, 0, "Cumplimiento de la OF por jornada",
     "Unidades por jornada: lo que pide la OF y lo terminado a tiempo", {
         "series": [("dsOFJornada", "OF pedida", "94A3B8"), ("dsATiempoJornada", "Producido a tiempo", "2563EB")]}),
    ("graficoFaltante", "BarChart", 1, 0, "Faltante acumulado por modelo",
     "Unidades de la OF que no se terminaron a tiempo", {
         "barras": [(f"faltanteModelo[{m}]", NOMBRES_MODELO[m], COLORES_MODELO[m]) for m in range(5)]}),
    ("graficoHorasExtra", "Plot", 2, 0, "Horas extra de fin de semana",
     "Horas-hombre de la recuperación de cada semana (se pagan al doble)", {
         "series": [("dsHorasExtraSemana", "Horas-hombre", "D97706")]}),
    ("graficoUtilizacion", "BarChart", 0, 1, "Utilización por especialidad",
     "% del tiempo presente trabajando o caminando", {
         "barras": [(f"100 * utilizacion(Especialidad.{e})", e, c)
                    for e, c in zip(("Armador", "Ajustador", "Controlador", "Embalador"), COLORES_ESPECIALIDAD)]}),
    ("graficoEspera", "BarChart", 1, 1, "Espera en cola por tipo de puesto",
     "Minutos de espera media hasta conseguir operario (cuellos de botella)", {
         "barras": [(f"esperaMedia({t})", n, c)
                    for t, (n, c) in enumerate(zip(("Armado", "Ajuste", "Control final", "Embalaje"),
                                                   COLORES_ESPECIALIDAD))]}),
    ("graficoRacks", "TimePlot", 2, 1, "Ocupación de los racks del depósito",
     "% de celdas ocupadas en cada rack; el stock baja con cada camión", {
         "series": [("dsRackMateriales", "Materiales", "B45309"), ("dsRackCalidad", "Espera de calidad", "1D4ED8"),
                    ("dsRackStock", "Stock", "64748B")],
         "ventana": 2400}),
]

# --- Experimentos de réplicas (Variación de parámetros) -------------------------------
REPLICAS = 30
# Experimento de réplicas por cada experimento de simulación: nombre de Simulation -> nombre de réplicas
NOMBRES_REPLICAS = {
    "Simulation": "Replicas",
    "EscenarioContratacion": "ReplicasContratacion",
    "EscenarioContratacionArmadores": "ReplicasContratacionArmadores",
    "EscenarioContratacionControlador": "ReplicasContratacionControlador",
    "EscenarioContratacionEmbalador": "ReplicasContratacionEmbalador",
    "EscenarioReserva": "ReplicasReserva",
    "EscenarioReorganizacion": "ReplicasReorganizacion",
    "EscenarioSecuencia": "ReplicasSecuencia",
}
# Data sets del experimento: (nombre, expresión con root = Main de la corrida, título, color)
DATASETS_REPLICAS = [
    ("dsCostoReplica", "root.costoTotal() / 1e6", "Costo total (millones de $)", "2563EB"),
    ("dsCumplimientoReplica", "100 * root.cumplimientoTotal()", "Cumplimiento de la OF (%)", "16A34A"),
    ("dsHorasExtraReplica", "root.horasExtraTotal", "Horas extra (h-hombre)", "D97706"),
]


def codigo_antes_replicas():
    return "\n".join(f"{n}.reset();" for n, *_ in DATASETS_REPLICAS)


def codigo_despues_corrida():
    lineas = ["// Un punto por réplica: x = número de réplica"]
    lineas += [f"{n}.add({n}.size() + 1, {e});" for n, e, *_ in DATASETS_REPLICAS]
    return "\n".join(lineas)


def codigo_fin_experimento(titulo):
    return ("traceln(String.format(\"%s: %d réplicas | costo medio $ %,.2f M | cumplimiento medio %.1f %%\", "
            f"\"{titulo}\", dsCostoReplica.size(), dsCostoReplica.getYMean(), dsCumplimientoReplica.getYMean()));\n"
            "traceln(\"Resultados en Resultados/resultados_corridas.csv: analizalos con scripts/analizar_resultados.py\");")


def texto_resumen_replicas():
    return ("String.format(\"Réplicas terminadas: %d de %d   |   costo total medio $ %,.2f M   |   "
            "cumplimiento medio %.1f %%   |   horas extra medias %.0f h-hombre\", dsCostoReplica.size(), "
            f"{REPLICAS}, dsCostoReplica.size() > 0 ? dsCostoReplica.getYMean() : 0, "
            "dsCumplimientoReplica.size() > 0 ? dsCumplimientoReplica.getYMean() : 0, "
            "dsHorasExtraReplica.size() > 0 ? dsHorasExtraReplica.getYMean() : 0)")
