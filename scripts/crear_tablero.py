"""Crea una copia del modelo con indicadores nativos de AnyLogic 8.9.9.

Usa solo la biblioteca estándar de Python. El modelo de entrada no se modifica.
"""

from pathlib import Path
from xml.dom import minidom
import argparse


STAGES = [
    ("ArmadoP1", "Armado 1", "res_ArmadoP1"),
    ("ArmadoP2", "Armado 2", "res_ArmadoP2"),
    ("ArmadoP3", "Armado 3", "res_ArmadoP3"),
    ("ArmadoP4", "Armado 4", "res_ArmadoP4"),
    ("Ajuste", "Ajuste", "res_Ajuste"),
    ("ControlFinal", "Control final", "res_ControlFinal"),
    ("Embalaje", "Embalaje", "res_Embalaje"),
]

MAIN_VARIABLES = [
    ("tableroIngresadas", "int", "0"),
    ("tableroTerminadas", "int", "0"),
    ("tableroSumaTiempoTotal", "double", "0"),
    ("tableroMaxTiempoTotal", "double", "0"),
    ("tableroSumaEsperaTotal", "double", "0"),
    ("tableroPrimeraSalida", "double", "-1"),
    ("tableroUltimaSalida", "double", "-1"),
    ("tableroSumaEsperaPuesto", "double[]", "new double[7]"),
    ("tableroIniciadasPuesto", "int[]", "new int[7]"),
    ("tableroSumaEsperaCola", "double", "0"),
    ("tableroSalidasCola", "int", "0"),
]

BALANZA_VARIABLES = [
    ("tiempoIngresoTablero", "double", "0"),
    ("inicioEsperaTablero", "double", "0"),
    ("inicioEsperaColaTablero", "double", "0"),
    ("esperaAcumuladaTablero", "double", "0"),
]

FUNCTIONS = {
    "tableroRitmoSalidas": ("double", [], """return tableroTerminadas > 1 && tableroUltimaSalida > tableroPrimeraSalida
    ? (tableroTerminadas - 1) * 60.0 / (tableroUltimaSalida - tableroPrimeraSalida)
    : 0.0;"""),
    "tableroTiempoMedio": ("double", [], """return tableroTerminadas > 0 ? tableroSumaTiempoTotal / tableroTerminadas : 0.0;"""),
    "tableroEsperaMedia": ("double", [], """return tableroTerminadas > 0 ? tableroSumaEsperaTotal / tableroTerminadas : 0.0;"""),
    "tableroEsperandoAhora": ("int", [], """return queue.size() + ArmadoP1.queueSize() + ArmadoP2.queueSize()
    + ArmadoP3.queueSize() + ArmadoP4.queueSize() + Ajuste.queueSize()
    + ControlFinal.queueSize() + Embalaje.queueSize();"""),
    "tableroFilaPuesto": ("String", [("indice", "int"), ("nombre", "String"), ("puesto", "Service"), ("recurso", "ResourcePool")], """double esperaMedia = tableroIniciadasPuesto[indice] > 0
    ? tableroSumaEsperaPuesto[indice] / tableroIniciadasPuesto[indice] : 0.0;
return String.format(java.util.Locale.US, "%-17s %8d %11s %10.1f %14.2f %10d",
    nombre, puesto.queueSize(), recurso.busy() + "/" + recurso.size(),
    100.0 * recurso.utilization(), esperaMedia, tableroIniciadasPuesto[indice]);"""),
    "tableroResumen": ("String", [], """StringBuilder resumen = new StringBuilder();
resumen.append("=== KRETZ | RESUMEN DEL TABLERO ===\\n");
resumen.append(String.format(java.util.Locale.US,
    "Tiempo simulado: %.2f min\\nIntervalo de ingreso: %.2f min\\n"
    + "Ingresadas: %d\\nTerminadas: %d\\nEn proceso: %d\\nEsperando ahora: %d\\n"
    + "Produccion media desde inicio: %.3f unidades/h\\n",
    time(MINUTE), source.interarrivalTime(MINUTE), tableroIngresadas, tableroTerminadas,
    tableroIngresadas - tableroTerminadas, tableroEsperandoAhora(),
    time(MINUTE) > 0 ? tableroTerminadas * 60.0 / time(MINUTE) : 0.0));
if (tableroTerminadas > 0) {
    resumen.append(String.format(java.util.Locale.US,
        "Tiempo total medio (terminadas): %.3f min\\nTiempo total maximo (terminadas): %.3f min\\n"
        + "Espera total media (terminadas): %.3f min\\n",
        tableroTiempoMedio(), tableroMaxTiempoTotal, tableroEsperaMedia()));
} else {
    resumen.append("Tiempo total y espera: sin unidades terminadas\\n");
}
resumen.append(tableroTerminadas > 1
    ? String.format(java.util.Locale.US, "Ritmo entre salidas: %.3f unidades/h\\n", tableroRitmoSalidas())
    : "Ritmo entre salidas: requiere al menos dos terminadas\\n");
resumen.append(String.format(java.util.Locale.US,
    "Cola inicial: %d | Espera media de las que salieron: %.3f min | Salieron: %d\\n",
    queue.size(), tableroSalidasCola > 0 ? tableroSumaEsperaCola / tableroSalidasCola : 0.0,
    tableroSalidasCola));
resumen.append(String.format("%-17s %8s %11s %10s %14s %10s\\n",
    "Puesto", "En cola", "Ocup./total", "Uso (%)", "Esp. media min", "Iniciadas"));
""" + "\n".join(
        f'resumen.append(tableroFilaPuesto({i}, "{label}", {block}, {pool})).append("\\n");'
        for i, (block, label, pool) in enumerate(STAGES)
    ) + """
resumen.append("Uso: promedio desde inicio. Espera por puesto: unidades que iniciaron tarea.\\n");
resumen.append("Tiempo total y espera total: solo unidades terminadas; las pendientes no estan incluidas.\\n");
resumen.append("=== FIN DEL RESUMEN ===");
return resumen.toString();"""),
}

CALLBACKS = {
    ("source", "onExit"): """Balanza balanzaTablero = (Balanza) agent;
balanzaTablero.tiempoIngresoTablero = time(MINUTE);
balanzaTablero.esperaAcumuladaTablero = 0.0;
tableroIngresadas++;""",
    ("queue", "onEnter"): """((Balanza) agent).inicioEsperaColaTablero = time(MINUTE);""",
    ("queue", "onExit"): """Balanza balanzaTablero = (Balanza) agent;
double esperaColaTablero = Math.max(0.0, time(MINUTE) - balanzaTablero.inicioEsperaColaTablero);
balanzaTablero.esperaAcumuladaTablero += esperaColaTablero;
tableroSumaEsperaCola += esperaColaTablero;
tableroSalidasCola++;""",
    ("sink", "onEnter"): """Balanza balanzaTablero = (Balanza) agent;
double tiempoTotalTablero = Math.max(0.0, time(MINUTE) - balanzaTablero.tiempoIngresoTablero);
tableroTerminadas++;
tableroSumaTiempoTotal += tiempoTotalTablero;
tableroMaxTiempoTotal = Math.max(tableroMaxTiempoTotal, tiempoTotalTablero);
tableroSumaEsperaTotal += balanzaTablero.esperaAcumuladaTablero;
if (tableroPrimeraSalida < 0) tableroPrimeraSalida = time(MINUTE);
tableroUltimaSalida = time(MINUTE);""",
}
for index, (block, _, _) in enumerate(STAGES):
    CALLBACKS[(block, "onEnter")] = "((Balanza) agent).inicioEsperaTablero = time(MINUTE);"
    CALLBACKS[(block, "onEnterDelay")] = f"""Balanza balanzaTablero = (Balanza) agent;
double esperaPuestoTablero = Math.max(0.0, time(MINUTE) - balanzaTablero.inicioEsperaTablero);
balanzaTablero.esperaAcumuladaTablero += esperaPuestoTablero;
tableroSumaEsperaPuesto[{index}] += esperaPuestoTablero;
tableroIniciadasPuesto[{index}]++;"""


class DashboardWriter:
    def __init__(self, source):
        self.doc = minidom.parse(str(source))
        self.next_id = 1790000000100
        self.used_ids = {n.firstChild.data for n in self.doc.getElementsByTagName("Id") if n.firstChild}

    def element(self, parent, tag, text=None, *, cdata=False, attributes=None):
        node = self.doc.createElement(tag)
        for key, value in (attributes or {}).items():
            node.setAttribute(key, str(value))
        if text is not None:
            node.appendChild(self.doc.createCDATASection(str(text)) if cdata else self.doc.createTextNode(str(text)))
        parent.appendChild(node)
        return node

    @staticmethod
    def child(parent, tag):
        return next((n for n in parent.childNodes if n.nodeType == n.ELEMENT_NODE and n.tagName == tag), None)

    def common(self, parent, name, x, y, visible=True):
        while str(self.next_id) in self.used_ids:
            self.next_id += 1
        self.element(parent, "Id", self.next_id)
        self.used_ids.add(str(self.next_id))
        self.next_id += 1
        self.element(parent, "Name", name, cdata=True)
        self.element(parent, "X", x)
        self.element(parent, "Y", y)
        label = self.element(parent, "Label")
        self.element(label, "X", 10)
        self.element(label, "Y", 0)
        self.element(parent, "PublicFlag", "true")
        self.element(parent, "PresentationFlag", str(visible).lower())
        self.element(parent, "ShowLabel", "false")

    def variable(self, container, name, kind, initial):
        variable = self.element(container, "Variable", attributes={"Class": "PlainVariable"})
        self.common(variable, name, 40, -250, visible=False)
        properties = self.element(variable, "Properties", attributes={
            "SaveInSnapshot": "true", "Constant": "false", "AccessType": "public", "StaticVariable": "false",
        })
        self.element(properties, "Type", kind, cdata=True)
        initial_node = self.element(properties, "InitialValue", attributes={"Class": "CodeValue"})
        self.element(initial_node, "Code", initial, cdata=True)

    def function(self, container, name, return_type, parameters, body):
        function = self.element(container, "Function", attributes={"AccessType": "public", "StaticFunction": "false"})
        self.element(function, "ReturnModificator", "RETURNS_VALUE")
        self.element(function, "ReturnType", return_type, cdata=True)
        self.common(function, name, 250, -250, visible=False)
        for parameter_name, parameter_type in parameters:
            parameter = self.element(function, "Parameter")
            self.element(parameter, "Name", parameter_name, cdata=True)
            self.element(parameter, "Type", parameter_type, cdata=True)
        self.element(function, "Body", body, cdata=True)

    def callback(self, block, name, code):
        parameters = self.child(block, "Parameters")
        parameter = next((p for p in parameters.getElementsByTagName("Parameter")
                          if self.child(p, "Name").firstChild.data == name), None)
        if parameter is None:
            parameter = self.element(parameters, "Parameter")
            self.element(parameter, "Name", name, cdata=True)
        existing = self.child(parameter, "Value")
        if existing is not None:
            old_code = self.child(existing, "Code")
            if old_code and old_code.firstChild and old_code.firstChild.data.strip():
                code = old_code.firstChild.data + "\n" + code
            parameter.removeChild(existing)
        value = self.element(parameter, "Value", attributes={"Class": "CodeValue"})
        self.element(value, "Code", code, cdata=True)

    @staticmethod
    def color(hex_color):
        return int(hex_color.removeprefix("#"), 16) - 0x1000000

    def text(self, container, name, x, y, value, expression=None, size=14, color="334155", bold=False, mono=False):
        text = self.element(container, "Text")
        self.common(text, name, x, y)
        self.element(text, "DrawMode", "SHAPE_DRAW_2D")
        self.element(text, "EmbeddedIcon", "false")
        self.element(text, "Z", 0)
        self.element(text, "Rotation", "0.0")
        self.element(text, "Color", self.color(color))
        self.element(text, "Text", value, cdata=True)
        if expression:
            self.element(text, "TextCode", expression, cdata=True)
        font = self.element(text, "Font")
        self.element(font, "Name", "Monospaced" if mono else "SansSerif")
        self.element(font, "Size", size)
        self.element(font, "Style", 1 if bold else 0)
        self.element(text, "Alignment", "LEFT")

    def rectangle(self, container, name, x, y, width, height, fill="FFFFFF", line="E2E8F0"):
        rectangle = self.element(container, "Rectangle")
        self.common(rectangle, name, x, y)
        self.element(rectangle, "DrawMode", "SHAPE_DRAW_2D")
        self.element(rectangle, "EmbeddedIcon", "false")
        self.element(rectangle, "Z", 0)
        self.element(rectangle, "LineColor", self.color(line))
        self.element(rectangle, "FillColor", self.color(fill))
        self.element(rectangle, "LineWidth", 1)
        self.element(rectangle, "Width", width)
        self.element(rectangle, "Height", height)
        self.element(rectangle, "Rotation", "0.0")

    def button(self, container, name, x, y, width, label, action):
        button = self.element(container, "Control", attributes={"Type": "Button"})
        self.element(button, "EmbeddedIcon", "false")
        self.common(button, name, x, y)
        self.element(button, "DrawMode", "SHAPE_DRAW_2D")
        basic = self.element(button, "BasicProperties", attributes={"Width": width, "Height": 36})
        self.element(basic, "EmbeddedIcon", "false")
        self.element(basic, "FillColor", self.color("2563EB"))
        self.element(basic, "TextColor", -1)
        self.element(basic, "Enabled", "true")
        self.element(basic, "ActionCode", action, cdata=True)
        extended = self.element(button, "ExtendedProperties")
        self.element(extended, "Font", attributes={"Name": "SansSerif", "Size": 14, "Style": 0})
        self.element(extended, "LabelText", label, cdata=True)

    def area(self, container, name, title, x, y, width, height):
        area = self.element(container, "Area")
        self.common(area, name, x, y)
        self.element(area, "Title", title, cdata=True)
        self.element(area, "Width", width)
        self.element(area, "Height", height)

    def build(self, output):
        classes = self.doc.getElementsByTagName("ActiveObjectClasses")[0]
        class_nodes = [n for n in classes.childNodes if n.nodeType == n.ELEMENT_NODE and n.tagName == "ActiveObjectClass"]
        main = next(n for n in class_nodes if self.child(n, "Name").firstChild.data == "Main")
        balanza = next(n for n in class_nodes if self.child(n, "Name").firstChild.data == "Balanza")
        model = self.doc.getElementsByTagName("Model")[0]
        self.child(model, "Name").firstChild.data = "TPI-Simulacion-KRETZ-Tablero"
        self.child(model, "Id").firstChild.data = "1790000000000"
        for node in self.doc.getElementsByTagName("JavaPackageName") + self.doc.getElementsByTagName("PackageName"):
            if node.firstChild and node.firstChild.data == "tpi_simulacion_kretz":
                node.firstChild.data = "tpi_simulacion_kretz_tablero"

        variables = self.element(main, "Variables")
        main.insertBefore(variables, self.child(main, "AgentLinks"))
        for variable in MAIN_VARIABLES:
            self.variable(variables, *variable)
        for variable in BALANZA_VARIABLES:
            self.variable(self.child(balanza, "Variables"), *variable)
        functions = self.element(main, "Functions")
        main.insertBefore(functions, self.child(main, "AgentLinks"))
        for name, function in FUNCTIONS.items():
            self.function(functions, name, *function)

        blocks = {self.child(block, "Name").firstChild.data: block
                  for block in self.child(main, "EmbeddedObjects").childNodes if block.nodeType == block.ELEMENT_NODE}
        for (block, callback), code in CALLBACKS.items():
            self.callback(blocks[block], callback, code)
        for _, _, pool in STAGES:
            self.callback(blocks[pool], "forceStatisticsCollection", "true")

        # Compatibilidad con entradas viejas: antes "especialidad" era un String sin
        # comillas (bug). El modelo base actual ya lo tiene bien tipado (enum
        # Especialidad, valor Armador); solo corregimos si detectamos el bug viejo.
        operario = next(n for n in class_nodes if self.child(n, "Name").firstChild.data == "Operario")
        specialty = next(v for v in self.child(operario, "Variables").getElementsByTagName("Variable")
                         if self.child(v, "Name").firstChild.data == "especialidad")
        specialty_code = specialty.getElementsByTagName("DefaultValue")[0].getElementsByTagName("Code")[0]
        if specialty_code.firstChild and specialty_code.firstChild.data == "ARMADOR":
            specialty_code.firstChild.data = "Armador"

        presentation = self.child(main, "Presentation")
        level = self.child(presentation, "Level")
        if level is not None:
            presentation = self.child(level, "Presentation")
            if presentation is None:
                presentation = self.element(level, "Presentation")
        areas = self.element(main, "Areas")
        self.area(areas, "vistaTablero", "Tablero de indicadores", 1820, 0, 1100, 860)
        self.area(areas, "vistaPlanta", "Planta y proceso", 0, 0, 1773, 1050)
        self.button(presentation, "botonAbrirTablero", 25, 25, 185, "Ver tablero", "vistaTablero.navigateTo();")

        x = 1820
        self.rectangle(presentation, "fondoTablero", x, 0, 1100, 860, "F4F7FB", "F4F7FB")
        self.text(presentation, "tituloTablero", x + 28, 28, "KRETZ | Indicadores de producción", size=24, bold=True, color="0F172A")
        self.button(presentation, "botonVerPlanta", x + 690, 24, 150, "Ver planta", "vistaPlanta.navigateTo();")
        self.button(presentation, "botonResumen", x + 860, 24, 212, "Resumen en consola", "traceln(tableroResumen());")
        self.text(presentation, "relojTablero", x + 28, 77, "Tiempo simulado: 0 min | Ingreso cada 10 min",
                  'String.format(java.util.Locale.US, "Tiempo simulado: %.1f min | Ingreso cada %.1f min", time(MINUTE), source.interarrivalTime(MINUTE))')

        def card(name, cx, cy, width, title, initial, expression, note, note_expression=None):
            self.rectangle(presentation, name + "Fondo", cx, cy, width, 108)
            self.text(presentation, name + "Titulo", cx + 16, cy + 16, title, size=12, bold=True, color="64748B")
            self.text(presentation, name + "Valor", cx + 16, cy + 44, initial, expression, size=27, bold=True, color="0F172A")
            self.text(presentation, name + "Nota", cx + 16, cy + 86, note, note_expression, size=12, color="64748B")

        card("terminadas", x + 28, 112, 328, "BALANZAS TERMINADAS", "0", '"" + tableroTerminadas', "Ingresadas: 0", '"Ingresadas: " + tableroIngresadas')
        card("enProceso", x + 376, 112, 328, "BALANZAS EN PROCESO", "0", '"" + (tableroIngresadas - tableroTerminadas)', "Esperando ahora: 0", '"Esperando ahora: " + tableroEsperandoAhora()')
        card("produccionMedia", x + 724, 112, 348, "PRODUCCIÓN MEDIA", "0.00 u/h",
             'String.format(java.util.Locale.US, "%.2f u/h", time(MINUTE) > 0 ? tableroTerminadas * 60.0 / time(MINUTE) : 0.0)', "Desde inicio; incluye arranque")
        card("tiempoMedio", x + 28, 238, 247, "TIEMPO TOTAL MEDIO", "Sin terminadas",
             'tableroTerminadas > 0 ? String.format(java.util.Locale.US, "%.2f min", tableroTiempoMedio()) : "Sin terminadas"', "Solo balanzas terminadas")
        card("tiempoMaximo", x + 294, 238, 247, "TIEMPO TOTAL MÁXIMO", "Sin terminadas",
             'tableroTerminadas > 0 ? String.format(java.util.Locale.US, "%.2f min", tableroMaxTiempoTotal) : "Sin terminadas"', "Solo balanzas terminadas")
        card("esperaMedia", x + 560, 238, 247, "ESPERA TOTAL MEDIA", "Sin terminadas",
             'tableroTerminadas > 0 ? String.format(java.util.Locale.US, "%.2f min", tableroEsperaMedia()) : "Sin terminadas"', "Solo balanzas terminadas")
        card("ritmoSalidas", x + 826, 238, 246, "RITMO ENTRE SALIDAS", "Faltan salidas",
             'tableroTerminadas > 1 ? String.format(java.util.Locale.US, "%.2f u/h", tableroRitmoSalidas()) : "Faltan salidas"', "Desde primera a última salida")

        self.text(presentation, "tituloPuestos", x + 28, 378, "Carga y espera por puesto", size=19, bold=True, color="0F172A")
        self.rectangle(presentation, "encabezadoPuestos", x + 28, 415, 1044, 40, "E2E8F0", "E2E8F0")
        self.text(presentation, "columnasPuestos", x + 40, 428,
                  "Puesto              En cola Ocup./total    Uso (%) Esp. media min  Iniciadas",
                  'String.format("%-17s %8s %11s %10s %14s %10s", "Puesto", "En cola", "Ocup./total", "Uso (%)", "Esp. media min", "Iniciadas")',
                  mono=True, size=14, bold=True)
        for i, (block, label, pool) in enumerate(STAGES):
            cy = 457 + i * 37
            self.rectangle(presentation, "fila" + block + "Fondo", x + 28, cy, 1044, 36, "FFFFFF" if i % 2 == 0 else "F8FAFC", "F4F7FB")
            self.text(presentation, "fila" + block, x + 40, cy + 10, label,
                      f'tableroFilaPuesto({i}, "{label}", {block}, {pool})', mono=True, size=14)
        self.text(presentation, "colaInicialTablero", x + 28, 738,
                  "Cola inicial: 0 | Espera media: 0.00 min | Salieron: 0",
                  'String.format(java.util.Locale.US, "Cola inicial: %d | Espera media: %.2f min | Salieron: %d", queue.size(), tableroSalidasCola > 0 ? tableroSumaEsperaCola / tableroSalidasCola : 0.0, tableroSalidasCola)')
        self.text(presentation, "ayudaUsoTablero", x + 28, 774, "Uso: ocupación promedio desde inicio. Ocup./total: ocupados / dotación total.", size=12, color="64748B")
        self.text(presentation, "ayudaEsperaTablero", x + 28, 796, "Espera por puesto: promedio de balanzas que iniciaron tarea; pendientes en cola todavía no se incluyen.", size=12, color="64748B")
        self.text(presentation, "ayudaResumenTablero", x + 28, 818, "Para compartir resultados: pausá la corrida, pulsá Resumen en consola y copiá el bloque completo.", size=12, color="64748B")

        experiment = self.doc.getElementsByTagName("SimulationExperiment")[0]
        title = experiment.getElementsByTagName("Title")[0]
        title.firstChild.data = "KRETZ | Tablero de indicadores"
        time_properties = self.child(experiment, "ModelTimeProperties")
        self.child(time_properties, "StopOption").firstChild.data = "Stop at specified time"
        self.child(time_properties, "FinalTime").firstChild.data = "240.0"
        after_run = self.child(experiment, "AfterSimulationRunCode")
        if after_run is None:
            self.element(experiment, "AfterSimulationRunCode", "traceln(root.tableroResumen());", cdata=True)
        else:
            previous = "".join(n.data for n in after_run.childNodes if n.nodeType in (n.TEXT_NODE, n.CDATA_SECTION_NODE))
            for node in list(after_run.childNodes):
                after_run.removeChild(node)
            after_run.appendChild(self.doc.createCDATASection(previous + "\ntraceln(root.tableroResumen());"))
        for node in experiment.getElementsByTagName("Text"):
            if node.firstChild and node.firstChild.nodeType == node.CDATA_SECTION_NODE:
                node.firstChild.data = "KRETZ | Tablero de indicadores"
        output.parent.mkdir(parents=True, exist_ok=True)
        def remove_formatting(node):
            for child in list(node.childNodes):
                if child.nodeType == child.TEXT_NODE and not child.data.strip():
                    node.removeChild(child)
                elif child.hasChildNodes():
                    remove_formatting(child)
        remove_formatting(self.doc)
        output.write_bytes(self.doc.toprettyxml(indent="\t", encoding="UTF-8").replace(b"\n", b"\r\n"))
        print(f"Modelo creado: {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("TPI-Simulacion-KRETZ.alp"))
    parser.add_argument("--salida", type=Path, default=Path("TPI-Simulacion-KRETZ-Tablero.alp"))
    args = parser.parse_args()
    if args.entrada.resolve() == args.salida.resolve():
        parser.error("La salida debe ser una copia distinta del modelo de entrada.")
    DashboardWriter(args.entrada).build(args.salida)


if __name__ == "__main__":
    main()
