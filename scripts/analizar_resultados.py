"""Analiza las réplicas del modelo KRETZ y arma el informe de comparación de escenarios.

Lee Resultados/resultados_corridas.csv (una fila por corrida, la escribe el modelo al
terminar) y Resultados/resultados_semanas.csv (una fila por semana simulada). Agrupa
por escenario y calcula media, desvío e intervalo de confianza del 95 % (t de Student),
el ahorro neto de cada alternativa frente al escenario actual y cuántas réplicas hacen
falta para estimar el costo total con la precisión pedida.

Escribe Resultados/informe_resultados.md y Resultados/resumen_escenarios.csv.

Usa solo la biblioteca estándar de Python.
"""

from pathlib import Path
import argparse
import csv
import math
import statistics

BASE = "Escenario actual"
MODELOS = ["aila", "rep", "nov", "lur", "aur"]
NOMBRES_MODELO = {"aila": "AILA 30KG", "rep": "REPORT LT", "nov": "NOVEL ECO", "lur": "LURA", "aur": "AURA"}
TIPOS = ["armado", "ajuste", "control", "embalaje"]
ESPECIALIDADES = ["armador", "ajustador", "controlador", "embalador"]

# Cuantiles t de Student de dos colas al 95 % según grados de libertad
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
       10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110,
       18: 2.101, 19: 2.093, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}


def t95(gl):
    if gl <= 0:
        return float("nan")
    if gl > 120:
        return 1.960
    return T95[max(k for k in T95 if k <= gl)]  # entre filas de la tabla se usa la más conservadora


def leer(archivo):
    if not archivo.exists():
        return []
    with archivo.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    for fila in filas:
        for k, v in fila.items():
            if k in ("escenario",):
                continue
            try:
                fila[k] = float(v.replace(".", "").replace(",", ".")) if "," in v else float(v)
            except (ValueError, AttributeError):
                pass
    return filas


def agrupar(filas):
    grupos = {}
    for f in filas:
        grupos.setdefault(f["escenario"], []).append(f)
    # El escenario actual primero; el resto en el orden en que aparecen
    return dict(sorted(grupos.items(), key=lambda kv: kv[0] != BASE))


def resumen(valores):
    n = len(valores)
    media = statistics.fmean(valores)
    desvio = statistics.stdev(valores) if n > 1 else float("nan")
    semi = t95(n - 1) * desvio / math.sqrt(n) if n > 1 else float("nan")
    return media, desvio, semi, n


def diferencia(base, alternativa):
    """Ahorro neto (base - alternativa) con IC del 95 % de Welch."""
    mb, sb, _, nb = resumen(base)
    ma, sa, _, na = resumen(alternativa)
    ahorro = mb - ma
    if nb < 2 or na < 2:
        return ahorro, float("nan")
    vb, va = sb ** 2 / nb, sa ** 2 / na
    if vb + va == 0:
        return ahorro, 0.0
    gl = (vb + va) ** 2 / (vb ** 2 / (nb - 1) + va ** 2 / (na - 1))
    return ahorro, t95(int(gl)) * math.sqrt(vb + va)


def replicas_necesarias(valores, precision):
    media, desvio, _, n = resumen(valores)
    if n < 2 or media == 0:
        return None
    return max(n, math.ceil((t95(n - 1) * desvio / (precision * abs(media))) ** 2))


def dec(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


def pesos(v):
    return ("-" if v < 0 else "") + "$ " + f"{abs(v):,.0f}".replace(",", ".")


def pct(v):
    return f"{dec(100 * v)} %"


def ic(media, semi, fmt):
    return fmt(media) if math.isnan(semi) else f"{fmt(media)} ± {fmt(semi).replace('$ ', '')}"


def col(grupo, clave):
    return [f[clave] for f in grupo if isinstance(f.get(clave), float)]


def informe(grupos, semanas, precision):
    L = []
    w = L.append
    w("# Resultados de la simulación — KRETZ\n")
    w("Informe generado por `scripts/analizar_resultados.py` a partir de las réplicas guardadas por el modelo "
      "en `Resultados/resultados_corridas.csv`. Cada réplica es una corrida completa (por defecto, 4 semanas "
      "de 5 jornadas más la recuperación de fin de semana) con una semilla distinta. Los intervalos son de "
      "confianza del 95 % (t de Student) sobre la media de las réplicas.\n")

    w("## Semillas (números aleatorios comunes)\n")
    w("Todos los escenarios tienen que correr con el mismo listado de semillas: la réplica n usa la misma "
      "semilla en todos, así las diferencias entre escenarios no se deben al azar.\n")
    semillas = {n: {int(f["semilla"]) for f in g if isinstance(f.get("semilla"), float)} for n, g in grupos.items()}
    ref = semillas.get(BASE) or next(iter(semillas.values()), set())
    w(f"| Escenario | Semillas distintas | Mismas que {BASE} |")
    w("|---|---|---|")
    for nombre, s in semillas.items():
        faltan, sobran = len(ref - s), len(s - ref)
        estado = "sí" if not faltan and not sobran else f"**no** (faltan {faltan}, sobran {sobran})"
        w(f"| {nombre} | {len(s)} | {estado} |")
    w("")

    w("## Réplicas por escenario\n")
    w("| Escenario | Réplicas | Semanas por réplica | Réplicas necesarias (costo total ±{:.0f} %) |".format(100 * precision))
    w("|---|---|---|---|")
    for nombre, g in grupos.items():
        nec = replicas_necesarias(col(g, "costo_total"), precision)
        w(f"| {nombre} | {len(g)} | {g[0].get('semanas', 0):.0f} | {nec if nec else 'hacen falta al menos 2'} |")
    w("")

    w("## Cumplimiento de la OF\n")
    w("| Escenario | Cumplimiento a tiempo | Jornadas sin cumplir | Efecto de las ausencias (u. de faltante por jornada) |")
    w("|---|---|---|---|")
    for nombre, g in grupos.items():
        m, _, s, _ = resumen(col(g, "cumplimiento"))
        sin = [f["jornadas_sin_cumplir"] / f["jornadas"] for f in g if f.get("jornadas")]
        ms, _, ss, _ = resumen(sin)
        efecto = col(g, "efecto_ausencias")
        if efecto:
            me, _, se, ne = resumen(efecto)
            texto_efecto = f"{ic(me, se, dec)} ({ne} réplicas)"
        else:
            texto_efecto = "s/d"
        w(f"| {nombre} | {ic(m, s, pct)} | {ic(ms, ss, pct)} | {texto_efecto} |")
    w("")
    w("El efecto de las ausencias compara cada día de la semana consigo mismo (jornadas con ausencias "
      "contra jornadas sin ausencias del mismo día), porque el atraso se acumula de lunes a viernes. "
      "Un valor positivo indica más faltante cuando falta alguien.\n")

    w("### Faltante acumulado por modelo (unidades por réplica)\n")
    w("| Escenario | " + " | ".join(NOMBRES_MODELO[m] for m in MODELOS) + " |")
    w("|---|" + "---|" * len(MODELOS))
    for nombre, g in grupos.items():
        celdas = [f"{dec(resumen(col(g, 'faltante_' + m))[0])}" for m in MODELOS]
        w(f"| {nombre} | " + " | ".join(celdas) + " |")
    w("")

    w("## Costos\n")
    w("| Escenario | Horas extra (h-hombre) | Costo horas extra | Costo horas normales | Costo total | Ahorro neto vs. actual |")
    w("|---|---|---|---|---|---|")
    base = grupos.get(BASE)
    filas_resumen = []
    for nombre, g in grupos.items():
        he, _, she, _ = resumen(col(g, "horas_extra"))
        ce, _, sce, _ = resumen(col(g, "costo_horas_extra"))
        cn, _, _, _ = resumen(col(g, "costo_horas_normales"))
        ct, dct, sct, n = resumen(col(g, "costo_total"))
        if base is None or nombre == BASE:
            ahorro_txt, ahorro, semi_a = "—", 0.0, float("nan")
        else:
            ahorro, semi_a = diferencia(col(base, "costo_total"), col(g, "costo_total"))
            signif = "" if math.isnan(semi_a) else (" (significativo)" if abs(ahorro) > semi_a else " (no significativo)")
            ahorro_txt = ic(ahorro, semi_a, pesos) + signif
        w(f"| {nombre} | {ic(he, she, dec)} | {ic(ce, sce, pesos)} | {pesos(cn)} | "
          f"{ic(ct, sct, pesos)} | {ahorro_txt} |")
        filas_resumen.append({"escenario": nombre, "replicas": n, "costo_total_media": ct, "costo_total_desvio": dct,
                              "costo_total_ic95": sct, "costo_horas_extra_media": ce, "horas_extra_media": he,
                              "ahorro_neto": ahorro, "ahorro_neto_ic95": semi_a,
                              "cumplimiento_media": resumen(col(g, "cumplimiento"))[0]})
    w("")
    w("El costo total suma las horas normales de toda la dotación (incluidas las contrataciones y el personal de "
      "reserva), las horas extra de fin de semana pagadas al doble y el costo de reorganización. Un ahorro es "
      "significativo cuando el intervalo de la diferencia no incluye el cero.\n")

    if semanas:
        w("### Horas extra por semana\n")
        w("| Escenario | Semanas observadas | Horas extra por semana | Costo por semana | Semanas con recuperación |")
        w("|---|---|---|---|---|")
        for nombre, g in agrupar(semanas).items():
            h, _, sh, n = resumen(col(g, "horas_extra"))
            c, _, sc, _ = resumen(col(g, "costo_horas_extra"))
            con = sum(1 for f in g if f.get("pendientes_recuperacion", 0) > 0)
            w(f"| {nombre} | {n} | {ic(h, sh, dec)} | {ic(c, sc, pesos)} | {con} de {n} |")
        w("")

    w("## Personal, cuellos de botella y traslados\n")
    w("| Escenario | Util. Armador | Util. Ajustador | Util. Controlador | Util. Embalador | Coberturas | "
      "Vacantes críticas sin cubrir | Tiempo caminando |")
    w("|---|---|---|---|---|---|---|---|")
    for nombre, g in grupos.items():
        u = [pct(resumen(col(g, "util_" + e))[0]) for e in ESPECIALIDADES]
        cob = resumen(col(g, "coberturas"))[0]
        vac = resumen(col(g, "vacantes_criticas"))[0]
        cam = resumen(col(g, "caminata_fraccion"))[0]
        w(f"| {nombre} | " + " | ".join(u) + f" | {dec(cob)} | {dec(vac)} | {pct(cam)} del tiempo ocupado |")
    w("")
    w("| Escenario | " + " | ".join(f"Espera {t} (media / máx., min)" for t in TIPOS) + " |")
    w("|---|" + "---|" * len(TIPOS))
    for nombre, g in grupos.items():
        celdas = [f"{dec(resumen(col(g, 'espera_media_' + t))[0])} / {dec(max(col(g, 'espera_max_' + t) or [0]))}"
                  for t in TIPOS]
        w(f"| {nombre} | " + " | ".join(celdas) + " |")
    w("")

    w("## Respuestas a las preguntas de simulación\n")
    w(conclusiones(grupos, filas_resumen))
    return "\n".join(L), filas_resumen


def conclusiones(grupos, filas):
    base = grupos.get(BASE)
    if base is None:
        return (f"No hay réplicas del escenario «{BASE}», que es la referencia de la comparación. "
                "Corré el experimento Simulation (o una Variación de parámetros sin cambios) para generarlas.\n")
    t = []
    sin = [f["jornadas_sin_cumplir"] / f["jornadas"] for f in base if f.get("jornadas")]
    cumpl = resumen(col(base, "cumplimiento"))[0]
    falt = {m: resumen(col(base, "faltante_" + m))[0] for m in MODELOS}
    peor = max(falt, key=falt.get)
    espera = {tp: resumen(col(base, "espera_media_" + tp))[0] for tp in TIPOS}
    cuello = max(espera, key=espera.get)
    util = {e: resumen(col(base, "util_" + e))[0] for e in ESPECIALIDADES}
    mas_cargada = max(util, key=util.get)
    t.append(f"1. **Cumplimiento con la dotación actual.** En promedio, no se cumple la OF en el "
             f"{pct(statistics.fmean(sin))} de las jornadas y se entrega a tiempo el {pct(cumpl)} de lo pedido. "
             f"El faltante se concentra en **{NOMBRES_MODELO[peor]}** ({dec(falt[peor])} u. por réplica), el mayor "
             f"tiempo de espera en cola está en **{cuello}** ({dec(espera[cuello])} min de media) y la "
             f"especialidad más cargada es **{mas_cargada}** ({pct(util[mas_cargada])}).")
    he = resumen(col(base, "horas_extra"))[0]
    ce = resumen(col(base, "costo_horas_extra"))[0]
    semanas = base[0].get("semanas", 0) or 1
    t.append(f"2. **Horas extra de fin de semana.** Recuperar el faltante requiere {dec(he)} h-hombre por réplica "
             f"({dec(he / semanas)} por semana), con un costo de {pesos(ce)} ({pesos(ce / semanas)} por semana) "
             f"pagadas al doble.")
    alternativas = [f for f in filas if f["escenario"] != BASE]
    if alternativas:
        mejor = max(alternativas, key=lambda f: f["ahorro_neto"])
        contrat = [f for f in alternativas if "Contratar" in f["escenario"]]
        signif = lambda f: not math.isnan(f["ahorro_neto_ic95"]) and abs(f["ahorro_neto"]) > f["ahorro_neto_ic95"]
        if contrat:
            mc = max(contrat, key=lambda f: f["ahorro_neto"])
            veredicto = "conviene" if mc["ahorro_neto"] > 0 and signif(mc) else (
                "no conviene" if mc["ahorro_neto"] < 0 and signif(mc) else "no muestra una diferencia significativa")
            t.append(f"3. **Contratación.** La mejor opción de contratación evaluada es «{mc['escenario']}», con un "
                     f"ahorro neto de {pesos(mc['ahorro_neto'])} por réplica frente al escenario actual: {veredicto} "
                     f"frente a seguir pagando horas extra.")
        for clave, titulo, num in (("Reorganización", "Reorganización de áreas", 4),
                                   ("reserva", "Personal de reserva", 5), ("Secuencia", "Cambio de secuencia", 6)):
            f = next((x for x in alternativas if clave.lower() in x["escenario"].lower()), None)
            if f:
                estado = "ahorra" if f["ahorro_neto"] > 0 else "cuesta"
                nota = "" if signif(f) else " (la diferencia no es significativa con las réplicas actuales)"
                t.append(f"{num}. **{titulo}.** «{f['escenario']}» {estado} {pesos(abs(f['ahorro_neto']))} por réplica "
                         f"frente al escenario actual, con un cumplimiento medio del {pct(f['cumplimiento_media'])}{nota}.")
        if mejor["ahorro_neto"] > 0:
            t.append(f"\n**Alternativa de menor costo total:** «{mejor['escenario']}» "
                     f"({pesos(mejor['costo_total_media'])} por réplica, ahorro neto de {pesos(mejor['ahorro_neto'])}).")
        else:
            t.append("\n**Ninguna alternativa evaluada baja el costo total:** el escenario actual, con horas extra de "
                     "fin de semana, sigue siendo el más barato.")
    else:
        t.append("3. Todavía no hay réplicas de escenarios alternativos para comparar.")
    return "\n".join(t) + "\n"


def main():
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--resultados", type=Path, default=raiz / "Resultados")
    parser.add_argument("--precision", type=float, default=0.05,
                        help="precisión relativa buscada para el costo total (por defecto 0,05 = ±5 %%)")
    args = parser.parse_args()
    corridas = leer(args.resultados / "resultados_corridas.csv")
    if not corridas:
        parser.exit(1, f"No hay resultados en {args.resultados / 'resultados_corridas.csv'}: corré el modelo primero.\n")
    semanas = leer(args.resultados / "resultados_semanas.csv")
    texto, filas = informe(agrupar(corridas), semanas, args.precision)
    (args.resultados / "informe_resultados.md").write_text(texto, encoding="utf-8")
    with (args.resultados / "resumen_escenarios.csv").open("w", encoding="utf-8", newline="") as f:
        out = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter=";")
        out.writeheader()
        for fila in filas:
            out.writerow({k: (f"{v:.4f}".replace(".", ",") if isinstance(v, float) else v) for k, v in fila.items()})
    print(f"Informe: {args.resultados / 'informe_resultados.md'} ({len(corridas)} réplicas, {len(filas)} escenarios)")


if __name__ == "__main__":
    main()
