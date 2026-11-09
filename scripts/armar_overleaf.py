"""Arma el proyecto de Overleaf del informe final a partir de INFORME-FINAL.md.

Escribe Informe/Overleaf/main.tex, copia las figuras a Informe/Overleaf/figuras/ y deja todo
comprimido en Informe/Informe_Final_GRUPO_07_Overleaf.zip, listo para "New Project > Upload
Project" en Overleaf (compilador pdfLaTeX). Usa el mismo estilo que la especificación de la
Etapa 1 (Overleaf/main.tex).

    py -3 scripts/armar_overleaf.py
"""
from pathlib import Path
import re
import shutil
import zipfile

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "INFORME-FINAL.md"
SALIDA = RAIZ / "Informe" / "Overleaf"
ZIP = RAIZ / "Informe" / "Informe_Final_GRUPO_07_Overleaf.zip"

TITULO = ("Simulación de la línea de producción y el depósito de KRETZ: horas extra de fin de semana "
          "frente a contratación, reorganización y personal de reserva")

PREAMBULO = r"""% ------------------------------------------------------------------
% Informe final — TPI Simulación KRETZ — Etapa 2/2 — Grupo 7
% Generado a partir de INFORME-FINAL.md con scripts/armar_overleaf.py
% Compilador en Overleaf: pdfLaTeX (Menu > Settings > Compiler).
% Las figuras van en la carpeta figuras/ del proyecto.
% ------------------------------------------------------------------
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{textcomp}
\usepackage[spanish,es-noquoting,es-nodecimaldot,es-tabla]{babel}
\usepackage[a4paper,top=2.5cm,bottom=2.5cm,left=2.3cm,right=2.3cm]{geometry}
\usepackage{microtype}
\usepackage{amsmath,amssymb}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{float}
\usepackage{array}
\usepackage{longtable}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{caption}
\usepackage{needspace}
\usepackage{url}
\usepackage[hidelinks]{hyperref}

% Colores
\definecolor{kretzazul}{HTML}{1F3A6B}
\definecolor{kretzfila}{HTML}{EEF2FA}
\definecolor{kretzgris}{HTML}{B7C2D8}
\definecolor{pendiente}{HTML}{B91C1C}

% Párrafos y listas
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\setlist{itemsep=2pt,topsep=3pt,parsep=0pt}
\renewcommand{\arraystretch}{1.3}

% Tablas: columna de ancho fijo alineada a la izquierda
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\LTpre}{0.6em}
\setlength{\LTpost}{0.6em}
\captionsetup{font=small,labelfont={bf,color=kretzazul}}
\captionsetup[longtable]{skip=4pt}

% Títulos
\titleformat{\section}{\Large\bfseries\color{kretzazul}}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\large\bfseries\color{kretzazul}}{\thesubsection}{0.5em}{}
\titlespacing*{\section}{0pt}{1.4em}{0.6em}
\titlespacing*{\subsection}{0pt}{1.1em}{0.4em}

% Encabezado y pie
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{gray}Informe final — Simulación KRETZ}
\fancyhead[R]{\small\color{gray}Grupo 7}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Datos que faltan completar (se ven en rojo hasta reemplazarlos)
\newcommand{\pendiente}[1]{\textcolor{pendiente}{\textbf{[#1]}}}

\hypersetup{pdftitle={Informe final — Simulación KRETZ}, pdfsubject={Línea de producción y depósito — Fábrica de balanzas KRETZ}}

\begin{document}

% ------------------------------------------------------------------ Título
\begin{center}
  {\LARGE\bfseries\color{kretzazul} TITULO \par}
  \vspace{0.8em}
  {\large Trabajo Práctico Integrador de Simulación — Etapa 2/2 — Grupo 7 \par}
  \vspace{0.6em}
  {\normalsize \pendiente{COMPLETAR: autores y correos electrónicos} \par}
\end{center}
\vspace{0.5em}
"""

ESPECIALES = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "{": r"\{",
              "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "$": r"\$"}
UNICODE = {"−": "$-$", "±": r"\textpm{}", "×": r"$\times$", "≈": r"$\approx$", "→": r"$\rightarrow$"}


def escapar(t):
    t = "".join(ESPECIALES.get(c, c) for c in t)
    for u, l in UNICODE.items():
        t = t.replace(u, l)
    return t


# Fragmentos en línea, en orden de prioridad
TOKEN = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<pend>\[\[[^\]]+\]\])"
    r"|(?P<math>\$(?![\s\)])(?:\\\$|[^$])+?(?<!\\)\$)"
    r"|(?P<bold>\*\*.+?\*\*)"
    r"|(?P<ital>\*[^*\s][^*]*?\*)"
    r"|(?P<url>https?://[^\s)]+)"
)


def en_linea(texto):
    salida, pos = [], 0
    for m in TOKEN.finditer(texto):
        salida.append(escapar(texto[pos:m.start()]))
        tipo, val = m.lastgroup, m.group()
        if tipo == "code":
            codigo = escapar(val[1:-1]).replace("/", r"/\allowbreak{}").replace(r"\_", r"\_\allowbreak{}")
            salida.append(r"\texttt{" + codigo + "}")
        elif tipo == "pend":
            salida.append(r"\pendiente{" + escapar(val[2:-2]) + "}")
        elif tipo == "math":
            salida.append(val)
        elif tipo == "bold":
            salida.append(r"\textbf{" + en_linea(val[2:-2]) + "}")
        elif tipo == "ital":
            salida.append(r"\emph{" + en_linea(val[1:-1]) + "}")
        elif tipo == "url":
            salida.append(r"\url{" + val + "}")
        pos = m.end()
    salida.append(escapar(texto[pos:]))
    return "".join(salida)


def tabla(filas, titulo):
    celdas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in filas]
    cab, cuerpo = celdas[0], [c for c in celdas[2:]]
    n = len(cab)
    largo = [max(len(re.sub(r"\$[^$]*\$", "xxxxx", fila[i])) for fila in [cab] + cuerpo) for i in range(n)]
    # cada columna al menos tan ancha como la palabra más larga de su encabezado (va en negrita)
    palabra = [max(len(w) for w in (re.sub(r"\$[^$]*\$", "xxxxx", c).split() or ["x"])) + 3 for c in cab]
    largo = [min(max(l, p, 8), 60) for l, p in zip(largo, palabra)]
    total = sum(largo)
    disponible = 1.0 - 0.03 * n           # descuenta el espacio entre columnas
    anchos = [disponible * l / total for l in largo]
    letra = r"\footnotesize" if n >= 7 else r"\small"
    columnas = "".join(f"P{{{a:.3f}\\linewidth}}" for a in anchos)
    lineas = [r"\needspace{5\baselineskip}", "{" + letra, r"\begin{longtable}{" + columnas + "}"]
    if titulo:
        lineas.append(r"\caption{" + en_linea(titulo) + r"}\\")
    encabezado = r"\rowcolor{kretzazul}" + " & ".join(
        r"\textcolor{white}{\textbf{" + en_linea(c) + "}}" for c in cab) + r" \\"
    lineas += [encabezado, r"\endfirsthead", encabezado, r"\endhead"]
    for i, fila in enumerate(cuerpo):
        fila = (fila + [""] * n)[:n]
        color = r"\rowcolor{kretzfila}" if i % 2 else ""
        lineas.append(color + " & ".join(en_linea(c) for c in fila) + r" \\")
    lineas += [r"\end{longtable}", "}"]
    return "\n".join(lineas)


def figura(ruta, alt, leyenda):
    nombre = Path(ruta).name
    ancho = "0.8" if "diagrama" in nombre or nombre.startswith("replicas_") else "0.95"
    cap = (r"\caption{" + en_linea(leyenda) + "}") if leyenda else (r"\caption*{" + en_linea(alt) + "}")
    return "\n".join([r"\begin{figure}[H]", r"\centering",
                      rf"\includegraphics[width={ancho}\linewidth]{{figuras/{nombre}}}", cap, r"\end{figure}"])


def lista(lineas):
    """Listas con viñetas o numeradas, anidadas por indentación."""
    out, pila = [], []           # pila de (indentación, entorno)
    for l in lineas:
        sangria = len(l) - len(l.lstrip(" "))
        txt = l.strip()
        numerada = re.match(r"\d+\.\s", txt) is not None
        entorno = "enumerate" if numerada else "itemize"
        contenido = re.sub(r"^(\d+\.|-)\s+", "", txt)
        while pila and sangria < pila[-1][0]:
            out.append(r"\end{" + pila.pop()[1] + "}")
        if not pila or sangria > pila[-1][0]:
            pila.append((sangria, entorno))
            out.append(r"\begin{" + entorno + "}")
        out.append(r"\item " + en_linea(contenido))
    while pila:
        out.append(r"\end{" + pila.pop()[1] + "}")
    return "\n".join(out)


def bloques(texto):
    """Separa el Markdown en bloques: párrafo, lista, tabla, imagen, cita, ecuación, título."""
    lineas = texto.splitlines()
    i, res = 0, []
    while i < len(lineas):
        l = lineas[i]
        s = l.strip()
        if not s:
            i += 1
            continue
        if s.startswith("#"):
            res.append(("titulo", s))
            i += 1
        elif s == "---":
            i += 1
        elif s.startswith("|"):
            j = i
            while j < len(lineas) and lineas[j].strip().startswith("|"):
                j += 1
            res.append(("tabla", lineas[i:j]))
            i = j
        elif s.startswith("!["):
            res.append(("imagen", s))
            i += 1
        elif s.startswith(">"):
            j = i
            while j < len(lineas) and lineas[j].strip().startswith(">"):
                j += 1
            res.append(("cita", " ".join(x.strip()[1:].strip() for x in lineas[i:j])))
            i = j
        elif s.startswith("$$"):
            res.append(("ecuacion", s))
            i += 1
        elif re.match(r"(-|\d+\.)\s", s):
            j = i
            while j < len(lineas) and lineas[j].strip() and re.match(r"\s*(-|\d+\.)\s", lineas[j]):
                j += 1
            res.append(("lista", lineas[i:j]))
            i = j
        else:
            j = i
            while j < len(lineas) and lineas[j].strip() and not re.match(r"\s*(#|\||!\[|>|\$\$|-\s|\d+\.\s)", lineas[j]):
                j += 1
            res.append(("parrafo", " ".join(x.strip() for x in lineas[i:j])))
            i = j
    return res


def convertir(md):
    # Lo que va antes del Resumen (título, autores y nota del borrador) lo arma el preámbulo
    md = md[md.index("## Resumen"):]
    bl = bloques(md)
    out, en_resumen, titulo_tabla = [], False, None
    k = 0
    while k < len(bl):
        tipo, val = bl[k]
        if tipo == "titulo":
            nivel = len(val) - len(val.lstrip("#"))
            txt = val.lstrip("#").strip()
            if en_resumen:
                out.append(r"\end{abstract}")
                en_resumen = False
            if txt == "Resumen":
                out.append(r"\begin{abstract}")
                en_resumen = True
            elif txt.startswith("Referencias") or txt.startswith("Anexos"):
                out.append(r"\section*{" + en_linea(txt) + "}")
                out.append(r"\addcontentsline{toc}{section}{" + en_linea(txt) + "}")
            else:
                txt = re.sub(r"^\d+(\.\d+)*\.?\s+", "", txt)
                out.append((r"\section{" if nivel == 2 else r"\subsection{") + en_linea(txt) + "}")
        elif tipo == "parrafo":
            m = re.match(r"^\*\*Tabla \d+\.\s*(.*?)\*\*$", val)
            if m:
                titulo_tabla = m.group(1)
            elif re.match(r"^\*\*Figura \d+\.\*\*", val):
                pass                                   # ya se usó como leyenda de la figura
            else:
                out.append(en_linea(val))
        elif tipo == "tabla":
            out.append(tabla(val, titulo_tabla))
            titulo_tabla = None
        elif tipo == "imagen":
            m = re.match(r"!\[(.*?)\]\((.*?)\)", val)
            alt, ruta = m.group(1), m.group(2)
            leyenda = None
            if k + 1 < len(bl) and bl[k + 1][0] == "parrafo":
                mm = re.match(r"^\*\*Figura \d+\.\*\*\s*(.*)$", bl[k + 1][1])
                if mm:
                    leyenda = mm.group(1)
            out.append(figura(ruta, alt, leyenda))
        elif tipo == "cita":
            out.append(r"\begin{center}\fcolorbox{kretzgris}{kretzfila}{\parbox{0.93\linewidth}{\small "
                       + en_linea(val) + r"}}\end{center}")
        elif tipo == "ecuacion":
            out.append(r"\[" + val.strip("$").strip() + r"\]")
        elif tipo == "lista":
            out.append(lista(val))
        k += 1
    if en_resumen:
        out.append(r"\end{abstract}")
    return "\n\n".join(out)


def main():
    md = ORIGEN.read_text(encoding="utf-8")
    cuerpo = convertir(md)
    tex = PREAMBULO.replace("TITULO", escapar(TITULO)) + "\n" + cuerpo + "\n\n\\end{document}\n"
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    (SALIDA / "figuras").mkdir(parents=True)
    (SALIDA / "main.tex").write_text(tex, encoding="utf-8")
    usadas = sorted(set(re.findall(r"figuras/([\w\-.]+\.png)", tex)))
    for nombre in usadas:
        shutil.copy(RAIZ / "Informe" / "figuras" / nombre, SALIDA / "figuras" / nombre)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(SALIDA / "main.tex", "main.tex")
        for nombre in usadas:
            z.write(SALIDA / "figuras" / nombre, f"figuras/{nombre}")
    print(f"{SALIDA / 'main.tex'} ({len(tex.splitlines())} líneas), {len(usadas)} figuras")
    print(f"Zip para Overleaf: {ZIP}")


if __name__ == "__main__":
    main()
