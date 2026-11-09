"""Arma la planilla de resultados (Resultados/Resultados_KRETZ.xlsx) para entregar con el informe.

Lee Resultados/consolidado/ (ver unir_resultados.py) y Datos/Sinteticos/ y escribe un libro
con los datos crudos y todas las estadísticas como fórmulas de Excel, para que se puedan
revisar y recalcular:

- Supuestos    parámetros del análisis (nivel de confianza, valor de la hora, semanas, etc.)
- Resumen      media, desvío e IC del 95 % por escenario (costo, cumplimiento, horas extra)
- Pares        diferencias réplica a réplica contra el escenario actual (números aleatorios comunes)
- Equilibrio   cuántas horas extra tiene que ahorrar una contratación para pagarse, y repago
               de la reorganización
- Validacion   escenario actual contra los datos históricos (sintéticos) de KRETZ
- Corridas, Semanas, Hist_diario, Hist_semanal   datos crudos

    py -3 scripts/armar_planilla.py
"""
from pathlib import Path
import csv

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

RAIZ = Path(__file__).resolve().parent.parent
CONSOLIDADO = RAIZ / "Resultados" / "consolidado"
SINTETICOS = RAIZ / "Datos" / "Sinteticos"
SALIDA = RAIZ / "Resultados" / "Resultados_KRETZ.xlsx"

ESCENARIOS = [
    ("E0", "Escenario actual"),
    ("E1", "Contratar 2 Ajustadores"),
    ("E2", "Contratar 2 Armadores"),
    ("E3", "Contratar 1 Controlador"),
    ("E4", "Contratar 1 Embalador"),
    ("E5", "Personal de reserva polivalente (2)"),
    ("E6", "Reorganización: 3 armadores + 2 ajustadores por línea"),
    ("E7", "Secuencia: procesos largos primero"),
]
REPLICAS = 30

FUENTE = "Arial"
F = Font(name=FUENTE, size=10)
FB = Font(name=FUENTE, size=10, bold=True)
FT = Font(name=FUENTE, size=13, bold=True)
FN = Font(name=FUENTE, size=9, italic=True, color="555555")
FIN = Font(name=FUENTE, size=10, color="0000FF")          # dato de entrada
FLINK = Font(name=FUENTE, size=10, color="008000")        # vínculo a otra hoja
FHEAD = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
RELLENO_HEAD = PatternFill("solid", fgColor="1F3A5F")
RELLENO_SUAVE = PatternFill("solid", fgColor="EEF2F7")
AMARILLO = PatternFill("solid", fgColor="FFFF00")
LINEA = Side(style="thin", color="BFC7D5")
BORDE = Border(bottom=LINEA)

PESOS = '"$" #,##0;-"$" #,##0;-'
PCT = "0.0%;-0.0%;-"
DEC1 = "#,##0.0;-#,##0.0;-"
DEC3 = "0.000"


def numero(v):
    v = v.strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v.replace(".", "").replace(",", ".")) if v.count(",") == 1 and v.count(".") >= 1 \
            else float(v.replace(",", "."))
    except ValueError:
        return v


def leer(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.reader(f, delimiter=";"))
    return filas[0], [[numero(c) for c in fila] for fila in filas[1:] if fila]


def encabezado(ws, fila, textos, desde=1):
    for i, t in enumerate(textos):
        c = ws.cell(fila, desde + i, t)
        c.font, c.fill = FHEAD, RELLENO_HEAD
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[fila].height = 32


def hoja_datos(wb, nombre, cab, filas, extra=()):
    """Hoja de datos crudos; extra = [(título, fórmula con {r} para la fila, formato)]."""
    ws = wb.create_sheet(nombre)
    encabezado(ws, 1, cab + [t for t, _, _ in extra])
    for r, fila in enumerate(filas, start=2):
        for c, v in enumerate(fila, start=1):
            ws.cell(r, c, v).font = F
        for k, (_, formula, fmt) in enumerate(extra):
            c = ws.cell(r, len(cab) + 1 + k, formula.format(r=r))
            c.font, c.number_format = F, fmt
    ws.freeze_panes = "B2"
    for c in range(1, len(cab) + len(extra) + 1):
        ws.column_dimensions[L(c)].width = 14
    ws.column_dimensions["A"].width = 44 if nombre in ("Corridas", "Semanas") else 14
    return ws


def main():
    cab_c, corridas = leer(CONSOLIDADO / "resultados_corridas.csv")
    cab_s, semanas = leer(CONSOLIDADO / "resultados_semanas.csv")
    cab_d, diario = leer(SINTETICOS / "cumplimiento_diario.csv")
    cab_w, semanal = leer(SINTETICOS / "horas_extra_fin_de_semana.csv")
    nombres = {n for _, n in ESCENARIOS}
    faltan = nombres - {f[0] for f in corridas}
    if faltan:
        raise SystemExit(f"Faltan escenarios en los resultados: {faltan}")

    wb = Workbook()
    wb.remove(wb.active)

    # ---------------- Supuestos ----------------
    sup = wb.create_sheet("Supuestos")
    sup["A1"], sup["A1"].font = "Planilla de resultados — Simulación KRETZ", FT
    sup["A2"] = ("Texto azul = dato de entrada que se puede cambiar; negro = fórmula; verde = vínculo a otra hoja. "
                 "Todas las estadísticas se recalculan solas a partir de las hojas de datos crudos.")
    sup["A2"].font = FN
    entradas = [
        ("Nivel de confianza", 0.95, "0%", "Intervalos de confianza de las medias y de las diferencias."),
        ("Semanas simuladas por réplica", 4, "0", "Parámetro semanasSimuladas del modelo."),
        ("Réplicas por escenario", REPLICAS, "0", "Una por semilla del listado común (semillaDeReplica)."),
        ("Valor de la hora normal ($/h, con cargas)", 6500, PESOS, "Parámetro valorHoraNormal (supuesto de la cátedra / KRETZ)."),
        ("Recargo de la hora de fin de semana", 2, "0.0", "Las horas de recuperación se pagan al doble."),
        ("Horas normales por semana por empleado", 40, "0", "5 jornadas de 8 h."),
        ("Costo de la reorganización ($, una sola vez)", 1500000, PESOS, "Parámetro costoReorganizacion del escenario E6."),
    ]
    encabezado(sup, 4, ["Supuesto", "Valor", "Fuente / comentario"])
    celdas = {}
    for i, (t, v, fmt, nota) in enumerate(entradas, start=5):
        sup.cell(i, 1, t).font = F
        c = sup.cell(i, 2, v)
        c.font, c.number_format = FIN, fmt
        sup.cell(i, 3, nota).font = FN
        celdas[t] = f"Supuestos!$B${i}"
    sup.column_dimensions["A"].width = 46
    sup.column_dimensions["B"].width = 16
    sup.column_dimensions["C"].width = 70
    CONF, SEM, VH, REC, HN, CREORG = (celdas[entradas[0][0]], celdas[entradas[1][0]], celdas[entradas[3][0]],
                                      celdas[entradas[4][0]], celdas[entradas[5][0]], celdas[entradas[6][0]])
    sup["A14"] = "Escenarios"
    sup["A14"].font = FB
    encabezado(sup, 15, ["Escenario", "Código", "Cambio respecto del escenario actual"])
    cambios = ["Dotación actual (4 líneas de Armado 4+1, 2 de Control Final 2+3); faltante recuperado el sábado",
               "+2 Ajustadores", "+2 Armadores", "+1 Controlador", "+1 Embalador",
               "2 operarios polivalentes que cubren ausencias", "3 armadores + 2 ajustadores por línea de Armado, "
               "coberturas entre especialidades, $ 1.500.000 una sola vez", "Primero los equipos de proceso más largo"]
    for i, ((cod, nom), cam) in enumerate(zip(ESCENARIOS, cambios), start=16):
        sup.cell(i, 1, nom).font = F
        sup.cell(i, 2, cod).font = F
        sup.cell(i, 3, cam).font = F

    # ---------------- Datos crudos ----------------
    ic = {n: i + 1 for i, n in enumerate(cab_c)}        # columna (1-based) de cada campo en Corridas
    col = lambda campo: L(ic[campo])
    extra_c = [
        ("costo_total_semanal", f"={col('costo_total')}{{r}}/{SEM}", PESOS),
        ("costo_horas_extra_semanal", f"={col('costo_horas_extra')}{{r}}/{SEM}", PESOS),
        ("horas_extra_semanal", f"={col('horas_extra')}{{r}}/{SEM}", DEC1),
        ("pct_jornadas_sin_cumplir", f"={col('jornadas_sin_cumplir')}{{r}}/{col('jornadas')}{{r}}", PCT),
    ]
    ws_c = hoja_datos(wb, "Corridas", cab_c, corridas, extra_c)
    for i, (t, *_) in enumerate(extra_c):
        ic[t] = len(cab_c) + 1 + i
    n_c = len(corridas) + 1
    rango = lambda campo: f"Corridas!${col(campo)}$2:${col(campo)}${n_c}"
    ESC, REP = rango("escenario"), rango("replica")

    hoja_datos(wb, "Semanas", cab_s, semanas)
    ics = {n: i + 1 for i, n in enumerate(cab_s)}
    n_s = len(semanas) + 1
    rango_s = lambda campo: f"Semanas!${L(ics[campo])}$2:${L(ics[campo])}${n_s}"

    hoja_datos(wb, "Hist_diario", cab_d, diario)
    hoja_datos(wb, "Hist_semanal", cab_w, semanal)
    idd = {n: L(i + 1) for i, n in enumerate(cab_d)}
    idw = {n: L(i + 1) for i, n in enumerate(cab_w)}
    n_d, n_w = len(diario) + 1, len(semanal) + 1

    # ---------------- Resumen ----------------
    res = wb.create_sheet("Resumen", 1)
    res["A1"], res["A1"].font = "Media e intervalo de confianza por escenario (réplicas independientes)", FT
    res["A2"] = ("IC = media ± t(n−1)·S/√n. Cada réplica usa una semilla distinta del listado común, así que las "
                 "réplicas de un escenario son independientes. Valores por semana = valor de la réplica / semanas simuladas.")
    res["A2"].font = FN
    medidas = [
        ("Costo total semanal ($)", "costo_total_semanal", PESOS),
        ("Costo de horas extra semanal ($)", "costo_horas_extra_semanal", PESOS),
        ("Horas extra (h-hombre por semana)", "horas_extra_semanal", DEC1),
        ("Cumplimiento de la OF", "cumplimiento", PCT),
        ("Jornadas sin cumplir la OF", "pct_jornadas_sin_cumplir", PCT),
        ("Utilización de Ajustadores", "util_ajustador", PCT),
        ("Espera media en ajuste (min)", "espera_media_ajuste", DEC1),
    ]
    ref_resumen = {}
    fila = 4
    for titulo, campo, fmt in medidas:
        res.cell(fila, 1, titulo).font = FB
        fila += 1
        encabezado(res, fila, ["Escenario", "Código", "n", "Media", "Desvío S", "t", "Semiancho", "IC inferior",
                               "IC superior"])
        for cod, nom in ESCENARIOS:
            fila += 1
            r = fila
            x = rango(campo)
            res.cell(r, 1, nom).font = F
            res.cell(r, 2, cod).font = F
            formulas = [
                f'=COUNTIF({ESC},$A{r})',
                f'=AVERAGEIF({ESC},$A{r},{x})',
                f'=SQRT(SUMPRODUCT(({ESC}=$A{r})*({x}-D{r})^2)/(C{r}-1))',
                f'=TINV(1-{CONF},C{r}-1)',
                f'=F{r}*E{r}/SQRT(C{r})',
                f'=D{r}-G{r}',
                f'=D{r}+G{r}',
            ]
            for k, fx in enumerate(formulas):
                c = res.cell(r, 3 + k, fx)
                c.font = F
                c.number_format = "0" if k == 0 else (DEC3 if k == 3 else fmt)
            ref_resumen[(campo, cod)] = r
        fila += 2
    res.column_dimensions["A"].width = 50
    for c in "BCDEFGHI":
        res.column_dimensions[c].width = 15
    res.freeze_panes = "B4"

    # ---------------- Pares ----------------
    par = wb.create_sheet("Pares", 2)
    par["A1"], par["A1"].font = "Diferencias réplica a réplica contra el escenario actual (números aleatorios comunes)", FT
    par["A2"] = ("La réplica j de todos los escenarios usa la misma semilla. D_j = costo del escenario actual − costo de la "
                 "alternativa (positivo = la alternativa ahorra). IC = media(D) ± t(n−1)·S_D/√n.")
    par["A2"].font = FN

    def bloque(fila0, titulo, campo):
        par.cell(fila0, 1, titulo).font = FB
        cab = ["Réplica", "Semilla"] + [f"{c}" for c, _ in ESCENARIOS] + [f"D {c}" for c, _ in ESCENARIOS[1:]]
        encabezado(par, fila0 + 1, cab)
        x = rango(campo)
        primera = fila0 + 2
        for j in range(1, REPLICAS + 1):
            r = primera + j - 1
            par.cell(r, 1, j).font = F
            c = par.cell(r, 2, f'=SUMIFS({rango("semilla")},{ESC},"{ESCENARIOS[0][1]}",{REP},$A{r})')
            c.font, c.number_format = F, "0"
            for k, (cod, nom) in enumerate(ESCENARIOS):
                c = par.cell(r, 3 + k, f'=SUMIFS({x},{ESC},"{nom}",{REP},$A{r})')
                c.font, c.number_format = F, PESOS
            for k in range(1, len(ESCENARIOS)):
                c = par.cell(r, 3 + len(ESCENARIOS) + k - 1, f"=$C{r}-{L(3 + k)}{r}")
                c.font, c.number_format = F, PESOS
        ultima = primera + REPLICAS - 1
        stats = [("Media", "AVERAGE({rg})"), ("Desvío S", "STDEV({rg})"), ("n", "COUNT({rg})"),
                 ("Semiancho", "TINV(1-{conf},{c}{n}-1)*{c}{s}/SQRT({c}{n})"), ("IC inferior", "{c}{m}-{c}{h}"),
                 ("IC superior", "{c}{m}+{c}{h}"),
                 ("¿Significativo?", 'IF(OR({c}{lo}>0,{c}{hi}<0),"Sí","No")')]
        base = ultima + 2
        filas_stat = {t: base + i for i, (t, _) in enumerate(stats)}
        for i, (t, fx) in enumerate(stats):
            r = base + i
            par.cell(r, 2, t).font = FB
            for cc in range(3, 3 + 2 * len(ESCENARIOS) - 1):
                c = L(cc)
                f = "=" + fx.format(rg=f"{c}{primera}:{c}{ultima}", conf=CONF, c=c, n=filas_stat["n"],
                                    s=filas_stat["Desvío S"], m=filas_stat["Media"], h=filas_stat["Semiancho"],
                                    lo=filas_stat["IC inferior"], hi=filas_stat["IC superior"])
                cel = par.cell(r, cc, f)
                cel.font = FB if t == "¿Significativo?" else F
                cel.number_format = "0" if t == "n" else PESOS
                if t in ("Media", "IC inferior", "IC superior"):
                    cel.fill = RELLENO_SUAVE
        return filas_stat, base + len(stats) + 2

    stats_costo, sig = bloque(4, "Costo total semanal ($)", "costo_total_semanal")
    stats_he, _ = bloque(sig, "Costo de horas extra semanal ($) — ahorro operativo, sin contar contrataciones ni "
                              "reorganización", "costo_horas_extra_semanal")
    par.column_dimensions["A"].width = 9
    par.column_dimensions["B"].width = 16
    for cc in range(3, 3 + 2 * len(ESCENARIOS)):
        par.column_dimensions[L(cc)].width = 14
    col_d = {cod: L(3 + len(ESCENARIOS) + k - 1) for k, (cod, _) in enumerate(ESCENARIOS) if k > 0}

    # ---------------- Equilibrio ----------------
    eq = wb.create_sheet("Equilibrio", 3)
    eq["A1"], eq["A1"].font = "¿Cuándo conviene contratar o reorganizar en lugar de pagar horas extra?", FT
    filas_eq = [
        ("Costo semanal de un empleado contratado ($)", f"={HN}*{VH}", PESOS),
        ("Costo de una hora extra de fin de semana ($)", f"={VH}*{REC}", PESOS),
        ("Horas extra que tiene que ahorrar por semana un contratado para pagarse (h-hombre)", "=B3/B4", DEC1),
        ("Horas extra por semana del escenario actual (media, h-hombre)",
         f"=Resumen!D{ref_resumen[('horas_extra_semanal', 'E0')]}", DEC1),
        ("Horas extra por semana del escenario actual (IC superior)",
         f"=Resumen!I{ref_resumen[('horas_extra_semanal', 'E0')]}", DEC1),
        ("¿Una sola contratación podría pagarse aun eliminando TODAS las horas extra?",
         '=IF(B7>=B5,"Sí","No: las horas extra del escenario actual no alcanzan")', None),
        ("", None, None),
        ("Reorganización (E6): ahorro operativo semanal en horas extra ($, media)",
         f"=Pares!{col_d['E6']}{stats_he['Media']}", PESOS),
        ("Ahorro operativo semanal: IC inferior", f"=Pares!{col_d['E6']}{stats_he['IC inferior']}", PESOS),
        ("Ahorro operativo semanal: IC superior", f"=Pares!{col_d['E6']}{stats_he['IC superior']}", PESOS),
        ("Costo de la reorganización ($, una sola vez)", f"={CREORG}", PESOS),
        ("Semanas para recuperar la inversión (media)", "=B13/B10", DEC1),
        ("Semanas para recuperar la inversión (optimista: IC superior del ahorro)", "=B13/B12", DEC1),
        ("Semanas para recuperar la inversión (pesimista: IC inferior del ahorro)", "=IF(B11>0,B13/B11,\"no se recupera\")", DEC1),
        ("Ahorro neto en un año de 48 semanas hábiles ($, media)", "=48*B10-B13", PESOS),
    ]
    for i, (t, fx, fmt) in enumerate(filas_eq, start=3):
        eq.cell(i, 1, t).font = F
        if fx:
            c = eq.cell(i, 2, fx)
            c.font = FLINK if "!" in fx else F
            if fmt:
                c.number_format = fmt
    eq.column_dimensions["A"].width = 82
    eq.column_dimensions["B"].width = 22
    eq["A19"] = ("Lectura: un contratado cuesta lo mismo que 20 h-hombre de horas extra por semana, y el escenario actual "
                 "usa en promedio menos que eso en TOTAL; por eso ninguna contratación se paga sola. La reorganización no "
                 "agrega sueldos: su único costo es la inversión inicial, que se recupera con el ahorro de horas extra.")
    eq["A19"].font = FN
    eq["A19"].alignment = Alignment(wrap_text=True, vertical="top")
    eq.row_dimensions[19].height = 48

    # ---------------- Validacion ----------------
    val = wb.create_sheet("Validacion", 4)
    val["A1"], val["A1"].font = "Validación: escenario actual simulado frente al historial de KRETZ", FT
    val["A2"] = ("ATENCIÓN: el historial de esta hoja es SINTÉTICO (Datos/Sinteticos, generado por "
                 "scripts/generar_datos_sinteticos.py) hasta que KRETZ entregue los registros reales; hay que declararlo "
                 "así en el informe. Al reemplazar las hojas Hist_diario e Hist_semanal por datos reales, esta tabla se "
                 "recalcula sola.")
    val["A2"].font = FN
    val["A2"].alignment = Alignment(wrap_text=True)
    val.row_dimensions[2].height = 40
    for c in "BCDEF":
        val[f"{c}2"].fill = AMARILLO
    val["A2"].fill = AMARILLO
    encabezado(val, 4, ["Medida", "Historial (26 semanas)", "Modelo: media", "Modelo: IC inferior",
                        "Modelo: IC superior", "¿Historial dentro del IC del modelo?"])
    r0 = ref_resumen
    validaciones = [
        ("Jornadas sin cumplir la OF",
         f'=COUNTIF(Hist_diario!${idd["OF_cumplida"]}$2:${idd["OF_cumplida"]}${n_d},"No")/COUNTA(Hist_diario!$A$2:$A${n_d})',
         ("pct_jornadas_sin_cumplir", "E0"), PCT),
        ("Cumplimiento de la OF en el turno",
         f'=SUM(Hist_diario!${idd["Producido_total"]}$2:${idd["Producido_total"]}${n_d})/'
         f'SUM(Hist_diario!${idd["Pedido_total"]}$2:${idd["Pedido_total"]}${n_d})',
         ("cumplimiento", "E0"), PCT),
        ("Horas extra de fin de semana (h-hombre por semana)",
         f'=AVERAGE(Hist_semanal!${idw["Horas_hombre"]}$2:${idw["Horas_hombre"]}${n_w})',
         ("horas_extra_semanal", "E0"), DEC1),
        ("Costo de horas extra por semana ($)",
         f'=AVERAGE(Hist_semanal!${idw["Costo_pesos"]}$2:${idw["Costo_pesos"]}${n_w})',
         ("costo_horas_extra_semanal", "E0"), PESOS),
    ]
    for i, (t, hist, (campo, cod), fmt) in enumerate(validaciones, start=5):
        rr = r0[(campo, cod)]
        val.cell(i, 1, t).font = F
        for k, fx in enumerate([hist, f"=Resumen!D{rr}", f"=Resumen!H{rr}", f"=Resumen!I{rr}"]):
            c = val.cell(i, 2 + k, fx)
            c.font = F if k == 0 else FLINK
            c.number_format = fmt
        val.cell(i, 6, f'=IF(AND(B{i}>=D{i},B{i}<=E{i}),"Sí","No")').font = FB
    i = 5 + len(validaciones)
    val.cell(i, 1, "Semanas que necesitaron recuperación").font = F
    c = val.cell(i, 2, f'=COUNTIF(Hist_semanal!${idw["Faltante_a_recuperar"]}$2:${idw["Faltante_a_recuperar"]}${n_w},">0")'
                       f'/COUNTA(Hist_semanal!$A$2:$A${n_w})')
    c.font, c.number_format = F, PCT
    c = val.cell(i, 3, f'=COUNTIFS({rango_s("escenario")},"{ESCENARIOS[0][1]}",{rango_s("horas_extra")},">0")'
                       f'/COUNTIF({rango_s("escenario")},"{ESCENARIOS[0][1]}")')
    c.font, c.number_format = FLINK, PCT
    val.cell(i, 6, "proporción (sin IC)").font = FN
    i += 1
    val.cell(i, 1, "Especialidad que limita la jornada (cuello de botella)").font = F
    c = val.cell(i, 2, f'=IF(COUNTIF(Hist_diario!${idd["Especialidad_cuello"]}$2:${idd["Especialidad_cuello"]}${n_d},'
                       f'"Ajustador")>=COUNTIF(Hist_diario!${idd["Especialidad_cuello"]}$2:${idd["Especialidad_cuello"]}${n_d},"?*")/2,'
                       f'"Ajustador","Otra")')
    c.font = F
    c = val.cell(i, 3, f"=IF(Resumen!D{r0[('util_ajustador', 'E0')]}>0.75,\"Ajustador (utilización \"&TEXT(Resumen!D{r0[('util_ajustador', 'E0')]},\"0%\")&\")\",\"Otra\")")
    c.font = FLINK
    val.cell(i, 6, '=IF(LEFT(B' + str(i) + ',9)=LEFT(C' + str(i) + ',9),"Sí","No")').font = FB
    val.column_dimensions["A"].width = 52
    for c in "BCDE":
        val.column_dimensions[c].width = 20
    val.column_dimensions["F"].width = 26
    val["A3"].comment = Comment("Datos sintéticos: no presentarlos como datos relevados de la planta.", "TPI")

    wb.calculation.fullCalcOnLoad = True
    wb.save(SALIDA)
    print(f"Planilla: {SALIDA}")


if __name__ == "__main__":
    main()
