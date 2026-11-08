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

# Elementos que generaba el script y ya no se usan
VARIABLES_OBSOLETAS = {"rackCalidadX", "rackCalidadY", "contadorRackCalidad", "despachoX", "despachoY"}
FUNCIONES_OBSOLETAS = {"ubicarEnRackCalidad"}
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
        # Racks del depósito: copias de la plantilla Storage con más estantes y cajas por celda
        for nombre, (x, y) in D.ALMACENES.items():
            r = p["storage"].cloneNode(True)
            self.renovar_ids(r)
            self.hijo(r, "Name").firstChild.data = nombre
            self.posicion(r, x, y)
            self.poner(r, "NumberOfShelves", D.ESTANTES_POR_RACK)
            for par in r.getElementsByTagName("Parameter"):
                if self.nombre(par) == "cellCapacity":
                    for h in self.hijos(par, "Value"):
                        par.removeChild(h)
                    val = self.el(par, "Value", attrs={"Class": "CodeValue"})
                    self.el(val, "Code", D.CAJAS_POR_CELDA, cdata=True)
            self.plano.appendChild(r)
        # Rótulos de los racks y del inspector
        xm, ym = D.ALMACENES["almacenMateriales"]
        xc, yc = D.ALMACENES["almacenCalidad"]
        self.posicion(textos["rotuloRack"], xm + 48, ym - 8)
        self.posicion(textos["usoRack"], v["rackX"], v["rackY"] + 14)
        self.posicion(textos["rotuloRackCalidad"], xc + 48, yc + 92)
        self.posicion(textos["rotuloStock"], v["stockFrenteX"], v["stockFrenteY"] + 14)
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
    e.requerir_libreria(D.MHL, (8, 3, 0))
    respaldo = args.modelo.with_suffix(".antes.alp")
    shutil.copy2(args.modelo, respaldo)
    e.guardar(args.modelo)
    print(f"Modelo actualizado: {args.modelo} (copia anterior en {respaldo.name})")


if __name__ == "__main__":
    main()
