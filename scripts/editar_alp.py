"""Aplica los cambios del modelo sobre el .alp guardado desde AnyLogic, sin regenerarlo.

A diferencia de desarrollar_modelo.py (que arma el modelo completo desde el modelo base y
pisa lo que se haya hecho a mano), este script edita "TPI-Simulacion-KRETZ - copia.alp" en
el lugar y conserva lo agregado en AnyLogic:

- sincroniza con modelo_java.py los parámetros, variables, funciones, eventos y el código
  de arranque de Main, Balanza y Operario;
- actualiza los parámetros de los bloques del diagrama de flujo (BLOQUES de
  desarrollar_modelo.py), agrega los que falten y rehace los conectores (CONEXIONES); las
  posiciones de los bloques que ya existen no se tocan;
- arma el plano 3D a partir de los objetos que se agregaron en AnyLogic como plantilla:
  una mesa por puesto (Figure3D "table"), los racks del depósito (Storage "storage") y la
  caja de cada unidad (Figure3D "box_1_closed"). Después de copiarlas, borra las plantillas.

Antes de escribir guarda una copia del archivo con extensión .antes.alp. Hay que cerrar el
modelo en AnyLogic antes de correrlo.

Usa solo la biblioteca estándar de Python.
"""

from pathlib import Path
import argparse
import math
import re
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_java as J  # noqa: E402
import desarrollar_modelo as D  # noqa: E402
import graficos as G  # noqa: E402

# Elementos que generaba el script y ya no se usan
VARIABLES_OBSOLETAS = {"rackCalidadX", "rackCalidadY", "contadorRackCalidad", "despachoX", "despachoY",
                       "kitsEnRack", "diagnosticoRacks", "diasConAusencias", "diasSinAusencias",
                       "faltanteConAusencias", "faltanteSinAusencias"}
FUNCIONES_OBSOLETAS = {"ubicarEnRackCalidad", "liberarCargador", "reponerKits"}
EVENTOS_OBSOLETOS = {"eventoReponerKits"}
BLOQUES_OBSOLETOS = {"esperaLugarKit"}
# Gráficos agregados por el script en versiones anteriores (se reemplazan por las plantillas)
GRAFICOS_VIEJOS = re.compile(r"^(mesa\d+|mesaInspector|rackDeMateriales.*|rackDeCalidad.*|stockProductoTerminado.*)$")
PLANTILLAS = {"table": "Figure3D", "box_1_closed": "Figure3D", "storage": "RackStorage"}


class Editor(D.Generador):
    def __init__(self, archivo):
        super().__init__(archivo)
        self.main = self.clase("Main")
        self.balanza = self.clase("Balanza")
        self.operario = self.clase("Operario")
        _, self.plano = self.presentacion_nivel(self.main)

    # --- utilidades -------------------------------------------------------------
    def nombre(self, nodo):
        n = self.hijo(nodo, "Name")
        return n.firstChild.data if n is not None and n.firstChild is not None else None

    def por_nombre(self, contenedor, tag):
        return {self.nombre(n): n for n in self.hijos(contenedor, tag)} if contenedor is not None else {}

    def nuevo(self, constructor, *args):
        """Construye un elemento con los métodos de Generador sin agregarlo a ningún lado."""
        tmp = self.el(None, "tmp")
        constructor(tmp, *args)
        nodo = self.hijos(tmp)[0]
        tmp.removeChild(nodo)
        return nodo

    def reemplazar(self, viejo, nuevo):
        # Se conserva el Id para que AnyLogic lo reconozca como el mismo elemento
        self.hijo(nuevo, "Id").firstChild.data = self.hijo(viejo, "Id").firstChild.data
        viejo.parentNode.replaceChild(nuevo, viejo)

    def poner(self, nodo, tag, valor, despues_de=None):
        h = self.hijo(nodo, tag)
        if h is None:
            h = self.el(None, tag)
            ref = self.hijo(nodo, despues_de) if despues_de else None
            nodo.insertBefore(h, ref.nextSibling if ref is not None else None)
        while h.firstChild is not None:
            h.removeChild(h.firstChild)
        h.appendChild(self.doc.createTextNode(str(valor)))
        return h

    def posicion(self, nodo, x, y):
        # Las figuras 3D repiten X/Y después del modo de dibujo: se actualizan todas
        for tag, v in (("X", x), ("Y", y)):
            for h in self.hijos(nodo, tag):
                h.firstChild.data = str(v)

    # --- código -------------------------------------------------------------------
    def sincronizar_variables(self, clase, variables, parametros=()):
        cont = self.hijo(clase, "Variables")
        actuales = {self.nombre(v): v for v in self.hijos(cont, "Variable")}
        for n in VARIABLES_OBSOLETAS & set(actuales):
            cont.removeChild(actuales.pop(n))
        y = 40 + 22 * len(actuales)
        for n, t, v, etiqueta in parametros:
            if n in actuales:
                # El valor por defecto y la etiqueta salen de modelo_java.py
                props = self.hijo(actuales[n], "Properties")
                self.hijo(self.hijo(props, "DefaultValue"), "Code").firstChild.data = v
                self.hijo(self.hijo(props, "ParameterEditor"), "Label").firstChild.data = etiqueta
            else:
                self.parametro(cont, n, t, v, etiqueta, 1820, y)
                y += 22
        for n, t, v in variables:
            if n in actuales:
                viejo = actuales[n]
                nuevo = self.nuevo(self.variable, n, t, v, self.hijo(viejo, "X").firstChild.data,
                                   self.hijo(viejo, "Y").firstChild.data)
                self.reemplazar(viejo, nuevo)
            else:
                self.variable(cont, n, t, v, 2560, y)
                y += 22

    def sincronizar_funciones(self, clase, funciones):
        cont = self.hijo(clase, "Functions")
        actuales = self.por_nombre(cont, "Function")
        for n in FUNCIONES_OBSOLETAS & set(actuales):
            cont.removeChild(actuales.pop(n))
        y = 40
        for n, (ret, params, cuerpo) in funciones.items():
            if n in actuales:
                viejo = actuales[n]
                nuevo = self.nuevo(self.funcion, n, ret, params, cuerpo, self.hijo(viejo, "X").firstChild.data,
                                   self.hijo(viejo, "Y").firstChild.data)
                self.reemplazar(viejo, nuevo)
            else:
                self.funcion(cont, n, ret, params, cuerpo, 3020, y)
                y += 22

    def sincronizar_codigo(self):
        self.sincronizar_variables(self.main, J.VARIABLES_MAIN, J.PARAMETROS)
        self.sincronizar_funciones(self.main, J.FUNCIONES_MAIN)
        self.sincronizar_variables(self.balanza, J.VARIABLES_BALANZA)
        self.sincronizar_variables(self.operario, J.VARIABLES_OPERARIO)
        self.sincronizar_funciones(self.operario, J.FUNCIONES_OPERARIO)
        eventos = self.hijo(self.main, "Events")
        actuales = self.por_nombre(eventos, "Event")
        for n in EVENTOS_OBSOLETOS & set(actuales):
            eventos.removeChild(actuales.pop(n))
        for i, (n, accion) in enumerate(J.EVENTOS):
            if n in actuales:
                self.hijo(actuales[n], "Action").firstChild.data = accion
            else:
                self.evento(eventos, n, accion, 1820, 520 + i * 25)
        self.hijo(self.main, "StartupCode").firstChild.data = J.STARTUP

    # --- diagrama de flujo -------------------------------------------------------
    def sincronizar_flujo(self):
        bloques = self.hijo(self.main, "EmbeddedObjects")
        actuales = self.por_nombre(bloques, "EmbeddedObject")
        for n in BLOQUES_OBSOLETOS & set(actuales):
            bloques.removeChild(actuales.pop(n))
        # Las entidades (Balanza / Operario) se toman de los bloques que ya las crean
        entidades = {}
        for eo in actuales.values():
            for par in eo.getElementsByTagName("Parameter"):
                valor = self.hijo(par, "Value")
                if self.nombre(par) in ("newEntity", "newUnit") and valor is not None:
                    cls = valor.getElementsByTagName("ClassName")
                    if cls:
                        entidades.setdefault(cls[0].firstChild.data, valor.cloneNode(True))
        # Tipos de agente nuevos (CamionRetiro): se copia la entidad de Balanza y se la apunta a ese tipo
        for tipo in set(D.TIPO_AGENTE.values()) - set(entidades):
            clase = self.clase(tipo)
            generico = self.hijo(self.hijo(clase, "GenericParameter"), "Id").firstChild.data
            valor = entidades["Balanza"].cloneNode(True)
            for c in valor.getElementsByTagName("ClassName"):
                c.firstChild.data = tipo
            valor.getElementsByTagName("ItemName")[0].firstChild.data = generico
            pars = valor.getElementsByTagName("Parameters")[0]
            for par in self.hijos(pars):
                pars.removeChild(par)
            entidades[tipo] = valor
        clases, posiciones = {}, {}
        for name, cls, x, y, params in D.BLOQUES:
            nuevo = self.nuevo(self.bloque, name, cls, x, y, params, entidades)
            if name in actuales:
                viejo = actuales[name]
                viejo.replaceChild(self.hijo(nuevo, "Parameters"), self.hijo(viejo, "Parameters"))
                x, y = (float(self.hijo(viejo, t).firstChild.data) for t in ("X", "Y"))
            else:
                bloques.appendChild(nuevo)
            clases[name], posiciones[name] = cls, (x, y)
        conectores = self.hijo(self.main, "Connectors")
        for c in self.hijos(conectores, "Connector"):
            conectores.removeChild(c)
        for i, con in enumerate(D.CONEXIONES):
            self.conector(conectores, i, *con, clases, posiciones)

    # --- plano 3D -----------------------------------------------------------------
    def plantillas(self):
        encontradas = {}
        for nombre, tag in PLANTILLAS.items():
            nodo = next((n for n in self.hijos(self.plano, tag) if self.nombre(n) == nombre), None)
            if nodo is None:
                sys.exit(f"No está la plantilla {tag} «{nombre}» en Main: agregala en AnyLogic y guardá el modelo.")
            encontradas[nombre] = nodo
        return encontradas

    def figura(self, plantilla, nombre, x, y, rotacion=0.0, visible=None, modo="SHAPE_DRAW_3D"):
        f = plantilla.cloneNode(True)
        self.renovar_ids(f)
        self.hijo(f, "Name").firstChild.data = nombre
        self.posicion(f, x, y)
        self.poner(f, "DrawMode", modo)
        self.poner(f, "Rotation", rotacion)
        viejo = self.hijo(f, "VisibleCode")
        if viejo is not None:
            f.removeChild(viejo)
        if visible:
            # Igual que en las formas: el código de visibilidad va después del modo de dibujo
            f.insertBefore(self.el(None, "VisibleCode", visible, cdata=True), self.hijo(f, "DrawMode").nextSibling)
        return f

    def armar_plano(self):
        p = self.plantillas()
        for n in list(self.hijos(self.plano)):
            if GRAFICOS_VIEJOS.match(self.nombre(n) or ""):
                self.plano.removeChild(n)
        v = {n: float(val) for n, t, val in J.VARIABLES_MAIN if t in ("int", "double")}
        # Estado de los puestos y etiquetas: solo en 2D (en 3D se ven las mesas)
        for n in self.hijos(self.plano, "Rectangle"):
            if re.match(r"^puesto(\d+|Inspector)$", self.nombre(n) or ""):
                self.poner(n, "DrawMode", "SHAPE_DRAW_2D")
                self.poner(n, "Z", 0)
                self.poner(n, "ZHeight", 0)
        textos = self.por_nombre(self.plano, "Text")
        rects = self.por_nombre(self.plano, "Rectangle")
        ix, iy = v["inspectorX"], v["inspectorY"]
        self.posicion(rects["puestoInspector"], ix - 7, iy - 18)
        # Mesas: una copia de la plantilla por puesto, en columnas a lo largo del eje Y
        giro = round(math.pi / 2, 6)
        for k in range(D.PUESTOS_DIBUJADOS):
            x, y = D.posicion_puesto(k, v)
            self.plano.appendChild(self.figura(p["table"], f"mesa{k}", x - v["mesaOffset"] + D.CORRECCION_MESA_X, y,
                                               giro, visible=f"nPuestos > {k}"))
        self.plano.appendChild(self.figura(p["table"], "mesaInspector", ix + D.CORRECCION_MESA_X, iy, giro))
        # Racks del depósito: copias de la plantilla Storage (el tamaño lo fija ajustar_racks)
        for nombre in D.ALMACENES:
            r = p["storage"].cloneNode(True)
            self.renovar_ids(r)
            self.hijo(r, "Name").firstChild.data = nombre
            self.plano.appendChild(r)
        self.posicion(textos["rotuloInspector"], ix, iy - 28)
        # Caja de cada unidad: la plantilla box_1_closed y una marca con el color del modelo
        _, plano_b = self.presentacion_nivel(self.balanza)
        for n in list(self.hijos(plano_b)):
            if self.nombre(n) in ("caja", "marcaModelo"):
                plano_b.removeChild(n)
        plano_b.appendChild(self.figura(p["box_1_closed"], "caja", 0, 0, visible="mostrarCaja",
                                        modo="SHAPE_DRAW_2D3D"))
        self.rectangulo(plano_b, "marcaModelo", -3, -3, 6, 6, fill="C8A165", line="7C5A2A", fill_code="color",
                        visible="mostrarCaja", draw="SHAPE_DRAW_2D3D", z=8, alto=1)
        for nodo in p.values():
            self.plano.removeChild(nodo)
        self.registrar_recurso("3d/box_1_closed.dae")
        self.registrar_recurso("3d/table.dae")

    def ajustar_racks(self):
        """Posición y tamaño de los racks Storage según D.ALMACENES, y sus rótulos.

        Cada celda de un Storage guarda una sola caja (la "capacidad de celda" de AnyLogic
        solo admite 1), así que la capacidad sale de unidades x bahías x estantes x celdas.
        """
        racks = {self.nombre(n): n for n in self.hijos(self.plano, "RackStorage")}
        for nombre, c in D.ALMACENES.items():
            if nombre not in racks:
                sys.exit(f"No está el rack «{nombre}» en Main.")
            r = racks[nombre]
            self.posicion(r, c["x"], c["y"])
            self.poner(r, "NumberOfBays", c["bahias"])
            self.poner(r, "NumberOfShelves", c["estantes"])
            for tag, valor in (("CellWidth", c["ancho_celda"]), ("ShelfHeight", c["alto_estante"]),
                               ("Width", c["bahias"] * c["celdas"] * c["ancho_celda"])):
                self.hijo(self.hijo(r, tag), "Value").firstChild.data = str(valor)
            for par in r.getElementsByTagName("Parameter"):
                if self.nombre(par) in ("cellCapacity", "numberOfCellsPerSlot"):
                    for h in self.hijos(par, "Value"):
                        par.removeChild(h)
                if self.nombre(par) == "numberOfCellsPerSlot":
                    val = self.el(par, "Value", attrs={"Class": "CodeValue"})
                    self.el(val, "Code", c["celdas"], cdata=True)
        v = {n: float(val) for n, t, val in J.VARIABLES_MAIN if t in ("int", "double")}
        textos = self.por_nombre(self.plano, "Text")
        m, q = D.ALMACENES["almacenMateriales"], D.ALMACENES["almacenCalidad"]
        self.posicion(textos["rotuloRack"], m["x"] + 48, m["y"] - 8)
        self.posicion(textos["usoRack"], v["rackX"], v["rackY"] + 14)
        self.posicion(textos["rotuloRackCalidad"], q["x"] + 80, q["y"] - 8)
        self.posicion(textos["rotuloStock"], v["stockFrenteX"], v["stockFrenteY"] + 14)

    # --- Gráficos: pestañas, tarjetas y data sets ----------------------------------------
    def poner_cdata(self, nodo, tag, valor):
        h = self.hijo(nodo, tag)
        if h is None:
            h = self.el(nodo, tag)
        while h.firstChild is not None:
            h.removeChild(h.firstChild)
        h.appendChild(self.doc.createCDATASection(str(valor)))

    def plantilla(self, contenedor, tag, nombres):
        """Primer elemento del tipo pedido: la muestra agregada en AnyLogic o uno ya generado."""
        for n in self.hijos(contenedor, tag):
            if self.nombre(n) in nombres:
                return n
        return next(iter(self.hijos(contenedor, tag)), None)

    def grafico(self, tpl, nombre, tipo, x, y, ancho, alto, opciones):
        g = tpl.cloneNode(True)
        self.renovar_ids(g)
        self.hijo(g, "Name").firstChild.data = nombre
        self.posicion(g, x, y)
        self.poner(g, "DrawMode", "SHAPE_DRAW_2D")
        self.poner(g, "Width", ancho)
        self.poner(g, "Height", alto)
        area = self.hijo(g, "ChartArea")
        for tag, valor in (("XOffset", 60), ("YOffset", 12), ("Width", ancho - 85), ("Height", alto - 110)):
            self.poner(area, tag, valor)
        self.poner(self.hijo(g, "Legend"), "Size", 40)
        item_tag = "DataItem" if tipo == "BarChart" else "DatasetExpression"
        items = self.hijos(g, item_tag)
        modelo, ref = items[0], items[-1].nextSibling
        for it in items:
            g.removeChild(it)
        lista = opciones.get("barras") or opciones.get("series")
        for expresion, titulo, color in lista:
            it = modelo.cloneNode(True)
            self.renovar_ids(it)
            self.poner_cdata(it, "Expression", expresion)
            self.poner(it, "Color", self.color(color))
            self.poner_cdata(it, "Title", titulo)
            if tipo != "BarChart":
                # Expression2Flag = "usar valor": en true grafica Expression2 (0) en lugar del data set
                self.poner(it, "Expression2Flag", "false")
                self.poner(it, "PointStyle", opciones.get("puntos") or ("CIRCLE" if tipo == "Plot" else "NONE"))
                self.poner(it, "LineWidth", "2.0")
            g.insertBefore(it, ref)
        if tipo != "BarChart":
            # Con actualización automática, el gráfico llama a update() de cada data set y este le agrega
            # (time(), 0) cada minuto, que desplaza a los datos reales. Los data sets los llena el modelo.
            self.poner(g, "AutoUpdate", "false")
        if tipo == "TimePlot":
            self.poner_cdata(g, "TimeWindowExpression", opciones.get("ventana", 2400))
            self.poner(g, "SamplesToKeep", 3000)
        elif tipo == "Plot":
            self.poner(g, "SamplesToKeep", 200)
            # Las réplicas corren en paralelo y terminan en cualquier orden: solo puntos, sin unirlos
            self.poner(g, "DrawLine", "false" if opciones.get("sin_linea") else "true")
        return g

    def data_set(self, tpl, nombre, puntos, x, y):
        d = tpl.cloneNode(True)
        self.renovar_ids(d)
        self.hijo(d, "Name").firstChild.data = nombre
        self.posicion(d, x, y)
        self.poner(d, "AutoUpdate", "false")
        self.poner(d, "SamplesToKeep", puntos)
        return d

    def armar_graficos(self):
        analisis = self.hijo(self.main, "AnalysisData")
        areas = self.hijo(self.main, "Areas")
        plano = self.plano
        tpl_ds = self.plantilla(analisis, "DataSet", {"dataset"})
        tpl_area = self.plantilla(areas, "Area", {"viewArea"})
        tpls = {t: self.plantilla(plano, t, n) for t, n in
                (("Plot", {"plot1"}), ("BarChart", {"chart"}), ("TimePlot", {"plot"}))}
        if None in (tpl_ds, tpl_area, *tpls.values()):
            sys.exit("Faltan plantillas de gráficos en Main (View Area, Plot, Bar Chart, Time Plot y Data Set).")
        tpl_ds, tpl_area = tpl_ds.cloneNode(True), tpl_area.cloneNode(True)
        tpls = {t: n.cloneNode(True) for t, n in tpls.items()}
        # Se borran las plantillas y lo generado antes (así se puede volver a correr)
        nuestros = re.compile(r"^(grafico|tarjeta|tituloGrafico|subtituloGrafico|fondoGraficos|encabezadoGraficos|"
                              r"relojGraficos|boton(VerGraficos|VerPlanta)|vista|navbar|fondoVariables|"
                              r"(titulo|panel)Ausencias$|fondoTablero$|tituloTablero$|reloj$)")
        for cont, plantillas in ((plano, {"plot", "plot1", "chart"}), (areas, {"viewArea"}),
                                 (analisis, {"dataset"})):
            for n in list(self.hijos(cont)):
                nombre = self.nombre(n) or ""
                if nombre in plantillas or nuestros.match(nombre) or nombre in dict(J.DATASETS):
                    cont.removeChild(n)
        # Data sets que llena el modelo (cerrarJornada, finSemana, registrarRacks)
        for i, (n, puntos) in enumerate(J.DATASETS):
            analisis.appendChild(self.data_set(tpl_ds, n, puntos, 1820, -1000 + i * 25))
        # Pestañas y botones para pasar de una a otra
        for nombre, (x, y, w, h, titulo) in G.VISTAS.items():
            a = tpl_area.cloneNode(True)
            self.renovar_ids(a)
            self.hijo(a, "Name").firstChild.data = nombre
            self.posicion(a, x, y)
            self.poner(a, "Width", w)
            self.poner(a, "Height", h)
            self.poner_cdata(a, "Title", titulo)
            areas.appendChild(a)
        # Panel de gráficos (la barra de pestañas la agrega armar_pestanas)
        self.rectangulo(plano, "fondoGraficos", G.X0, G.Y0, 1640, 900, fill="F1F5F9", line="CBD5E1")
        for nombre, tipo, col, fila, titulo, subtitulo, opciones in G.GRAFICOS:
            x, y = G.COLUMNAS[col], G.FILAS[fila]
            sufijo = nombre[len("grafico"):]
            self.rectangulo(plano, f"tarjeta{sufijo}", x, y, G.ANCHO_TARJETA, G.ALTO_TARJETA, fill="FFFFFF",
                            line="CBD5E1")
            self.texto(plano, f"tituloGrafico{sufijo}", x + 18, y + 12, titulo, size=15, bold=True, color="0F172A")
            self.texto(plano, f"subtituloGrafico{sufijo}", x + 18, y + 34, subtitulo, size=11, color="475569")
            plano.appendChild(self.grafico(tpls[tipo], nombre, tipo, x + 5, y + 52, G.ANCHO_TARJETA - 10,
                                           G.ALTO_TARJETA - 58, opciones))
        return tpl_ds, tpls["Plot"]

    # --- Pestañas: barra de navegación y pestaña Variables -------------------------------
    def armar_pestanas(self):
        """Corre después de armar_graficos, que borra lo generado antes (navbar*, tarjetaVar*, etc.)."""
        plano = self.plano
        elems = self.por_nombre(plano, "Text")
        elems.update(self.por_nombre(plano, "Control"))

        def al_frente(nombre, x, y):
            # Se mueve al final de la lista para que se dibuje encima de las tarjetas
            n = elems[nombre]
            plano.removeChild(n)
            plano.appendChild(n)
            self.posicion(n, x, y)

        # Pestaña Variables: fondo, línea del escenario y tarjetas con el tablero de indicadores
        y0 = G.VAR_Y0
        self.rectangulo(plano, "fondoVariables", 0, y0, 1640, 900, fill="F1F5F9", line="CBD5E1")
        pos = G.layout_variables()
        for sufijo, titulo, funcion, _, _, tam in G.VAR_TARJETAS:
            x, y, w, h = pos[sufijo]
            self.rectangulo(plano, f"tarjetaVar{sufijo}", x, y, w, h, fill="FFFFFF", line="CBD5E1")
        for sufijo, titulo, funcion, _, _, tam in G.VAR_TARJETAS:
            x, y, w, h = pos[sufijo]
            if f"titulo{sufijo}" not in elems:
                self.texto(plano, f"titulo{sufijo}", x + 18, y + 12, titulo, size=14, bold=True, color="0F172A")
                self.texto(plano, f"panel{sufijo}", x + 18, y + 36, "-", funcion + "()", size=tam, mono=True,
                           color="1E293B")
            else:
                al_frente(f"titulo{sufijo}", x + 18, y + 12)
                al_frente(f"panel{sufijo}", x + 18, y + 36)
        al_frente("escenario", 30, y0 + G.ALTO_NAVBAR + 16)
        al_frente("botonResumen", 1445, y0 + G.ALTO_NAVBAR + 10)

        # Barra de navegación, igual en las tres pestañas, con la pestaña activa resaltada
        vistas = list(G.VISTAS.items())
        for i, (vista, (vx, vy, vw, _, _)) in enumerate(vistas):
            self.rectangulo(plano, f"navbar{i}Fondo", vx, vy, vw, G.ALTO_NAVBAR, fill="0F172A", line="0F172A")
            self.texto(plano, f"navbar{i}Titulo", vx + 24, vy + 18, "KRETZ", size=18, bold=True, color="FFFFFF")
            for j, (destino, (*_, titulo)) in enumerate(vistas):
                bx = vx + 130 + j * (G.ANCHO_BOTON_PESTANA + 10)
                activa = destino == vista
                self.boton(plano, f"navbar{i}Boton{j}", bx, vy + 13, G.ANCHO_BOTON_PESTANA, titulo,
                           f"{destino}.navigateTo();", fill="2563EB" if activa else "334155")
                if activa:
                    self.rectangulo(plano, f"navbar{i}Activa", bx, vy + G.ALTO_NAVBAR - 5, G.ANCHO_BOTON_PESTANA, 5,
                                    fill="60A5FA", line="60A5FA")
            self.texto(plano, f"navbar{i}Reloj", vx + vw - 20, vy + 20, "Preparando la primera jornada...",
                       "textoReloj()", size=12, bold=True, color="BFDBFE", align="RIGHT")

    # --- Experimentos de réplicas -------------------------------------------------------
    def armar_replicas(self, tpl_ds, tpl_plot):
        exps = self.doc.getElementsByTagName("Experiments")[0]
        pvs = {self.nombre(e): e for e in self.hijos(exps, "ParamVariationExperiment")}
        if not pvs:
            sys.exit("Falta el experimento de Variación de parámetros (Replicas) que sirve de plantilla.")
        plantilla = pvs.get("Replicas") or next(iter(pvs.values()))
        ids = {self.nombre(v): self.hijo(v, "Id").firstChild.data
               for v in self.hijos(self.hijo(self.main, "Variables"), "Variable") if v.getAttribute("Class") == "Parameter"}
        for sim, (titulo, valores) in D.EXPERIMENTOS.items():
            nombre = G.NOMBRES_REPLICAS[sim]
            e = pvs.get(nombre)
            if e is None:
                e = plantilla.cloneNode(True)
                self.hijo(e, "Id").firstChild.data = str(self.nuevo_id())
                exps.appendChild(e)
            self.configurar_replicas(e, nombre, titulo, {**valores, "nombreEscenario": f'"{titulo}"'}, ids,
                                     tpl_ds, tpl_plot)

    def configurar_replicas(self, e, nombre, titulo, valores, ids, tpl_ds, tpl_plot):
        self.hijo(e, "Name").firstChild.data = nombre
        self.poner(e, "RandomNumberGenerationType", "fixedSeed")
        self.poner(e, "SeedValue", 1)
        self.poner(e, "MaximumMemory", 2048)
        self.poner(e, "AllowParallelEvaluations", "true")
        self.poner(e, "UseFreeformParameters", "false")
        # Todos los parámetros fijos; los del escenario con su valor (las réplicas varían la semilla)
        rangos = {self.hijo(r, "Id").firstChild.data: r for r in self.hijos(e, "RangeVariationParamValue")}
        libres = {self.hijo(r, "Id").firstChild.data for r in self.hijos(e, "FreeformParamValue")}
        ancla = self.hijo(e, "ModelTimeProperties")
        for pid in ids.values():
            if pid not in libres:
                f = self.el(None, "FreeformParamValue")
                self.el(f, "Id", pid)
                e.insertBefore(f, ancla)
            if pid not in rangos:
                r = self.el(None, "RangeVariationParamValue")
                self.el(r, "Id", pid)
                self.el(r, "Type", "FIXED")
                e.insertBefore(r, ancla)
                rangos[pid] = r
        for pid, r in rangos.items():
            self.poner(r, "Type", "FIXED")
            for tag in ("Expression", "From", "To", "Step"):
                for h in self.hijos(r, tag):
                    r.removeChild(h)
        for pname, valor in valores.items():
            r = rangos[ids[pname]]
            ex = self.el(r, "Expression", attrs={"Class": "CodeValue"})
            self.el(ex, "Code", valor, cdata=True)
        # La réplica es el único parámetro que varía (1..N): cada iteración usa la semilla N del
        # listado común, así todos los escenarios corren con las mismas semillas
        r = rangos[ids["replica"]]
        self.poner(r, "Type", "RANGE")
        for tag, valor in (("From", 1), ("To", G.REPLICAS), ("Step", 1)):
            v = self.el(r, tag, attrs={"Class": "CodeValue"})
            self.el(v, "Code", valor, cdata=True)
        # Se detiene solo (finishSimulation al terminar las semanas simuladas)
        self.poner_cdata(self.hijo(e, "ModelTimeProperties"), "StopOption", "Never")
        self.poner_cdata(self.hijo(e, "PresentationProperties"), "Title", f"KRETZ | Réplicas: {titulo}")
        rep = self.hijo(e, "ReplicationsProperties")
        # Una corrida por iteración: las réplicas son las iteraciones del parámetro replica
        self.poner(rep, "UseReplication", "false")
        self.poner(rep, "FixedReplicationsNumber", "true")
        self.poner(rep, "ReplicationPerIteration", 1)
        # Código: los data sets se vacían al empezar y suman un punto por réplica
        for tag, codigo in (("BeforeEachExperimentRunCode", G.codigo_antes_replicas()),
                            ("AfterSimulationRunCode", G.codigo_despues_corrida()),
                            ("AfterExperimentCode", G.codigo_fin_experimento(titulo))):
            h = self.hijo(e, tag)
            if h is None:
                h = self.el(None, tag)
                e.insertBefore(h, ancla)
            while h.firstChild is not None:
                h.removeChild(h.firstChild)
            h.appendChild(self.doc.createCDATASection(codigo))
        # Data sets y presentación del experimento
        for tag in ("AnalysisData", "Presentation"):
            for h in self.hijos(e, tag):
                e.removeChild(h)
        analisis = self.el(None, "AnalysisData")
        pres = self.el(None, "Presentation")
        despues = self.hijo(e, "LoadRootFromSnapshot")
        e.insertBefore(pres, despues.nextSibling)
        e.insertBefore(analisis, pres)
        for i, n in enumerate(G.nombres_datasets_replicas()):
            analisis.appendChild(self.data_set(tpl_ds, n, 500, 40 + (i % 4) * 200, 660 + (i // 4) * 25))
        self.rectangulo(pres, "fondoReplicas", 0, 0, 1660, 640, fill="F1F5F9", line="CBD5E1")
        self.texto(pres, "tituloReplicas", 30, 22, f"KRETZ | Réplicas: {titulo}", size=22, bold=True, color="0F172A")
        self.texto(pres, "resumenReplicas", 30, 60, "Réplicas terminadas: 0", G.texto_resumen_replicas(), size=13,
                   bold=True, color="1D4ED8")
        self.texto(pres, "notaReplicas", 30, 84,
                   f"{G.REPLICAS} réplicas con la misma secuencia de semillas en todos los escenarios. "
                   "Cada gráfico muestra la media acumulada de las réplicas terminadas y su intervalo de confianza "
                   "del 95 %: cuando las líneas se estabilizan y se juntan, alcanzan las réplicas.",
                   size=11, color="475569")
        for i, (n, _, titulo_ds, color) in enumerate(G.DATASETS_REPLICAS):
            x = 30 + i * 540
            self.rectangulo(pres, f"tarjetaReplicas{i}", x, 120, 510, 490, fill="FFFFFF", line="CBD5E1")
            self.texto(pres, f"tituloReplicas{i}", x + 18, 132, titulo_ds, size=15, bold=True, color="0F172A")
            self.texto(pres, f"subtituloReplicas{i}", x + 18, 154, "Media acumulada ± IC 95 % según réplicas terminadas",
                       size=11, color="475569")
            pres.appendChild(self.grafico(tpl_plot, f"graficoReplicas{i}", "Plot", x + 5, 175, 500, 425,
                                          {"series": G.series_replicas(n, color), "puntos": "NONE"}))

    def registrar_recurso(self, ruta):
        recursos = self.doc.getElementsByTagName("ModelResources")[0]
        if any(self.hijo(r, "Path").firstChild.data == ruta for r in self.hijos(recursos, "Resource")):
            return
        r = self.el(recursos, "Resource")
        self.el(r, "Id", self.nuevo_id())
        self.el(r, "Path", ruta, cdata=True)
        self.el(r, "ReferencedFromUserCode", "false")
        self.el(r, "Location", "FILE_SYSTEM")

    def requerir_libreria(self, nombre, version):
        refs = self.doc.getElementsByTagName("RequiredLibraryReference")
        if any(self.hijo(r, "LibraryName").firstChild.data == nombre for r in refs):
            return
        ref = self.el(None, "RequiredLibraryReference")
        self.el(ref, "LibraryName", nombre, cdata=True)
        for tag, val in zip(("VersionMajor", "VersionMinor", "VersionBuild"), version):
            self.el(ref, tag, val)
        refs[-1].parentNode.insertBefore(ref, refs[-1].nextSibling)

    def verificar_nombres(self):
        # AnyLogic no abre el modelo si dos elementos de un agente comparten nombre
        for clase in (self.main, self.balanza, self.operario):
            nombres = []
            for tag in ("Variables", "Functions", "Events", "EmbeddedObjects"):
                cont = self.hijo(clase, tag)
                if cont is not None:
                    nombres += [self.nombre(n) for n in self.hijos(cont)]
            _, plano = self.presentacion_nivel(clase)
            if plano is not None:
                nombres += [self.nombre(n) for n in self.hijos(plano)]
            repetidos = sorted({n for n in nombres if n and nombres.count(n) > 1})
            if repetidos:
                sys.exit(f"Nombres repetidos en {self.nombre(clase)}: {', '.join(repetidos)}. No se guardó el modelo.")

    def guardar(self, salida):
        def limpiar(node):
            for ch in list(node.childNodes):
                if ch.nodeType == ch.TEXT_NODE and not ch.data.strip():
                    node.removeChild(ch)
                elif ch.hasChildNodes():
                    limpiar(ch)
        limpiar(self.doc)
        salida.write_bytes(self.doc.toprettyxml(indent="\t", encoding="UTF-8").replace(b"\n", b"\r\n"))


def main():
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--modelo", type=Path, default=raiz / "TPI-Simulacion-KRETZ - copia.alp")
    parser.add_argument("--plano", action="store_true",
                        help="además de sincronizar código y flujo, arma el plano 3D desde las plantillas")
    args = parser.parse_args()
    if any(args.modelo.parent.glob(args.modelo.name + ".autosave")):
        parser.error("Hay un .autosave del modelo: cerralo en AnyLogic (sin guardar o guardando) antes de editar.")
    e = Editor(args.modelo)
    e.sincronizar_codigo()
    e.sincronizar_flujo()
    if args.plano:
        e.armar_plano()
    e.ajustar_racks()
    plantillas = e.armar_graficos()
    e.armar_pestanas()
    e.armar_replicas(*plantillas)
    e.requerir_libreria(D.MHL, (8, 3, 0))
    e.verificar_nombres()
    respaldo = args.modelo.with_suffix(".antes.alp")
    shutil.copy2(args.modelo, respaldo)
    e.guardar(args.modelo)
    print(f"Modelo actualizado: {args.modelo} (copia anterior en {respaldo.name})")


if __name__ == "__main__":
    main()
