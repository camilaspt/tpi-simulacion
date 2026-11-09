"""Figuras del informe a partir de Resultados/consolidado/ (ver unir_resultados.py).

Escribe en Informe/figuras/:
- costo_total_ic.png        costo total semanal por escenario, media e IC 95 %
- ahorro_vs_actual.png      ahorro semanal pareado contra el escenario actual, IC 95 %
- horas_extra_ic.png        horas extra semanales por escenario, media e IC 95 %
- validacion.png            escenario actual frente al historial (sintético) de KRETZ

    py -3 scripts/graficos_informe.py
"""
from pathlib import Path
import csv
import math
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "Informe" / "figuras"
SEMANAS = 4
ESCENARIOS = [
    ("E0", "Escenario actual", "Actual"),
    ("E1", "Contratar 2 Ajustadores", "+2 Ajustadores"),
    ("E2", "Contratar 2 Armadores", "+2 Armadores"),
    ("E3", "Contratar 1 Controlador", "+1 Controlador"),
    ("E4", "Contratar 1 Embalador", "+1 Embalador"),
    ("E5", "Personal de reserva polivalente (2)", "Reserva (2)"),
    ("E6", "Reorganización: 3 armadores + 2 ajustadores por línea", "Reorganización"),
    ("E7", "Secuencia: procesos largos primero", "Secuencia largos 1.º"),
]
T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145,
       2.131, 2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]

TINTA, TINTA2, GRILLA = "#1F2937", "#6B7280", "#E5E7EB"
AZUL, GRIS, VERDE, ROJO = "#2563EB", "#9CA3AF", "#15803D", "#B91C1C"
plt.rcParams.update({"font.family": "Arial", "font.size": 10, "axes.edgecolor": GRILLA, "axes.labelcolor": TINTA2,
                     "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.titlesize": 12, "axes.titleweight": "bold",
                     "axes.titlecolor": TINTA, "figure.dpi": 150})


def leer(ruta):
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f, delimiter=";"))
    return filas


def num(v):
    return float(v.replace(",", "."))


def ic(xs):
    n = len(xs)
    m = st.mean(xs)
    return m, (T95[n - 2] if n - 1 <= len(T95) else 1.96) * st.stdev(xs) / math.sqrt(n)


def por_replica(filas, campo, escala=1.0):
    datos = {}
    for f in filas:
        datos.setdefault(f["escenario"], {})[int(f["replica"])] = num(f[campo]) * escala
    return datos


def miles(v, _=None):
    return f"{v / 1e6:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def estilo(ax):
    ax.grid(axis="x", color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def intervalos(datos, titulo, xlabel, archivo, fmt, referencia=None, eje=None):
    etiquetas = [c + "  " + e for c, _, e in ESCENARIOS]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for i, (cod, nom, _) in enumerate(ESCENARIOS):
        m, h = ic(list(datos[nom].values()))
        color = AZUL if cod != "E0" else TINTA
        ax.errorbar(m, i, xerr=h, fmt="o", color=color, ecolor=color, elinewidth=2, capsize=4, markersize=6)
        ax.text(m + h, i, "  " + fmt(m), va="center", fontsize=8.5, color=TINTA)
    if referencia is not None:
        ax.axvline(referencia, color=TINTA2, linewidth=1, linestyle="--")
    ax.set_yticks(range(len(ESCENARIOS)), etiquetas)
    ax.invert_yaxis()
    ax.set_title(titulo, loc="left")
    ax.set_xlabel(xlabel)
    if eje:
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(eje))
    estilo(ax)
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin, xmax + (xmax - xmin) * 0.15)
    fig.tight_layout()
    fig.savefig(SALIDA / archivo)
    plt.close(fig)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    filas = leer(RAIZ / "Resultados" / "consolidado" / "resultados_corridas.csv")

    costo = por_replica(filas, "costo_total", 1 / SEMANAS)
    intervalos(costo, "Costo total semanal por escenario (media e IC 95 %, n = 30)", "Millones de $ por semana",
               "costo_total_ic.png", lambda v: "$ " + miles(v) + " M",
               referencia=st.mean(costo["Escenario actual"].values()), eje=miles)
    horas = por_replica(filas, "horas_extra", 1 / SEMANAS)
    intervalos(horas, "Horas extra de fin de semana (media e IC 95 %, n = 30)", "Horas-hombre por semana",
               "horas_extra_ic.png", lambda v: f"{v:.1f}".replace(".", ",") + " h")

    # Ahorro pareado (misma semilla): actual - alternativa, en miles de $ por semana
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    base = costo["Escenario actual"]
    alternativas = ESCENARIOS[1:]
    for i, (cod, nom, et) in enumerate(alternativas):
        d = [(base[r] - costo[nom][r]) / 1e3 for r in base]
        m, h = ic(d)
        color = VERDE if m - h > 0 else (ROJO if m + h < 0 else GRIS)
        ax.errorbar(m, i, xerr=h, fmt="o", color=color, ecolor=color, elinewidth=2, capsize=4, markersize=6)
        txt = f"{m:+,.0f}".replace(",", ".") + f" ± {h:,.0f}".replace(",", ".")
        ax.text(m + h + 12 if m > -150 else m - h - 12, i, txt, va="center", ha="left" if m > -150 else "right",
                fontsize=8.5, color=TINTA)
    ax.axvline(0, color=TINTA, linewidth=1)
    ax.set_yticks(range(len(alternativas)), [c + "  " + e for c, _, e in alternativas])
    ax.invert_yaxis()
    ax.set_title("Ahorro semanal frente al escenario actual (IC 95 % pareado)", loc="left")
    ax.set_xlabel("Miles de $ por semana (positivo = la alternativa ahorra)")
    estilo(ax)
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin - 60, xmax + 60)
    fig.tight_layout()
    fig.savefig(SALIDA / "ahorro_vs_actual.png")
    plt.close(fig)

    # Validación: historial sintético contra el IC del modelo (escenario actual)
    diario = leer(RAIZ / "Datos" / "Sinteticos" / "cumplimiento_diario.csv")
    semanal = leer(RAIZ / "Datos" / "Sinteticos" / "horas_extra_fin_de_semana.csv")
    hist = {
        "Jornadas sin cumplir la OF (%)": 100 * sum(f["OF_cumplida"] == "No" for f in diario) / len(diario),
        "Cumplimiento de la OF (%)": 100 * sum(num(f["Producido_total"]) for f in diario)
                                     / sum(num(f["Pedido_total"]) for f in diario),
        "Horas extra (h-hombre/semana)": st.mean(num(f["Horas_hombre"]) for f in semanal),
    }
    act = [f for f in filas if f["escenario"] == "Escenario actual"]
    modelo = {
        "Jornadas sin cumplir la OF (%)": [100 * num(f["jornadas_sin_cumplir"]) / num(f["jornadas"]) for f in act],
        "Cumplimiento de la OF (%)": [100 * num(f["cumplimiento"]) for f in act],
        "Horas extra (h-hombre/semana)": [num(f["horas_extra"]) / SEMANAS for f in act],
    }
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6))
    for ax, (t, xs) in zip(axes, modelo.items()):
        m, h = ic(xs)
        ax.errorbar(0, m, yerr=h, fmt="o", color=AZUL, elinewidth=2, capsize=5, markersize=6, label="Modelo (IC 95 %)")
        ax.axhspan(m - h, m + h, color=AZUL, alpha=0.08, linewidth=0)
        ax.plot(1, hist[t], marker="D", color=TINTA, markersize=6, linestyle="none", label="Historial KRETZ")
        ax.set_xticks([0, 1], ["Modelo", "Historial"])
        ax.set_xlim(-0.6, 1.6)
        ax.set_title(t, fontsize=9.5, loc="left")
        ax.grid(axis="y", color=GRILLA, linewidth=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
        lo, hi = min(m - h, hist[t]), max(m + h, hist[t])
        ax.set_ylim(lo - (hi - lo) * 0.6, hi + (hi - lo) * 0.6)
    axes[0].legend(loc="lower left", fontsize=7.5, frameon=False)
    fig.suptitle("Validación del escenario actual (historial sintético, 26 semanas)", x=0.01, ha="left",
                 fontsize=11, fontweight="bold", color=TINTA)
    fig.tight_layout()
    fig.savefig(SALIDA / "validacion.png")
    plt.close(fig)
    print(f"Figuras en {SALIDA}")


if __name__ == "__main__":
    main()
