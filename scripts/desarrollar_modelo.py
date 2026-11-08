"""Desarrolla el modelo AnyLogic según la especificación (README-Especificacion_1.md).

Lee el modelo base (TPI-Simulacion-KRETZ.alp, que no se modifica) y escribe el
modelo completo en "TPI-Simulacion-KRETZ - copia.alp". Se puede volver a correr
las veces que haga falta: siempre parte del modelo base.

Con --verificar arma un arnés Java con todo el código del modelo y lo compila
contra las librerías de AnyLogic instaladas, para detectar errores antes de
abrir el modelo.

Usa solo la biblioteca estándar de Python.
"""

from pathlib import Path
from xml.dom import minidom
import argparse
import math
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo_java as J  # noqa: E402

PAQUETE = "tpi_simulacion_kretz"
PML = "com.anylogic.libraries.processmodeling"
MHL = "com.anylogic.libraries.material_handling"

# Id del parámetro genérico de cada bloque (Process Modeling y Material Handling Library 8.9)
GENERICOS = {
    "Source": "1412336242928", "Sink": "1412336242929", "Delay": "1412336242930",
    "SelectOutput": "1412336242931", "Seize": "1412336243147", "Release": "1412336243154",
    "Wait": "1412336243169", "ResourcePool": "1412336243135",
    "Store": "1608133547886", "Retrieve": "1608135007245",
}
PAQUETES = {c: MHL if c in ("Store", "Retrieve") else PML for c in GENERICOS}

# ---------------------------------------------------------------------------
# Diagrama de flujo. Cada parámetro: nombre -> (clase de valor, código, unidad)
# y, para el arnés, el tipo de código: ("expr", tipo, args) o ("accion", args)
# ---------------------------------------------------------------------------
AG = [("agent", "Balanza")]
AG_UNIT = [("agent", "Balanza"), ("unit", "Agent")]


def codigo(c, kind=None):
    return ("CodeValue", c, None, kind)


def tiempo(c, args=AG):
    return ("CodeUnitValue", c, ("TimeUnits", "MINUTE"), ("expr", "double", args))


def accion(c, args=AG):
    return ("CodeValue", c, None, ("accion", args))


def expr(c, tipo, args=AG):
    return ("CodeValue", c, None, ("expr", tipo, args))


Y1, Y2, Y3 = 1000, 1080, 1160
BLOQUES = [
    ("fuenteOF", "Source", 40, Y2, {
        "arrivalType": codigo("self.MANUAL"),
        "newEntity": ("Entity", "Balanza", None, None),
        "onAtExit": accion("prepararUnidad((Balanza) agent);", [("agent", "Agent")]),
    }),
    # Racks (Space Markup -> Storage) con la Material Handling Library, sin recursos: la caja
    # entra y sale de la celda al instante, así que no cambian los tiempos del proceso
    ("guardarKit", "Store", 40, Y1, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "storage": expr("almacenMateriales", "RackUnitAggregator"),
        "onEnter": accion("agent.cajaEnRack = true;"),
    }),
    ("tomarOperario", "Seize", 130, Y2, {
        "seizeFromOnePool": codigo("true"),
        "resourcePool": expr("operarios", "ResourcePool"),
        "maximumCapacity": codigo("true"),
        "priority": expr("prioridad(agent)", "double"),
        "customizeResourceChoice": codigo("true"),
        "resourceChoiceCondition": expr("puestoParaPaso(agent, (Operario) unit) >= 0", "boolean",
                                        [("agent", "Balanza"), ("unit", "Agent"), ("pool", "ResourcePool")]),
        "onEnter": accion("agent.tInicioEspera = time();"),
        "onSeizeUnit": accion("alTomarOperario(agent, (Operario) unit);", AG_UNIT),
        "onExit": accion("planificarDespuesDeTomar(agent);"),
    }),
    ("caminar", "Delay", 240, Y2, {
        "delayTime": tiempo("iniciarTramo(agent)"),
        "maximumCapacity": codigo("true"),
        "onExit": accion("finTramo(agent);"),
    }),
    ("masTramos", "SelectOutput", 340, Y2, {
        "conditionIsProbabilistic": codigo("false"),
        "condition": expr("!agent.tramos.isEmpty()", "boolean"),
    }),
    ("irAlRack", "SelectOutput", 430, Y2, {
        "conditionIsProbabilistic": codigo("false"),
        "condition": expr("agent.fase == 1", "boolean"),
    }),
    ("tomarRack", "Seize", 520, Y1, {
        "seizeFromOnePool": codigo("true"),
        "resourcePool": expr("rackMateriales", "ResourcePool"),
        "maximumCapacity": codigo("true"),
    }),
    ("retirarMateriales", "Delay", 620, Y1, {
        "delayTime": tiempo("tiempoAleatorio(tiempoRetiro[agent.tipoModelo])"),
        "maximumCapacity": codigo("true"),
        "onEnter": accion("agent.opActual.estado = 2;", [("agent", "Balanza"), ("delayTime", "double")]),
    }),
    # El kit sale del rack hacia el operario que lo vino a buscar
    ("retirarKit", "Retrieve", 670, 940, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "destinationType": codigo("self.DEST_AGENT"),
        "destinationAgent": expr("agent.opActual", "Agent"),
    }),
    ("liberarRack", "Release", 720, Y1, {
        "releaseMode": codigo("self.SPECIFIED_RESOURCES"),
        "resources": expr("{ rackMateriales }", "ResourcePool[]"),
        "onEnter": accion("agent.fase = 2;\nrecogerCaja(agent);\nplanificarCaminata(agent, pX[agent.puestoActual], pY[agent.puestoActual]);"),
    }),
    ("tarea", "Delay", 520, Y2, {
        "delayTime": tiempo("tiempoTarea(agent)"),
        "maximumCapacity": codigo("true"),
        # El paso avanza aca y no en el Release: quedanPasos se evalua antes de entrar al Release
        "onEnter": accion("agent.opActual.estado = 2;\ndejarCajaEnMesa(agent);\nagent.paso++;",
                          [("agent", "Balanza"), ("delayTime", "double")]),
    }),
    ("liberarOperario", "Release", 620, Y2, {
        "releaseMode": codigo("self.SPECIFIED_RESOURCES"),
        "resources": expr("{ operarios }", "ResourcePool[]"),
        "movingGoHome": expr("false", "boolean", AG_UNIT),
        "onEnter": accion("alLiberarOperario(agent);"),
    }),
    ("quedanPasos", "SelectOutput", 720, Y2, {
        "conditionIsProbabilistic": codigo("false"),
        "condition": expr("agent.paso < recLen[agent.tipoModelo]", "boolean"),
    }),
    ("esPrimero", "SelectOutput", 810, Y2, {
        "conditionIsProbabilistic": codigo("false"),
        "condition": expr("registrarTerminada(agent)", "boolean"),
    }),
    ("guardarCalidad", "Store", 860, 1240, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "storage": expr("almacenCalidad", "RackUnitAggregator"),
        "onEnter": accion("agent.cajaEnRack = true;"),
    }),
    # Las unidades quedan en el rack hasta el cierre de la jornada (cerrarMuestras)
    ("rackCalidad", "Wait", 900, Y3, {
        "maximumCapacity": codigo("true"),
    }),
    # Salen a la mesa del inspector o al frente del rack de stock
    ("retirarCalidad", "Retrieve", 950, 1240, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "destinationType": codigo("self.DEST_XYZ"),
        "destinationX": expr("agent.inspeccionar ? inspectorX : stockFrenteX", "double"),
        "destinationY": expr("agent.inspeccionar ? inspectorY : stockFrenteY", "double"),
        "destinationZ": expr("agent.inspeccionar ? alturaMesa : 0", "double"),
        "onExit": accion("agent.cajaEnRack = false;"),
    }),
    ("aInspeccion", "SelectOutput", 1000, Y3, {
        "conditionIsProbabilistic": codigo("false"),
        "condition": expr("agent.inspeccionar", "boolean"),
    }),
    ("tomarInspector", "Seize", 1100, Y2, {
        "seizeFromOnePool": codigo("true"),
        "resourcePool": expr("inspector", "ResourcePool"),
        "maximumCapacity": codigo("true"),
    }),
    ("inspeccion", "Delay", 1200, Y2, {
        "delayTime": tiempo("tiempoAleatorio(tiempoInspeccionMin)"),
        "maximumCapacity": codigo("true"),
        "onEnter": accion("llevarAInspeccion(agent);", [("agent", "Balanza"), ("delayTime", "double")]),
        "onExit": accion("alFinalizarInspeccion(agent);"),
    }),
    ("liberarInspector", "Release", 1300, Y2, {
        "releaseMode": codigo("self.SPECIFIED_RESOURCES"),
        "resources": expr("{ inspector }", "ResourcePool[]"),
    }),
    ("guardarStock", "Store", 1400, Y2, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "storage": expr("almacenStock", "RackUnitAggregator"),
        "onEnter": accion("agent.cajaEnRack = true;\nalIngresarStock(agent);"),
    }),
    # Producto terminado esperando el despacho (hoy al cierre de cada jornada)
    ("esperaDespacho", "Wait", 1500, Y2, {
        "maximumCapacity": codigo("true"),
    }),
    ("retirarStock", "Retrieve", 1600, Y2, {
        "resourceType": codigo("self.RESOURCE_NONE"),
        "destinationType": codigo("self.DEST_XYZ"),
        "destinationX": expr("despachoX", "double"),
        "destinationY": expr("despachoY", "double"),
        "destinationZ": expr("0", "double"),
        "onExit": accion("agent.cajaEnRack = false;"),
    }),
    ("stock", "Sink", 1700, Y2, {}),
    ("operarios", "ResourcePool", 130, 1250, {
        "capacity": expr("cantidadOperarios()", "int", []),
        "newUnit": ("Entity", "Operario", None, None),
        "speed": ("CodeUnitValue", "velocidadOperario", ("SpeedUnits", "MPS"), ("expr", "double", [])),
        "homeNode": expr("zonaIngreso", "com.anylogic.engine.markup.INode", []),
        "forceStatisticsCollection": codigo("true"),
        "onNewUnit": accion("registrarOperario(unit);", [("unit", "Operario")]),
    }),
    ("rackMateriales", "ResourcePool", 520, 1250, {
        "type": codigo("self.RESOURCE_STATIC"),
        "capacity": expr("capacidadRackMateriales", "int", []),
        "forceStatisticsCollection": codigo("true"),
    }),
    ("inspector", "ResourcePool", 1100, 1250, {
        "type": codigo("self.RESOURCE_STATIC"),
        "capacity": codigo("1"),
        "forceStatisticsCollection": codigo("true"),
    }),
]

# (bloque destino, puerto de entrada, bloque origen, puerto de salida)
CONEXIONES = [
    ("guardarKit", "in", "fuenteOF", "out"),
    ("tomarOperario", "in", "guardarKit", "out"),
    ("caminar", "in", "tomarOperario", "out"),
    ("masTramos", "in", "caminar", "out"),
    ("caminar", "in", "masTramos", "outT"),
    ("irAlRack", "in", "masTramos", "outF"),
    ("tomarRack", "in", "irAlRack", "outT"),
    ("retirarMateriales", "in", "tomarRack", "out"),
    ("retirarKit", "in", "retirarMateriales", "out"),
    ("liberarRack", "in", "retirarKit", "out"),
    ("caminar", "in", "liberarRack", "out"),
    ("tarea", "in", "irAlRack", "outF"),
    ("liberarOperario", "in", "tarea", "out"),
    ("quedanPasos", "in", "liberarOperario", "out"),
    ("tomarOperario", "in", "quedanPasos", "outT"),
    ("esPrimero", "in", "quedanPasos", "outF"),
    ("tomarInspector", "in", "esPrimero", "outT"),
    ("guardarCalidad", "in", "esPrimero", "outF"),
    ("rackCalidad", "in", "guardarCalidad", "out"),
    ("retirarCalidad", "in", "rackCalidad", "out"),
    ("aInspeccion", "in", "retirarCalidad", "out"),
    ("tomarInspector", "in", "aInspeccion", "outT"),
    ("guardarStock", "in", "aInspeccion", "outF"),
    ("inspeccion", "in", "tomarInspector", "out"),
    ("liberarInspector", "in", "inspeccion", "out"),
    ("guardarStock", "in", "liberarInspector", "out"),
    ("esperaDespacho", "in", "guardarStock", "out"),
    ("retirarStock", "in", "esperaDespacho", "out"),
    ("stock", "in", "retirarStock", "out"),
]

ALTO_PAREDES = 48  # 3 m (16 px = 1 m)

# Racks del depósito (Space Markup -> Storage): nombre -> (x, y) en el plano
ALMACENES = {
    "almacenMateriales": (1400, 185),
    "almacenCalidad": (1400, 440),
    "almacenStock": (1480, 300),
}
CAJAS_POR_CELDA = 20
ESTANTES_POR_RACK = 3

# Experimentos de comparación de escenarios: nombre -> (título, {parámetro: valor})
EXPERIMENTOS = {
    "Simulation": ("Escenario actual", {}),
    "EscenarioContratacion": ("Contratar 2 Ajustadores", {"extraAjustadores": "2"}),
    "EscenarioContratacionArmadores": ("Contratar 2 Armadores", {"extraArmadores": "2"}),
    "EscenarioContratacionControlador": ("Contratar 1 Controlador", {"extraControladores": "1"}),
    "EscenarioContratacionEmbalador": ("Contratar 1 Embalador", {"extraEmbaladores": "1"}),
    "EscenarioReserva": ("Personal de reserva polivalente (2)", {"operariosReserva": "2"}),
    "EscenarioReorganizacion": ("Reorganización: 3 armadores + 2 ajustadores por línea",
                                {"armadoresPorLinea": "3", "ajustadoresPorLinea": "2",
                                 "coberturaEntreEspecialidades": "true", "costoReorganizacion": "1500000"}),
    "EscenarioSecuencia": ("Secuencia: procesos largos primero", {"reglaSecuencia": "1"}),
}

# Mesas que se dibujan: 6 columnas de 6, lo que entra en la nave de producción. Los escenarios
# llegan a 32 puestos; si alguno pasara de 36, esos puestos funcionan pero no se dibujan
PUESTOS_DIBUJADOS = 36

# Mesa de la paleta 3D de AnyLogic (Table). AnyLogic la copió a 3d/ al arrastrarla al modelo
MESA_3D = "3d/table.dae"
# El origen del modelo de la mesa está en un borde del lado corto (1,05 m de profundidad):
# girada 90°, se la corre media profundidad para que quede centrada en su lugar
CORRECCION_MESA_X = 8.4


def posicion_puesto(p, v):
    """Misma fórmula que posicionPuestoX/Y en modelo_java.py (columnas de mesas pegadas)."""
    por_columna = int(v["mesasPorColumna"])
    columna = p // por_columna
    x = v["origenPuestosX"] + (columna % 6) * v["separacionColumnas"] + (columna // 6) * v["separacionColumnas"] / 2
    y = v["origenPuestosY"] + (p % por_columna) * v["largoMesa"]
    return x, y


class Generador:
    def __init__(self, base):
        self.doc = minidom.parse(str(base))
        self.next_id = 1796000000000
        self.used = {n.firstChild.data for n in self.doc.getElementsByTagName("Id") if n.firstChild}

    # --- utilidades XML ----------------------------------------------------
    def nuevo_id(self):
        while str(self.next_id) in self.used:
            self.next_id += 1
        self.used.add(str(self.next_id))
        self.next_id += 1
        return self.next_id - 1

    def el(self, parent, tag, text=None, cdata=False, attrs=None):
        node = self.doc.createElement(tag)
        for k, v in (attrs or {}).items():
            node.setAttribute(k, str(v))
        if text is not None:
            node.appendChild(self.doc.createCDATASection(str(text)) if cdata else self.doc.createTextNode(str(text)))
        if parent is not None:
            parent.appendChild(node)
        return node

    @staticmethod
    def hijo(parent, tag):
        return next((n for n in parent.childNodes if n.nodeType == n.ELEMENT_NODE and n.tagName == tag), None)

    @staticmethod
    def hijos(parent, tag=None):
        return [n for n in parent.childNodes if n.nodeType == n.ELEMENT_NODE and (tag is None or n.tagName == tag)]

    def comunes(self, parent, name, x, y, label=(10, 0), public=True, visible=True, show_label=False):
        self.el(parent, "Id", self.nuevo_id())
        self.el(parent, "Name", name, cdata=True)
        self.el(parent, "X", x)
        self.el(parent, "Y", y)
        lab = self.el(parent, "Label")
        self.el(lab, "X", label[0])
        self.el(lab, "Y", label[1])
        self.el(parent, "PublicFlag", str(public).lower())
        self.el(parent, "PresentationFlag", str(visible).lower())
        self.el(parent, "ShowLabel", str(show_label).lower())

    def insertar_antes(self, parent, node, before_tags):
        ref = next((self.hijo(parent, t) for t in before_tags if self.hijo(parent, t) is not None), None)
        if ref is None:
            parent.appendChild(node)
        else:
            parent.insertBefore(node, ref)
        return node

    def renovar_ids(self, node):
        for n in node.getElementsByTagName("Id"):
            n.firstChild.data = str(self.nuevo_id())

    @staticmethod
    def color(hex_color):
        return int(hex_color.removeprefix("#"), 16) - 0x1000000

    # --- variables, parámetros, funciones y eventos -------------------------
    def parametro(self, container, name, tipo, valor, etiqueta, x, y):
        v = self.el(container, "Variable", attrs={"Class": "Parameter"})
        self.comunes(v, name, x, y, public=False, show_label=True)
        p = self.el(v, "Properties", attrs={"SaveInSnapshot": "true", "ModificatorType": "STATIC"})
        self.el(p, "Type", tipo, cdata=True)
        self.el(p, "UnitType", "NONE", cdata=True)
        self.el(p, "SdArray", "false")
        dv = self.el(p, "DefaultValue", attrs={"Class": "CodeValue"})
        self.el(dv, "Code", valor, cdata=True)
        ed = self.el(p, "ParameterEditor")
        self.el(ed, "Id", self.nuevo_id())
        self.el(ed, "Label", etiqueta, cdata=True)
        self.el(ed, "EditorContolType", "CHECK_BOX" if tipo == "boolean" else "TEXT_BOX")
        self.el(ed, "MinSliderValue", "0", cdata=True)
        self.el(ed, "MaxSliderValue", "100", cdata=True)
        self.el(ed, "DelimeterType", "NO_DELIMETER")

    def variable(self, container, name, tipo, inicial, x, y):
        v = self.el(container, "Variable", attrs={"Class": "PlainVariable"})
        self.comunes(v, name, x, y, public=False, show_label=True)
        p = self.el(v, "Properties", attrs={"SaveInSnapshot": "true", "Constant": "false",
                                           "AccessType": "public", "StaticVariable": "false"})
        self.el(p, "Type", tipo, cdata=True)
        iv = self.el(p, "InitialValue", attrs={"Class": "CodeValue"})
        self.el(iv, "Code", inicial, cdata=True)

    def funcion(self, container, name, retorno, params, cuerpo, x, y):
        f = self.el(container, "Function", attrs={"AccessType": "public", "StaticFunction": "false"})
        self.el(f, "ReturnModificator", "VOID" if retorno == "void" else "RETURNS_VALUE")
        self.el(f, "ReturnType", retorno, cdata=True)
        self.comunes(f, name, x, y, public=False, show_label=True)
        for pn, pt in params:
            par = self.el(f, "Parameter")
            self.el(par, "Name", pn, cdata=True)
            self.el(par, "Type", pt, cdata=True)
        self.el(f, "Body", cuerpo, cdata=True)

    def evento(self, container, name, accion_code, x, y):
        e = self.el(container, "Event")
        self.comunes(e, name, x, y, public=False, show_label=True)
        p = self.el(e, "Properties", attrs={"TriggerType": "timeout", "Mode": "userControls"})
        t = self.el(p, "Timeout", attrs={"Class": "CodeUnitValue"})
        self.el(t, "Code", "1", cdata=True)
        self.el(t, "Unit", "MINUTE", cdata=True, attrs={"Class": "TimeUnits"})
        r = self.el(p, "Rate", attrs={"Class": "CodeUnitValue"})
        self.el(r, "Code", "1", cdata=True)
        self.el(r, "Unit", "PER_MINUTE", cdata=True, attrs={"Class": "RateUnits"})
        self.el(p, "Id", self.nuevo_id())
        self.el(p, "OccurrenceAtTime", "true")
        self.el(p, "OccurrenceDate", "1787990400000")
        ot = self.el(p, "OccurrenceTime", attrs={"Class": "CodeUnitValue"})
        self.el(ot, "Code", "0", cdata=True)
        self.el(ot, "Unit", "MINUTE", cdata=True, attrs={"Class": "TimeUnits"})
        rc = self.el(p, "RecurrenceCode", attrs={"Class": "CodeUnitValue"})
        self.el(rc, "Code", "1", cdata=True)
        self.el(rc, "Unit", "MINUTE", cdata=True, attrs={"Class": "TimeUnits"})
        self.el(p, "Condition", "false", cdata=True)
        self.el(e, "Action", accion_code, cdata=True)
        self.el(e, "Logging", "false")

    # --- bloques de la Process Modeling Library -----------------------------
    def bloque(self, container, name, clase, x, y, params, entidades):
        eo = self.el(container, "EmbeddedObject")
        self.comunes(eo, name, x, y, label=(-5, -12), public=False, show_label=True)
        aoc = self.el(eo, "ActiveObjectClass")
        self.el(aoc, "PackageName", PAQUETES[clase], cdata=True)
        self.el(aoc, "ClassName", clase, cdata=True)
        gps = self.el(eo, "GenericParameterSubstitute")
        ref = self.el(gps, "GenericParameterSubstituteReference")
        self.el(ref, "PackageName", PAQUETES[clase], cdata=True)
        self.el(ref, "ClassName", clase, cdata=True)
        self.el(ref, "ItemName", GENERICOS[clase], cdata=True)
        if clase not in ("Source", "ResourcePool"):
            val = self.el(gps, "GenericParameterSubstituteValue", attrs={"Class": "CodeValue"})
            self.el(val, "Code", "Balanza", cdata=True)
        ps = self.el(eo, "Parameters")
        for pname, (vclass, code, unit, _) in params.items():
            par = self.el(ps, "Parameter")
            self.el(par, "Name", pname, cdata=True)
            if vclass == "Entity":
                value = entidades[code].cloneNode(True)
                self.renovar_ids(value)
                par.appendChild(value)
                continue
            value = self.el(par, "Value", attrs={"Class": vclass})
            self.el(value, "Code", code, cdata=True)
            if unit:
                self.el(value, "Unit", unit[1], cdata=True, attrs={"Class": unit[0]})
        self.el(eo, "ReplicationFlag", "false")
        rep = self.el(eo, "Replication", attrs={"Class": "CodeValue"})
        self.el(rep, "Code", "100", cdata=True)
        self.el(eo, "CollectionType", "ARRAY_LIST_BASED")
        self.el(eo, "InitialLocationType", "XYZ")
        for tag, val in (("ColumnCode", "0"), ("RowCode", "0"), ("LocationNameCode", '""')):
            c = self.el(eo, tag, attrs={"Class": "CodeValue"})
            self.el(c, "Code", val, cdata=True)
        self.el(eo, "InitializationType", "SPECIFIED_NUMBER")
        q = self.el(eo, "InitializationDatabaseTableQuery")
        self.el(q, "Id", self.nuevo_id())
        self.el(q, "TableReference")
        self.el(eo, "InitializationDatabaseType", "ONE_AGENT_PER_DATABASE_RECORD")
        self.el(eo, "QuantityColumn")

    def conector(self, container, n, destino, puerto_in, origen, puerto_out, clases, posiciones):
        c = self.el(container, "Connector")
        self.comunes(c, f"conector{n}", 0, 0, public=False)
        for tag, blk in (("SourceEmbeddedObjectReference", destino), ("TargetEmbeddedObjectReference", origen)):
            r = self.el(c, tag)
            self.el(r, "PackageName", PAQUETE, cdata=True)
            self.el(r, "ClassName", "Main", cdata=True)
            self.el(r, "ItemName", blk, cdata=True)
        for tag, blk, port in (("SourceConnectableItemReference", destino, puerto_in),
                               ("TargetConnectableItemReference", origen, puerto_out)):
            r = self.el(c, tag)
            self.el(r, "PackageName", PAQUETES[clases[blk]], cdata=True)
            self.el(r, "ClassName", clases[blk], cdata=True)
            self.el(r, "ItemName", port, cdata=True)
        pts = self.el(c, "Points")
        (xi, yi), (xo, yo) = posiciones[destino], posiciones[origen]
        for x, y in ((xi, yi + 10), (xo + 40, yo + 10)):
            p = self.el(pts, "Point")
            self.el(p, "X", x)
            self.el(p, "Y", y)

    # --- formas de presentación ----------------------------------------------
    def dinamicos(self, node, xcode=None, ycode=None, visible=None):
        if xcode:
            self.el(node, "XCode", xcode, cdata=True)
        if ycode:
            self.el(node, "YCode", ycode, cdata=True)
        if visible:
            self.el(node, "VisibleCode", visible, cdata=True)

    def texto(self, container, name, x, y, valor, codigo_texto=None, size=12, color="334155", bold=False,
              mono=False, xcode=None, ycode=None, visible=None, draw="SHAPE_DRAW_2D", align="LEFT", rotacion=0.0):
        t = self.el(container, "Text")
        self.comunes(t, name, x, y, label=(0, -10))
        self.el(t, "DrawMode", draw)
        self.dinamicos(t, xcode, ycode, visible)
        self.el(t, "EmbeddedIcon", "false")
        self.el(t, "Z", 0)
        self.el(t, "Rotation", rotacion)
        self.el(t, "Color", self.color(color))
        self.el(t, "Text", valor, cdata=True)
        if codigo_texto:
            self.el(t, "TextCode", codigo_texto, cdata=True)
        f = self.el(t, "Font")
        self.el(f, "Name", "Monospaced" if mono else "SansSerif")
        self.el(f, "Size", size)
        self.el(f, "Style", 1 if bold else 0)
        self.el(t, "Alignment", align)

    def rectangulo(self, container, name, x, y, w, h, fill="FFFFFF", line="CBD5E1", fill_code=None,
                   xcode=None, ycode=None, visible=None, draw="SHAPE_DRAW_2D", line_width=1, z=0, alto=None):
        r = self.el(container, "Rectangle")
        self.comunes(r, name, x, y)
        self.el(r, "DrawMode", draw)
        self.dinamicos(r, xcode, ycode, visible)
        self.el(r, "EmbeddedIcon", "false")
        self.el(r, "Z", z)
        self.el(r, "ZHeight", alto if alto is not None else (4 if draw != "SHAPE_DRAW_2D" else 0))
        self.el(r, "LineWidth", line_width)
        self.el(r, "LineColor", self.color(line))
        self.el(r, "LineMaterial", "null")
        self.el(r, "LineStyle", "SOLID")
        self.el(r, "Width", w)
        self.el(r, "Height", h)
        self.el(r, "Rotation", "0.0")
        self.el(r, "FillColor", self.color(fill))
        if fill_code:
            self.el(r, "FillColorCode", fill_code, cdata=True)
        self.el(r, "FillMaterial", "null")

    def ovalo(self, container, name, radio, fill_code, line_code):
        o = self.el(container, "Oval")
        self.comunes(o, name, 0, 0, label=(0, 0))
        self.el(o, "DrawMode", "SHAPE_DRAW_2D3D")
        self.el(o, "EmbeddedIcon", "false")
        self.el(o, "Z", 0)
        self.el(o, "ZHeight", 2)
        self.el(o, "LineWidth", 2)
        self.el(o, "LineColor", self.color("0F172A"))
        self.el(o, "LineColorCode", line_code, cdata=True)
        self.el(o, "LineMaterial", "null")
        self.el(o, "LineStyle", "SOLID")
        self.el(o, "RadiusX", radio)
        self.el(o, "RadiusY", radio)
        self.el(o, "Rotation", "0.0")
        self.el(o, "FillColor", self.color("A0A8B4"))
        self.el(o, "FillColorCode", fill_code, cdata=True)
        self.el(o, "FillMaterial", "null")

    def figura3d(self, container, name, x, y, recurso, rotacion=0.0, visible=None):
        # Misma estructura que guarda AnyLogic para un objeto de la paleta 3D (ver worker en Operario)
        f = self.el(container, "Figure3D")
        self.comunes(f, name, x, y, label=(0, -10))
        self.el(f, "DrawMode", "SHAPE_DRAW_3D")
        self.dinamicos(f, visible=visible)
        self.el(f, "Z", 0)
        ref = self.el(f, "ResourceReference")
        self.el(ref, "PackageName", PAQUETE, cdata=True)
        self.el(ref, "ClassName", recurso, cdata=True)
        self.el(f, "ColorTable")
        self.el(f, "AutoScale", "true")
        self.el(f, "Scale", "1.0")
        self.el(f, "Rotation", rotacion)
        self.el(f, "AxisOrder", "YZX_AXIS_ORDER")
        self.el(f, "SelectedAnimationPose", "")
        self.el(f, "ApplyShading", "true")
        self.el(f, "InternalLighting", "OFF")
        self.el(f, "IgnoreSceneLights", "false")

    def rack3d(self, container, name, x, y, w, h, niveles=3, alto_nivel=16, color="92400E", cajas=True):
        # Rack armado con formas 3D: cuatro parantes, estantes y cajas de materiales. Todas las
        # piezas caen en el mismo lugar del plano, así que en 2D se ve solo la planta del rack
        alto = niveles * alto_nivel
        self.rectangulo(container, f"{name}Planta", x, y, w, h, fill=color, line="451A03")
        for i, (px, py) in enumerate(((x, y), (x + w - 3, y), (x, y + h - 3), (x + w - 3, y + h - 3))):
            self.rectangulo(container, f"{name}Parante{i}", px, py, 3, 3, fill="475569", line="334155",
                            draw="SHAPE_DRAW_3D", alto=alto)
        for n in range(niveles):
            self.rectangulo(container, f"{name}Estante{n}", x, y, w, h, fill=color, line="451A03",
                            draw="SHAPE_DRAW_3D", z=n * alto_nivel, alto=2)
            if cajas:
                for k in range(int(w // 14)):
                    self.rectangulo(container, f"{name}Caja{n}_{k}", x + 3 + k * 14, y + 3, 10, h - 6,
                                    fill="C8A165", line="7C5A2A", draw="SHAPE_DRAW_3D",
                                    z=n * alto_nivel + 2, alto=8)

    def registrar_recurso(self, ruta):
        recursos = self.doc.getElementsByTagName("ModelResources")[0]
        for r in self.hijos(recursos, "Resource"):
            if self.hijo(r, "Path").firstChild.data == ruta:
                return
        r = self.el(recursos, "Resource")
        self.el(r, "Id", self.nuevo_id())
        self.el(r, "Path", ruta, cdata=True)
        self.el(r, "ReferencedFromUserCode", "false")
        self.el(r, "Location", "FILE_SYSTEM")

    def boton(self, container, name, x, y, width, label, action):
        b = self.el(container, "Control", attrs={"Type": "Button"})
        self.el(b, "EmbeddedIcon", "false")
        self.comunes(b, name, x, y)
        self.el(b, "DrawMode", "SHAPE_DRAW_2D")
        basic = self.el(b, "BasicProperties", attrs={"Width": width, "Height": 30})
        self.el(basic, "EmbeddedIcon", "false")
        self.el(basic, "FillColor", self.color("2563EB"))
        self.el(basic, "TextColor", -1)
        self.el(basic, "Enabled", "true")
        self.el(basic, "ActionCode", action, cdata=True)
        ext = self.el(b, "ExtendedProperties")
        self.el(ext, "Font", attrs={"Name": "SansSerif", "Size": 13, "Style": 0})
        self.el(ext, "LabelText", label, cdata=True)

    # --- construcción ---------------------------------------------------------
    def clase(self, nombre):
        clases = self.doc.getElementsByTagName("ActiveObjectClasses")[0]
        return next(c for c in self.hijos(clases, "ActiveObjectClass") if self.hijo(c, "Name").firstChild.data == nombre)

    @staticmethod
    def presentacion_nivel(clase):
        pres = Generador.hijo(clase, "Presentation")
        level = Generador.hijo(pres, "Level")
        inner = Generador.hijo(level, "Presentation")
        return level, inner

    def construir(self, salida):
        main = self.clase("Main")
        balanza = self.clase("Balanza")
        operario = self.clase("Operario")
        main_id = self.hijo(main, "Id").firstChild.data

        # Especialidad polivalente para el personal de reserva
        for ol in self.doc.getElementsByTagName("OptionList"):
            if self.hijo(ol, "Name").firstChild.data == "Especialidad":
                op = self.el(ol, "Option")
                self.el(op, "Id", self.nuevo_id())
                self.el(op, "Name", "Polivalente", cdata=True)

        # Entidades (Balanza / Operario) tomadas del modelo base
        entidades = {}
        viejos = self.hijo(main, "EmbeddedObjects")
        for eo in self.hijos(viejos, "EmbeddedObject"):
            for par in eo.getElementsByTagName("Parameter"):
                nombre = self.hijo(par, "Name").firstChild.data
                valor = self.hijo(par, "Value")
                if nombre in ("newEntity", "newUnit") and valor is not None:
                    cls = valor.getElementsByTagName("ClassName")[0].firstChild.data
                    entidades.setdefault(cls, valor.cloneNode(True))
        assert {"Balanza", "Operario"} <= set(entidades), entidades.keys()

        # Se reemplaza el flujo de una sola línea (AILA) por el modelo completo
        main.removeChild(viejos)
        main.removeChild(self.hijo(main, "Connectors"))
        level, plano = self.presentacion_nivel(main)
        nodos = self.hijos(plano, "RectangleNode")
        plantilla_nodo = nodos[0].cloneNode(True)
        for n in nodos:
            plano.removeChild(n)

        # Código de arranque (va justo después del nombre, como lo guarda AnyLogic)
        startup = self.el(None, "StartupCode", J.STARTUP, cdata=True)
        main.insertBefore(startup, self.hijo(main, "Generic"))

        orden = ["Connectors", "Events", "Functions", "AgentLinks", "EmbeddedObjects", "Presentation"]
        variables = self.insertar_antes(main, self.el(None, "Variables"), ["Connectors"] + orden)
        for i, (n, t, v, etiqueta) in enumerate(J.PARAMETROS):
            self.parametro(variables, n, t, v, etiqueta, 1820 + (i // 20) * 260, 40 + (i % 20) * 22)
        for i, (n, t, v) in enumerate(J.VARIABLES_MAIN):
            self.variable(variables, n, t, v, 2340 + (i // 30) * 220, 40 + (i % 30) * 22)
        conectores = self.insertar_antes(main, self.el(None, "Connectors"), orden[1:])
        eventos = self.insertar_antes(main, self.el(None, "Events"), orden[2:])
        for i, (n, a) in enumerate(J.EVENTOS):
            self.evento(eventos, n, a, 1820, 520 + i * 25)
        funciones = self.insertar_antes(main, self.el(None, "Functions"), orden[3:])
        for i, (n, (ret, params, cuerpo)) in enumerate(J.FUNCIONES_MAIN.items()):
            self.funcion(funciones, n, ret, params, cuerpo, 2800 + (i // 30) * 220, 40 + (i % 30) * 22)
        bloques = self.insertar_antes(main, self.el(None, "EmbeddedObjects"), ["Presentation"])
        clases = {}
        posiciones = {}
        for name, cls, x, y, params in BLOQUES:
            self.bloque(bloques, name, cls, x, y, params, entidades)
            clases[name] = cls
            posiciones[name] = (x, y)
        for i, con in enumerate(CONEXIONES):
            self.conector(conectores, i, *con, clases, posiciones)

        # Nodo de ingreso (home del ResourcePool), a partir de un nodo del modelo base
        nodo = plantilla_nodo
        self.renovar_ids(nodo)
        self.hijo(nodo, "Name").firstChild.data = "zonaIngreso"
        self.hijo(nodo, "X").firstChild.data = "1128"
        self.hijo(nodo, "Y").firstChild.data = "530"
        for slope in nodo.getElementsByTagName("Slope"):
            self.hijo(slope, "Name").firstChild.data = "zonaIngresoPendiente"
        self.hijo(nodo, "Width").firstChild.data = "80"
        self.hijo(nodo, "Height").firstChild.data = "26"
        plano.appendChild(nodo)

        self.paredes(plano)
        self.presentacion_main(plano)

        # Balanza y Operario
        vb = self.hijo(balanza, "Variables")
        for i, (n, t, v) in enumerate(J.VARIABLES_BALANZA):
            self.variable(vb, n, t, v, 50 + (i // 15) * 200, 90 + (i % 15) * 22)
        vo = self.hijo(operario, "Variables")
        for i, (n, t, v) in enumerate(J.VARIABLES_OPERARIO):
            self.variable(vo, n, t, v, 50 + (i // 15) * 200, 90 + (i % 15) * 22)
        fo = self.insertar_antes(operario, self.el(None, "Functions"), ["AgentLinks"])
        for i, (n, (ret, params, cuerpo)) in enumerate(J.FUNCIONES_OPERARIO.items()):
            self.funcion(fo, n, ret, params, cuerpo, 300, 90 + i * 22)
        _, plano_op = self.presentacion_nivel(operario)
        self.ovalo(plano_op, "marcaOperario", 6, "colorEstado()", "colorEspecialidad()")

        # Cada unidad se ve como una caja del color de su modelo (0,6 m de lado)
        nivel_b, plano_b = self.presentacion_nivel(balanza)
        if plano_b is None:
            plano_b = self.el(nivel_b, "Presentation")
        self.rectangulo(plano_b, "caja", -5, -5, 10, 10, fill="C8A165", line="7C5A2A", fill_code="color",
                        visible="mostrarCaja", draw="SHAPE_DRAW_2D3D", alto=8)

        self.experimentos(main_id)

        def limpiar(node):
            for ch in list(node.childNodes):
                if ch.nodeType == ch.TEXT_NODE and not ch.data.strip():
                    node.removeChild(ch)
                elif ch.hasChildNodes():
                    limpiar(ch)
        limpiar(self.doc)
        salida.write_bytes(self.doc.toprettyxml(indent="\t", encoding="UTF-8").replace(b"\n", b"\r\n"))
        print(f"Modelo escrito: {salida}")

    def paredes(self, plano):
        # Las paredes del modelo base se dejan como están: AnyLogic guarda cada vértice
        # como tres puntos (el vértice y sus dos manijas de curvatura), y una lista que
        # no respeta ese formato hace fallar la apertura del modelo. Solo se las sube
        # a 3 m de alto para la vista 3D
        for w in self.hijos(plano, "Wall"):
            self.hijo(w, "ZHeight").firstChild.data = str(ALTO_PAREDES)

    def presentacion_main(self, plano):
        # Tablero de indicadores sobre la parte izquierda del plano
        self.rectangulo(plano, "fondoTablero", 15, 15, 905, 860, fill="F8FAFC", line="CBD5E1")
        self.texto(plano, "tituloTablero", 35, 28, "KRETZ | Línea de producción y depósito", size=22, bold=True, color="0F172A")
        self.boton(plano, "botonResumen", 735, 26, 165, "Resumen en consola", "traceln(resumenTexto());")
        self.texto(plano, "reloj", 35, 64, "Preparando la primera jornada...", "textoReloj()", size=13, color="1D4ED8", bold=True)
        self.texto(plano, "escenario", 35, 86, "Escenario", "textoEscenario()", size=11, color="475569")
        secciones = [
            ("tituloOF", 112, "Orden de fabricación del día", "textoOF", 136, 12),
            ("tituloPersonal", 262, "Personal, asistencia y coberturas", "textoPersonal", 286, 11),
            ("tituloColas", 362, "Colas y avance", "textoColas", 386, 11),
            ("tituloCalidad", 428, "Control de calidad por muestreo y tiempos por modelo", "textoCalidad", 452, 11),
            ("tituloCostos", 548, "Cumplimiento de la OF y costos", "textoCostos", 572, 11),
            ("tituloHistorial", 652, "Historial de jornadas", "textoHistorial", 676, 10),
        ]
        for nombre, y, titulo, funcion, y_texto, size in secciones:
            self.texto(plano, nombre, 35, y, titulo, size=14, bold=True, color="0F172A")
            self.texto(plano, nombre.replace("titulo", "panel"), 35, y_texto, "-", funcion + "()", size=size,
                       mono=True, color="1E293B")

        # Referencias de la planta
        self.texto(plano, "rotuloProduccion", 955, 150, "PLANTA DE PRODUCCIÓN", size=12, bold=True, color="0F172A")
        self.texto(plano, "rotuloDeposito", 1290, 150, "DEPÓSITO", size=12, bold=True, color="0F172A")
        # Puestos: columnas de mesas 3D (Table de la paleta de AnyLogic) pegadas a lo largo del eje Y.
        # El modelo de la mesa mide 2,5 m x 1,05 m con el lado largo en X, así que se la gira 90°
        # y se corrige su origen, que está en un borde y no en el centro del lado corto
        v = {n: float(val) for n, _, val in J.VARIABLES_MAIN
             if n in ("origenPuestosX", "origenPuestosY", "mesasPorColumna", "separacionColumnas", "largoMesa",
                      "mesaOffset", "alturaMesa")}
        self.registrar_recurso(MESA_3D)
        for p in range(PUESTOS_DIBUJADOS):
            x, y = posicion_puesto(p, v)
            mx = x - v["mesaOffset"]
            visible = f"nPuestos > {p}"
            self.figura3d(plano, f"mesa{p}", mx + CORRECCION_MESA_X, y, MESA_3D, rotacion=round(math.pi / 2, 6),
                          visible=visible)
            # Tablero de la mesa con el color del estado del puesto
            self.rectangulo(plano, f"puesto{p}", mx - 7, y - 18, 14, 36, fill="AFE1BE", line="334155",
                            fill_code=f"colorPuesto({p})", xcode=f"pX[{p}] - mesaOffset - 7", ycode=f"pY[{p}] - 18",
                            visible=visible, draw="SHAPE_DRAW_2D3D", z=v["alturaMesa"], alto=1)
            self.texto(plano, f"siglaPuesto{p}", mx, y, "", f"etiquetaPuesto({p})", size=7, color="0F172A",
                       xcode=f"pX[{p}] - mesaOffset + 3", ycode=f"pY[{p}]", visible=visible, align="CENTER",
                       rotacion=round(-math.pi / 2, 6))
        self.rack3d(plano, "rackDeMateriales", 1425, 210, 70, 22)
        self.texto(plano, "rotuloRack", 1460, 196, "Rack único de materiales", size=9, color="0F172A", align="CENTER")
        self.texto(plano, "usoRack", 1460, 256, "", '"en uso " + rackMateriales.busy() + "/" + rackMateriales.size()',
                   size=9, color="0F172A", align="CENTER")
        # Rack de espera de calidad: las cajas terminadas se apoyan en sus estantes (ubicarEnRackCalidad)
        self.rack3d(plano, "rackDeCalidad", 1455, 470, 90, 24, color="1D4ED8", cajas=False)
        self.texto(plano, "rotuloRackCalidad", 1500, 500, "", '"Rack espera calidad: " + rackCalidad.size()',
                   size=9, color="0F172A", align="CENTER")
        self.figura3d(plano, "mesaInspector", 1500 + CORRECCION_MESA_X, 439, MESA_3D, rotacion=round(math.pi / 2, 6))
        self.rectangulo(plano, "puestoInspector", 1493, 421, 14, 36, fill="0D9488", line="134E4A",
                        fill_code="inspector.busy() > 0 ? new Color(13, 148, 136) : new Color(153, 246, 228)",
                        draw="SHAPE_DRAW_2D3D", z=v["alturaMesa"], alto=1)
        self.texto(plano, "rotuloInspector", 1500, 412, "Inspector", size=9, color="0F172A", align="CENTER")
        self.rack3d(plano, "stockProductoTerminado", 1520, 290, 55, 90, niveles=4, color="64748B")
        self.texto(plano, "rotuloStock", 1547, 386, "", '"Stock: " + sumar(enStock)', size=9, color="0F172A", align="CENTER")
        self.rectangulo(plano, "zonaAusentes", 950, 588, 160, 46, fill="FEE2E2", line="DC2626")
        self.texto(plano, "rotuloAusentes", 952, 576, "Ausentes", size=9, bold=True, color="991B1B")
        self.rectangulo(plano, "zonaReserva", 1128, 530, 80, 26, fill="E0E7FF", line="4338CA")
        self.texto(plano, "rotuloReserva", 1130, 518, "Reserva", size=9, bold=True, color="3730A3")
        self.texto(plano, "leyenda", 1150, 600,
                   "Puestos (color sobre la mesa): verde = trabajando · verde claro = ocioso · naranja = cubierto por otro · rojo = vacante\n"
                   "Cajas: azul AILA 30KG · naranja REPORT LT · verde NOVEL ECO · violeta LURA · rojo AURA\n"
                   "Operarios: relleno verde = trabaja · amarillo = camina · gris = libre · rojo = ausente;"
                   " borde = especialidad (azul Armador, violeta Ajustador, verde azulado Controlador, marrón Embalador)",
                   size=9, color="0F172A")
        self.texto(plano, "rotuloFlujo", 40, 960, "Flujo del proceso (Process Modeling Library)", size=14, bold=True, color="0F172A")

    def experimentos(self, main_id):
        exps = self.doc.getElementsByTagName("Experiments")[0]
        base = self.hijos(exps, "SimulationExperiment")[0]
        plantilla = base.cloneNode(True)
        exps.removeChild(base)
        for nombre, (titulo, valores) in EXPERIMENTOS.items():
            valores = {**valores, "nombreEscenario": f'"{titulo}"'}
            e = plantilla.cloneNode(True)
            self.renovar_ids(e)
            self.hijo(e, "Name").firstChild.data = nombre
            for t in e.getElementsByTagName("Text"):
                if t.firstChild is not None and t.firstChild.nodeType == t.CDATA_SECTION_NODE:
                    t.firstChild.data = f"KRETZ | {titulo}"
            props = self.hijo(e, "PresentationProperties")
            self.hijo(props, "Title").firstChild.data = f"KRETZ | {titulo}"
            self.hijo(props, "RealTimeScale").firstChild.data = "30.0"
            pars = self.hijo(e, "Parameters")
            for n, _, _, _ in J.PARAMETROS:
                p = self.el(pars, "Parameter")
                self.el(p, "ParameterName", n, cdata=True)
                if n in valores:
                    v = self.el(p, "ParameterValue", attrs={"Class": "CodeValue"})
                    self.el(v, "Code", valores[n], cdata=True)
            exps.appendChild(e)


# ---------------------------------------------------------------------------
# Arnés de compilación: reproduce cómo AnyLogic genera el código Java
# ---------------------------------------------------------------------------
def arnes(destino):
    destino.mkdir(parents=True, exist_ok=True)
    pkg = destino / PAQUETE
    pkg.mkdir(exist_ok=True)
    imports = ("package %s;\nimport java.util.*;\nimport java.awt.Color;\nimport com.anylogic.engine.*;\n"
               "import com.anylogic.engine.markup.*;\nimport com.anylogic.libraries.processmodeling.*;\n"
               "import com.anylogic.libraries.material_handling.*;\n"
               "import static com.anylogic.engine.Utilities.*;\n" % PAQUETE)
    (pkg / "Especialidad.java").write_text(imports + "public enum Especialidad { Armador, Ajustador, Controlador, Embalador, Polivalente }\n", encoding="utf-8")

    def campos(variables):
        return "".join(f"  public {t} {n} = {v};\n" for n, t, v in variables)

    def metodos(funciones):
        salida = ""
        for n, (ret, params, cuerpo) in funciones.items():
            firma = ", ".join(f"{pt} {pn}" for pn, pt in params)
            salida += f"  public {ret} {n}({firma}) {{\n{cuerpo}\n  }}\n"
        return salida

    (pkg / "Balanza.java").write_text(imports + "public abstract class Balanza extends Agent {\n"
        "  public String modelo = \"AILA 30KG\";\n  public void set_modelo(String v) { modelo = v; }\n"
        + campos(J.VARIABLES_BALANZA)
        + "  void presentacion() { Color c = color; boolean v = mostrarCaja; }\n}\n", encoding="utf-8")
    (pkg / "Operario.java").write_text(imports + "public abstract class Operario extends Agent {\n"
        "  public Especialidad especialidad = Especialidad.Armador;\n"
        + campos(J.VARIABLES_OPERARIO) + metodos(J.FUNCIONES_OPERARIO)
        + "  void presentacion() { Color a = colorEstado(); Color b = colorEspecialidad(); }\n}\n", encoding="utf-8")

    m = imports + "public abstract class Main extends Agent {\n"
    m += "".join(f"  public {t} {n} = {v};\n" for n, t, v, _ in J.PARAMETROS)
    m += campos(J.VARIABLES_MAIN)
    m += "".join(f"  public EventTimeout {n};\n" for n, _ in J.EVENTOS)
    m += "  public RectangularNode zonaIngreso;\n"
    m += "  public Level level;\n"
    m += "".join(f"  public Storage {n};\n" for n in ALMACENES)
    tipos = {"Source": "Source<Balanza>", "Seize": "Seize<Balanza>", "Delay": "Delay<Balanza>",
             "Release": "Release<Balanza>", "SelectOutput": "SelectOutput<Balanza>", "Wait": "Wait<Balanza>",
             "Sink": "Sink<Balanza>", "ResourcePool": "ResourcePool<Agent>",
             "Store": "Store<Balanza>", "Retrieve": "Retrieve<Balanza>"}
    m += "".join(f"  public {tipos[c]} {n};\n" for n, c, _, _, _ in BLOQUES)
    m += metodos(J.FUNCIONES_MAIN)
    m += f"  void startup() {{\n{J.STARTUP}\n  }}\n"
    for n, a in J.EVENTOS:
        m += f"  void accion_{n}() {{\n{a}\n  }}\n"
    k = 0
    for n, c, _, _, params in BLOQUES:
        for pn, (_, code, _, kind) in params.items():
            if kind is None:
                continue
            k += 1
            if kind[0] == "expr":
                _, tipo, args = kind
                firma = ", ".join(f"{t} {a}" for a, t in args)
                # AnyLogic convierte los inicializadores de arreglo en "new Tipo[] { ... }"
                valor = f"new {tipo} {code}" if tipo.endswith("[]") and code.startswith("{") else code
                m += f"  {tipo} p{k}_{n}_{pn}({firma}) {{ return {valor}; }}\n"
            else:
                _, args = kind
                firma = ", ".join(f"{t} {a}" for a, t in args)
                m += f"  void p{k}_{n}_{pn}({firma}) {{\n{code}\n  }}\n"
    # Expresiones de la presentación
    m += "  void presentacion() {\n    Object o;\n"
    for e in ["textoReloj()", "textoEscenario()", "textoOF()", "textoPersonal()", "textoColas()", "textoCalidad()",
              "textoCostos()", "textoHistorial()", "nombreLinea(0)", "lineasArmado + lineasCF > 0",
              "colorPuesto(0)", "pX[0] - mesaOffset - 7", "pY[0] - 18", "pX[0] - mesaOffset + 3", "nPuestos > 0", "etiquetaPuesto(0)",
              '"en uso " + rackMateriales.busy() + "/" + rackMateriales.size()', '"Rack espera calidad: " + rackCalidad.size()',
              "inspector.busy() > 0 ? new Color(13, 148, 136) : new Color(153, 246, 228)", '"Stock: " + sumar(enStock)']:
        m += f"    o = {e};\n"
    m += "    traceln(resumenTexto());\n  }\n}\n"
    (pkg / "Main.java").write_text(m, encoding="utf-8")
    return pkg


def verificar(destino):
    instalacion = Path(r"C:\Program Files\AnyLogic 8.9 Personal Learning Edition")
    javac = instalacion / "jre" / "bin" / "javac.exe"
    plugins = instalacion / "plugins"
    jars = [str(p) for p in plugins.glob("com.anylogic.engine*/*.jar")]
    jars += [str(p) for p in plugins.glob("com.anylogic.process_modeling_library_*/lib/*.jar")]
    jars += [str(p) for p in plugins.glob("com.anylogic.material_handling_library_*/lib/*.jar")]
    jars += [str(p) for p in plugins.glob("com.anylogic.libraries.modules_*/lib/*/*.jar")]
    pkg = arnes(destino)
    fuentes = [str(p) for p in pkg.glob("*.java")]
    salida = destino / "clases"
    salida.mkdir(exist_ok=True)
    r = subprocess.run([str(javac), "-encoding", "UTF-8", "-nowarn", "-proc:none", "-d", str(salida), "-cp", ";".join(jars)] + fuentes,
                       capture_output=True, text=True)
    print(r.stdout + r.stderr)
    print("Compilación OK" if r.returncode == 0 else "Compilación con errores")
    return r.returncode == 0


def main():
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=raiz / "TPI-Simulacion-KRETZ.alp")
    parser.add_argument("--salida", type=Path, default=raiz / "TPI-Simulacion-KRETZ - copia.alp")
    parser.add_argument("--verificar", type=Path, metavar="CARPETA",
                        help="compila el código del modelo en CARPETA contra las librerías de AnyLogic")
    parser.add_argument("--forzar", action="store_true",
                        help="regenera el modelo desde el base aunque pise lo editado a mano en AnyLogic")
    args = parser.parse_args()
    if args.verificar:
        sys.exit(0 if verificar(args.verificar) else 1)
    if args.entrada.resolve() == args.salida.resolve():
        parser.error("La salida debe ser distinta del modelo base.")
    # El modelo ahora se edita también en AnyLogic (mesas, cajas y racks): los cambios se
    # aplican con editar_alp.py, y regenerarlo desde el base perdería esos elementos
    if args.salida.exists() and not args.forzar:
        parser.error(f"{args.salida.name} ya existe y puede tener cambios hechos en AnyLogic. "
                     "Usá scripts/editar_alp.py para actualizarlo, o --forzar para regenerarlo desde cero.")
    Generador(args.entrada).construir(args.salida)


if __name__ == "__main__":
    main()
