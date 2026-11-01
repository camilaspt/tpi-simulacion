"""Código Java del modelo KRETZ (parámetros, variables, funciones y acciones).

Lo usa desarrollar_modelo.py para escribir el .alp y para armar un arnés de
compilación que verifica el código contra las librerías de AnyLogic.
"""

# ---------------------------------------------------------------------------
# Parámetros de Main: (nombre, tipo, valor por defecto, etiqueta)
# ---------------------------------------------------------------------------
PARAMETROS = [
    # Orden de fabricación
    ("ofSeleccionada", "int", "1", "OF (1, 2, 3 = ejemplos; 4 = rotar ejemplos; 0 = personalizada)"),
    ("cantidadAILA", "int", "36", "OF personalizada: AILA 30KG"),
    ("cantidadREPORT", "int", "50", "OF personalizada: REPORT LT"),
    ("cantidadNOVEL", "int", "72", "OF personalizada: NOVEL ECO"),
    ("cantidadLURA", "int", "48", "OF personalizada: LURA"),
    ("cantidadAURA", "int", "60", "OF personalizada: AURA"),
    ("reglaSecuencia", "int", "0", "Secuencia (0 FIFO de la OF, 1 largos primero, 2 cortos primero, 3 intercalado)"),
    # Jornada
    ("diasPorSemana", "int", "5", "Jornadas por semana"),
    ("semanasSimuladas", "int", "4", "Semanas a simular"),
    ("duracionTurnoMin", "double", "480", "Duración del turno (min)"),
    ("maxHorasRecuperacion", "double", "16", "Máximo de horas de recuperación por fin de semana"),
    ("detenerAlFinal", "boolean", "true", "Detener la simulación al terminar"),
    # Estructura y dotación
    ("lineasArmado", "int", "4", "Líneas de Armado"),
    ("lineasCF", "int", "2", "Líneas de Control Final"),
    ("armadoresPorLinea", "int", "4", "Puestos de armado por línea de Armado"),
    ("ajustadoresPorLinea", "int", "1", "Puestos de ajuste por línea de Armado"),
    ("controladoresPorLineaCF", "int", "2", "Puestos de control final por línea de CF"),
    ("embaladoresPorLineaCF", "int", "3", "Puestos de embalaje por línea de CF"),
    ("extraArmadores", "int", "0", "Contratación: Armadores adicionales"),
    ("extraAjustadores", "int", "0", "Contratación: Ajustadores adicionales"),
    ("extraControladores", "int", "0", "Contratación: Controladores adicionales"),
    ("extraEmbaladores", "int", "0", "Contratación: Embaladores adicionales"),
    ("operariosReserva", "int", "0", "Personal de reserva polivalente"),
    ("empleadosDeposito", "int", "20", "Empleados de depósito (solo para costos)"),
    # Ausentismo y coberturas
    ("probAusencia", "double", "0.06", "Probabilidad de ausencia por empleado y día"),
    ("probAusenciaFinDeSemana", "double", "0.10", "Probabilidad de no asistir a la recuperación"),
    ("coberturaEntreEspecialidades", "boolean", "false", "Permitir coberturas entre especialidades"),
    ("maxPuestosPorOperario", "int", "2", "Máximo de puestos que atiende un operario"),
    # Tiempos
    ("variabilidadTiempos", "double", "1", "Variabilidad de tiempos (0 = determinístico)"),
    ("velocidadOperario", "double", "1.3", "Velocidad peatonal (m/s)"),
    ("capacidadRackMateriales", "int", "1", "Operarios que retiran en el rack a la vez"),
    ("tiempoInspeccionMin", "double", "8", "Tiempo medio de inspección (min)"),
    ("probRechazo", "double", "0.03", "Probabilidad de rechazo en inspección"),
    # Costos
    ("valorHoraNormal", "double", "6500", "Costo hora normal por empleado ($/h, con cargas)"),
    ("recargoFinDeSemana", "double", "2", "Recargo de la hora extra de fin de semana"),
    ("costoReorganizacion", "double", "0", "Costo de la reorganización ($)"),
]

# ---------------------------------------------------------------------------
# Variables de Main: (nombre, tipo, valor inicial)
# ---------------------------------------------------------------------------
VARIABLES_MAIN = [
    # Constantes de tipos de puesto
    ("T_ARMADO", "int", "0"),
    ("T_AJUSTE", "int", "1"),
    ("T_CONTROL", "int", "2"),
    ("T_EMBALAJE", "int", "3"),
    # Geometría de la planta (píxeles; la regla de escala da 16 px = 1 m)
    ("pxPorMetro", "double", "16"),
    ("origenPuestosX", "double", "995"),
    ("origenPuestosY", "double", "205"),
    ("separacionPuestosX", "double", "52"),
    ("separacionLineasY", "double", "58"),
    ("rackX", "double", "1460"),
    ("rackY", "double", "245"),
    ("zonaAusentesX", "double", "962"),
    ("zonaAusentesY", "double", "603"),
    ("zonaReservaX", "double", "1142"),
    ("zonaReservaY", "double", "538"),
    # Recetas de proceso (paso 0 = primer puesto; el viaje a Depósito va aparte)
    ("nombresModelo", "String[]", '{ "AILA 30KG", "REPORT LT", "NOVEL ECO", "LURA", "AURA" }'),
    ("abreviaturas", "String[]", '{ "AILA", "REP", "NOV", "LUR", "AUR" }'),
    ("recLen", "int[]", "new int[5]"),
    ("recTipo", "int[][]", "new int[5][12]"),
    ("recNum", "int[][]", "new int[5][12]"),
    ("recTiempo", "double[][]", "new double[5][12]"),
    ("tiempoRetiro", "double[]", "new double[5]"),
    ("fuenteTiempos", "String", '""'),
    # Puestos de trabajo
    ("plantaConstruida", "boolean", "false"),
    ("nPuestos", "int", "0"),
    ("nArmadoFijos", "int", "4"),
    ("columnasLinea", "int[]", "new int[12]"),
    ("pLinea", "int[]", "new int[60]"),
    ("pTipo", "int[]", "new int[60]"),
    ("pNum", "int[]", "new int[60]"),
    ("pX", "double[]", "new double[60]"),
    ("pY", "double[]", "new double[60]"),
    ("pTitular", "int[]", "new int[60]"),
    ("pAtiende", "int[]", "new int[60]"),
    ("lineaCapaz", "boolean[][][]", "new boolean[12][5][2]"),
    ("ops", "java.util.ArrayList<Operario>", "new java.util.ArrayList<Operario>()"),
    # Estado de la jornada
    ("colaLiberacion", "java.util.LinkedList<Integer>", "new java.util.LinkedList<Integer>()"),
    ("contadorLiberadas", "int", "0"),
    ("dia", "int", "0"),
    ("diaGlobal", "int", "0"),
    ("semana", "int", "0"),
    ("enRecuperacion", "boolean", "false"),
    ("simulacionTerminada", "boolean", "false"),
    ("tInicioJornada", "double", "0"),
    ("tInicioRecuperacion", "double", "0"),
    ("factorAusenciaDia", "double[]", "{ 1.25, 1.0, 0.9, 0.9, 1.1 }"),
    ("ofDia", "int[]", "new int[5]"),
    ("aTiempoDia", "int[]", "new int[5]"),
    ("prodDia", "int[]", "new int[5]"),
    ("ofSemana", "int[]", "new int[5]"),
    ("prodSemana", "int[]", "new int[5]"),
    ("prodTotal", "int[]", "new int[5]"),
    ("faltanteModelo", "int[]", "new int[5]"),
    ("liberadasSemana", "int", "0"),
    ("terminadasSemana", "int", "0"),
    ("enProceso", "int", "0"),
    # Personal
    ("ausentesHoy", "int", "0"),
    ("vacantesHoy", "int", "0"),
    ("coberturasHoy", "int", "0"),
    ("vacantesCriticasHoy", "int", "0"),
    ("coberturasTotal", "int", "0"),
    ("vacantesCriticasTotal", "int", "0"),
    ("minutosVacantesTotal", "double", "0"),
    ("caminataTotalMin", "double", "0"),
    ("personasRecuperacion", "int", "0"),
    ("pendientesInicioRecuperacion", "int", "0"),
    # Indicadores de cierre
    ("diasSimulados", "int", "0"),
    ("diasSinCumplir", "int", "0"),
    ("diasConAusencias", "int", "0"),
    ("diasSinAusencias", "int", "0"),
    ("faltanteConAusencias", "double", "0"),
    ("faltanteSinAusencias", "double", "0"),
    ("horasExtraTotal", "double", "0"),
    ("costoHorasExtraTotal", "double", "0"),
    ("historial", "java.util.ArrayList<String>", "new java.util.ArrayList<String>()"),
    # Calidad y stock
    ("inspeccionadas", "int[]", "new int[5]"),
    ("rechazadas", "int[]", "new int[5]"),
    ("enStock", "int[]", "new int[5]"),
    ("sumaTiempoSistema", "double[]", "new double[5]"),
    ("sumaEspera", "double[]", "new double[5]"),
]

VARIABLES_BALANZA = [
    ("tipoModelo", "int", "0"),
    ("paso", "int", "0"),
    ("lineaArmado", "int", "-1"),
    ("lineaCF", "int", "-1"),
    ("puestoActual", "int", "-1"),
    ("opActual", "Operario", "null"),
    ("fase", "int", "0"),
    ("destX", "double", "0"),
    ("destY", "double", "0"),
    ("tInicioCaminata", "double", "0"),
    ("tIngreso", "double", "0"),
    ("tInicioEspera", "double", "0"),
    ("esperaTotal", "double", "0"),
    ("tCaminata", "double", "0"),
    ("diaOF", "int", "0"),
    ("ordenLiberacion", "int", "0"),
    ("inspeccionar", "boolean", "false"),
    ("posMuestra", "int", "0"),
    ("rechazada", "boolean", "false"),
    ("tIngresoRack", "double", "0"),
]

VARIABLES_OPERARIO = [
    ("idOp", "int", "0"),
    ("lineaHabitual", "int", "-1"),
    ("puestoHabitual", "int", "-1"),
    ("presente", "boolean", "true"),
    ("esReserva", "boolean", "false"),
    ("puestosAtendidos", "java.util.ArrayList<Integer>", "new java.util.ArrayList<Integer>()"),
    ("estado", "int", "0"),
    ("puestoTrabajo", "int", "-1"),
    ("tInicioOcupado", "double", "0"),
    ("tOcupado", "double", "0"),
    ("tCaminando", "double", "0"),
    ("minPresente", "double", "0"),
    # Peatón: destino actual, unidad que espera su llegada y si ya entró a la planta
    ("destX", "double", "0"),
    ("destY", "double", "0"),
    ("balanzaEnCamino", "Balanza", "null"),
    ("ingresoPedido", "boolean", "false"),
    ("enPlanta", "boolean", "false"),
]

FUNCIONES_OPERARIO = {
    "colorEstado": ("Color", [], """// Relleno según el estado del operario
if (!presente) return new Color(205, 60, 60);
if (estado == 2) return new Color(30, 150, 75);
if (estado == 1) return new Color(240, 180, 30);
return new Color(160, 168, 180);"""),
    "colorEspecialidad": ("Color", [], """// Borde según la especialidad
if (especialidad == Especialidad.Armador) return new Color(37, 99, 235);
if (especialidad == Especialidad.Ajustador) return new Color(147, 51, 234);
if (especialidad == Especialidad.Controlador) return new Color(13, 148, 136);
if (especialidad == Especialidad.Embalador) return new Color(180, 83, 9);
return new Color(15, 23, 42);"""),
}

# ---------------------------------------------------------------------------
# Funciones de Main: nombre -> (tipo de retorno, [(parámetro, tipo)], cuerpo)
# ---------------------------------------------------------------------------
FUNCIONES_MAIN = {}


def funcion(nombre, retorno, parametros, cuerpo):
    FUNCIONES_MAIN[nombre] = (retorno, parametros, cuerpo.strip("\n"))


# --- Construcción de la planta y datos de entrada ---------------------------
funcion("cantidadOperarios", "int", [], """
construirPlanta();
return nPuestos + operariosReserva;
""")

funcion("construirPlanta", "void", [], """
if (plantaConstruida) return;
cargarRecetas();
nPuestos = 0;
for (int l = 0; l < columnasLinea.length; l++) columnasLinea[l] = 0;
nArmadoFijos = Math.max(1, Math.min(4, armadoresPorLinea));
// Líneas de Armado: puestos de armado (Celda 1) + ajuste (Celda 2/3)
for (int l = 0; l < lineasArmado; l++) {
	for (int k = 1; k <= armadoresPorLinea; k++)
		agregarPuesto(l, T_ARMADO, k <= nArmadoFijos ? k : 0);
	for (int k = 0; k < ajustadoresPorLinea; k++)
		agregarPuesto(l, T_AJUSTE, 0);
}
// Líneas de Control Final: control final + embalaje
for (int l = 0; l < lineasCF; l++) {
	int linea = lineasArmado + l;
	for (int k = 0; k < controladoresPorLineaCF; k++) agregarPuesto(linea, T_CONTROL, 0);
	for (int k = 0; k < embaladoresPorLineaCF; k++) agregarPuesto(linea, T_EMBALAJE, 0);
}
// Contrataciones: cada empleado nuevo agrega un puesto de su especialidad,
// repartido en forma rotativa entre las líneas que hacen esa tarea
for (int k = 0; k < extraArmadores; k++) agregarPuesto(k % lineasArmado, T_ARMADO, 0);
for (int k = 0; k < extraAjustadores; k++) agregarPuesto(k % lineasArmado, T_AJUSTE, 0);
for (int k = 0; k < extraControladores; k++) agregarPuesto(lineasArmado + k % lineasCF, T_CONTROL, 0);
for (int k = 0; k < extraEmbaladores; k++) agregarPuesto(lineasArmado + k % lineasCF, T_EMBALAJE, 0);
plantaConstruida = true;
""")

funcion("agregarPuesto", "void", [("linea", "int"), ("tipo", "int"), ("num", "int")], """
if (nPuestos >= pLinea.length || linea >= columnasLinea.length) {
	traceln("Se alcanzó el máximo de puestos del modelo; se ignora un puesto adicional.");
	return;
}
int c = columnasLinea[linea]++;
int p = nPuestos++;
pLinea[p] = linea;
pTipo[p] = tipo;
pNum[p] = num;
// Hasta 5 puestos en la fila de la línea; los adicionales van en una segunda fila
if (c < 5) {
	pX[p] = origenPuestosX + c * separacionPuestosX;
	pY[p] = origenPuestosY + linea * separacionLineasY;
} else {
	pX[p] = origenPuestosX + (c - 5) * separacionPuestosX + separacionPuestosX / 2;
	pY[p] = origenPuestosY + linea * separacionLineasY + 24;
}
pTitular[p] = -1;
pAtiende[p] = -1;
""")

funcion("pasoReceta", "void", [("m", "int"), ("tipo", "int"), ("num", "int"), ("tiempo", "double")], """
int k = recLen[m]++;
recTipo[m][k] = tipo;
recNum[m][k] = num;
recTiempo[m][k] = tiempo;
""")

funcion("cargarRecetas", "void", [], """
// Valores relevados de SAP (los mismos de Datos/tiempos_proceso.csv), por si no se encuentra el archivo
for (int m = 0; m < 5; m++) {
	recLen[m] = 0;
	tiempoRetiro[m] = 2;
}
pasoReceta(0, T_ARMADO, 1, 3.5); pasoReceta(0, T_ARMADO, 2, 7); pasoReceta(0, T_ARMADO, 3, 7); pasoReceta(0, T_ARMADO, 4, 7.5);
pasoReceta(0, T_AJUSTE, 0, 5); pasoReceta(0, T_CONTROL, 0, 4.5); pasoReceta(0, T_EMBALAJE, 0, 10);
pasoReceta(1, T_ARMADO, 0, 11); pasoReceta(1, T_AJUSTE, 0, 12); pasoReceta(1, T_CONTROL, 0, 12); pasoReceta(1, T_EMBALAJE, 0, 12);
pasoReceta(2, T_ARMADO, 0, 3.15); pasoReceta(2, T_AJUSTE, 0, 3); pasoReceta(2, T_CONTROL, 0, 2.25); pasoReceta(2, T_EMBALAJE, 0, 3);
pasoReceta(3, T_AJUSTE, 0, 4); pasoReceta(3, T_CONTROL, 0, 3.15); pasoReceta(3, T_EMBALAJE, 0, 3.15);
pasoReceta(4, T_ARMADO, 0, 3.15); pasoReceta(4, T_AJUSTE, 0, 3); pasoReceta(4, T_CONTROL, 0, 2.5); pasoReceta(4, T_EMBALAJE, 0, 2.88);
fuenteTiempos = "valores SAP cargados en el modelo";

java.io.File archivo = new java.io.File("Datos/tiempos_proceso.csv");
if (!archivo.exists()) {
	traceln("No se encontró Datos/tiempos_proceso.csv; se usan los tiempos cargados en el modelo.");
	return;
}
int[] largo = new int[5];
int[][] tipos = new int[5][12];
int[][] nums = new int[5][12];
double[][] tiempos = new double[5][12];
double[] retiro = { 2, 2, 2, 2, 2 };
try (java.io.BufferedReader lector = new java.io.BufferedReader(new java.io.InputStreamReader(
		new java.io.FileInputStream(archivo), java.nio.charset.StandardCharsets.UTF_8))) {
	String fila = lector.readLine(); // encabezado
	while ((fila = lector.readLine()) != null) {
		String[] c = fila.split(";");
		if (c.length < 7) continue;
		int m = indiceModelo(c[0]);
		if (m < 0) continue;
		double t = Double.parseDouble(c[6].trim().replace(',', '.'));
		String celda = c[3].trim().toUpperCase();
		String puesto = c[4].trim().toUpperCase();
		String tarea = c[5].trim().toUpperCase();
		if (c[2].trim().toUpperCase().startsWith("DEPOSITO")) {
			retiro[m] = t; // solo el retiro en el rack; las caminatas salen del modelo
			continue;
		}
		int tipo;
		if (celda.startsWith("EMBALAJE")) tipo = T_EMBALAJE;
		else if (celda.startsWith("CONTROL")) tipo = T_CONTROL;
		else if (tarea.startsWith("AJUSTADOR")) tipo = T_AJUSTE; // Celda 2 y Celda 3 (REPORT LT)
		else tipo = T_ARMADO;
		int num = 0;
		int i = puesto.indexOf("PUESTO ");
		if (tipo == T_ARMADO && i >= 0) num = Integer.parseInt(puesto.substring(i + 7).trim());
		if (largo[m] >= 12) continue;
		tipos[m][largo[m]] = tipo;
		nums[m][largo[m]] = num;
		tiempos[m][largo[m]] = t;
		largo[m]++;
	}
} catch (Exception e) {
	traceln("No se pudo leer Datos/tiempos_proceso.csv (" + e.getMessage() + "); se usan los tiempos cargados en el modelo.");
	return;
}
for (int m = 0; m < 5; m++) if (largo[m] == 0) return;
for (int m = 0; m < 5; m++) {
	recLen[m] = largo[m];
	tiempoRetiro[m] = retiro[m];
	for (int k = 0; k < largo[m]; k++) {
		recTipo[m][k] = tipos[m][k];
		recNum[m][k] = nums[m][k];
		recTiempo[m][k] = tiempos[m][k];
	}
}
fuenteTiempos = "Datos/tiempos_proceso.csv";
""")

funcion("indiceModelo", "int", [("nombre", "String")], """
String u = nombre.toUpperCase();
if (u.contains("AILA")) return 0;
if (u.contains("REPORT")) return 1;
if (u.contains("NOVEL")) return 2;
if (u.contains("LURA")) return 3;
if (u.contains("AURA")) return 4;
return -1;
""")

funcion("especialidadDeTipo", "Especialidad", [("tipo", "int")], """
if (tipo == T_ARMADO) return Especialidad.Armador;
if (tipo == T_AJUSTE) return Especialidad.Ajustador;
if (tipo == T_CONTROL) return Especialidad.Controlador;
return Especialidad.Embalador;
""")

funcion("registrarOperario", "void", [("o", "Operario")], """
construirPlanta();
o.idOp = ops.size();
ops.add(o);
if (o.idOp < nPuestos) {
	// Titular de un puesto: su especialidad sale del tipo de puesto
	int p = o.idOp;
	o.puestoHabitual = p;
	o.lineaHabitual = pLinea[p];
	o.esReserva = false;
	o.especialidad = especialidadDeTipo(pTipo[p]);
	pTitular[p] = o.idOp;
} else {
	o.puestoHabitual = -1;
	o.lineaHabitual = -1;
	o.esReserva = true;
	o.especialidad = Especialidad.Polivalente;
}
""")

funcion("ofEjemplo", "int", [("of", "int"), ("m", "int")], """
// OF de ejemplo (reemplazar por OF reales de KRETZ cuando estén disponibles)
int[][] ejemplos = {
	{ 36, 50, 72, 48, 60 },   // OF 1: mezcla equilibrada
	{ 24, 72, 48, 36, 48 },   // OF 2: mucha REPORT LT (procesos largos)
	{ 48, 30, 96, 60, 72 }    // OF 3: alto volumen de equipos cortos
};
if (of == 0) {
	int[] propia = { cantidadAILA, cantidadREPORT, cantidadNOVEL, cantidadLURA, cantidadAURA };
	return propia[m];
}
if (of == 4) return ejemplos[(diaGlobal - 1) % 3][m];
return ejemplos[Math.max(1, Math.min(3, of)) - 1][m];
""")

funcion("tiempoTotalModelo", "double", [("m", "int")], """
double total = tiempoRetiro[m];
for (int k = 0; k < recLen[m]; k++) total += recTiempo[m][k];
return total;
""")

funcion("nombreDia", "String", [("d", "int")], """
String[] dias = { "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo" };
return dias[d % 7];
""")

funcion("sumar", "int", [("valores", "int[]")], """
int total = 0;
for (int v : valores) total += v;
return total;
""")

# --- Jornada: asistencia, coberturas y liberación de la OF ------------------
funcion("iniciarJornada", "void", [], """
// Los operarios los crea el ResourcePool y después entran como peatones a la planta;
// hasta que estén todos adentro se reintenta enseguida
if (ops.size() < nPuestos + operariosReserva || !operariosEnPlanta()) {
	eventoInicioJornada.restart(0.01);
	return;
}
enRecuperacion = false;
diaGlobal++;
tInicioJornada = time();
for (int m = 0; m < 5; m++) {
	ofDia[m] = ofEjemplo(ofSeleccionada, m);
	ofSemana[m] += ofDia[m];
	prodDia[m] = 0;
	aTiempoDia[m] = 0;
}
asignarAsistencia(Math.min(1, probAusencia * factorAusenciaDia[dia % 5]));
asignarCoberturas();
ubicarOperarios();
liberarUnidadesOF();
eventoCierreJornada.restart(duracionTurnoMin);
""")

funcion("asignarAsistencia", "void", [("prob", "double")], """
ausentesHoy = 0;
for (Operario o : ops) {
	o.presente = !randomTrue(prob);
	if (!o.presente) ausentesHoy++;
}
""")

funcion("asignarCoberturas", "void", [], """
for (int p = 0; p < nPuestos; p++) pAtiende[p] = -1;
for (Operario o : ops) {
	o.puestosAtendidos.clear();
	if (o.presente && o.puestoHabitual >= 0) {
		pAtiende[o.puestoHabitual] = o.idOp;
		o.puestosAtendidos.add(o.puestoHabitual);
	}
}
vacantesHoy = 0;
coberturasHoy = 0;
vacantesCriticasHoy = 0;
for (int p = 0; p < nPuestos; p++) if (pAtiende[p] < 0) vacantesHoy++;
// Se cubren los puestos vacantes que frenan la línea (ningún otro puesto
// atendido de esa línea puede hacer la tarea). Quien cubre conserva su puesto
// y reparte su tiempo entre los dos: traslada el cuello de botella.
for (int p = 0; p < nPuestos; p++) {
	if (pAtiende[p] >= 0 || !esPuestoCritico(p)) continue;
	Operario c = buscarCobertura(p);
	if (c != null) {
		pAtiende[p] = c.idOp;
		c.puestosAtendidos.add(p);
		coberturasHoy++;
	} else {
		vacantesCriticasHoy++;
	}
}
coberturasTotal += coberturasHoy;
vacantesCriticasTotal += vacantesCriticasHoy;
if (!enRecuperacion) minutosVacantesTotal += (vacantesHoy - coberturasHoy) * duracionTurnoMin;
// Qué líneas pueden completar cada modelo con el personal de hoy
for (int l = 0; l < lineasArmado + lineasCF && l < lineaCapaz.length; l++)
	for (int m = 0; m < 5; m++) {
		lineaCapaz[l][m][0] = l < lineasArmado && lineaPuedeProcesar(l, m, true);
		lineaCapaz[l][m][1] = l >= lineasArmado && lineaPuedeProcesar(l, m, false);
	}
tomarOperario.recalculateResourceChoiceConditions();
""")

funcion("esPuestoCritico", "boolean", [("p", "int")], """
// Un puesto es crítico si ningún otro puesto atendido de su línea puede hacer su tarea
for (int q = 0; q < nPuestos; q++) {
	if (q == p || pAtiende[q] < 0 || pLinea[q] != pLinea[p] || pTipo[q] != pTipo[p]) continue;
	if (pTipo[p] != T_ARMADO || pNum[p] == 0 || pNum[q] == 0 || pNum[q] == pNum[p]) return false;
}
return true;
""")

funcion("puedeCubrir", "boolean", [("o", "Operario")], """
return o.presente && !o.esReserva && !o.puestosAtendidos.isEmpty()
	&& o.puestosAtendidos.size() < maxPuestosPorOperario;
""")

funcion("cargaCobertura", "int", [("o", "Operario")], """
// Menor es mejor: primero quien atiende menos puestos y cuyo puesto propio tiene respaldo
int carga = o.puestosAtendidos.size() * 2;
if (o.puestoHabitual >= 0 && esPuestoCritico(o.puestoHabitual)) carga++;
return carga;
""")

funcion("mejorCandidato", "Operario", [("actual", "Operario"), ("candidato", "Operario")], """
if (actual == null) return candidato;
return cargaCobertura(candidato) < cargaCobertura(actual) ? candidato : actual;
""")

funcion("buscarCobertura", "Operario", [("p", "int")], """
Especialidad e = especialidadDeTipo(pTipo[p]);
int linea = pLinea[p];
boolean lineaDeArmado = linea < lineasArmado;
// 0) Personal de reserva polivalente libre (no deja ningún puesto)
for (Operario o : ops)
	if (o.esReserva && o.presente && o.puestosAtendidos.isEmpty()) return o;
Operario mejor = null;
// 1) Misma especialidad y misma línea
for (Operario o : ops)
	if (puedeCubrir(o) && o.especialidad == e && o.lineaHabitual == linea) mejor = mejorCandidato(mejor, o);
if (mejor != null) return mejor;
// 2) Misma especialidad, otra línea del mismo tipo
for (Operario o : ops)
	if (puedeCubrir(o) && o.especialidad == e && (o.lineaHabitual < lineasArmado) == lineaDeArmado) mejor = mejorCandidato(mejor, o);
if (mejor != null) return mejor;
// 3) Los puestos de armado los puede cubrir cualquier operario (primero de la misma línea)
if (pTipo[p] == T_ARMADO || coberturaEntreEspecialidades) {
	for (Operario o : ops)
		if (puedeCubrir(o) && o.lineaHabitual == linea) mejor = mejorCandidato(mejor, o);
	if (mejor != null) return mejor;
	for (Operario o : ops)
		if (puedeCubrir(o)) mejor = mejorCandidato(mejor, o);
}
return mejor;
""")

funcion("asegurarEspacio", "void", [("o", "Operario")], """
// El ResourcePool crea a los operarios sin espacio asignado; antes de entrar
// como peatones se los incorpora al espacio y nivel de Main
if (o.getSpace() == null) o.setSpace(this);
if (o.getLevel() == null) o.setLevel(level);
""")

funcion("operariosEnPlanta", "boolean", [], """
// Cada operario entra una sola vez al espacio peatonal, directamente en su lugar habitual
boolean listos = true;
for (Operario o : ops) {
	if (o.enPlanta) continue;
	listos = false;
	if (o.ingresoPedido) continue;
	o.ingresoPedido = true;
	asegurarEspacio(o);
	if (o.puestoHabitual >= 0) {
		o.destX = pX[o.puestoHabitual];
		o.destY = pY[o.puestoHabitual];
	} else {
		o.destX = lugarReservaX(o);
		o.destY = lugarReservaY(o);
	}
	entrarPlanta.take(o);
}
return listos;
""")

# Lugares fijos por operario: dos peatones nunca tienen el mismo destino
funcion("lugarAusenteX", "double", [("o", "Operario")], """
return zonaAusentesX + (o.idOp % 11) * 14;
""")

funcion("lugarAusenteY", "double", [("o", "Operario")], """
return zonaAusentesY + (o.idOp / 11 % 4) * 10;
""")

funcion("lugarReservaX", "double", [("o", "Operario")], """
return zonaReservaX + (Math.max(0, o.idOp - nPuestos) % 5) * 14;
""")

funcion("lugarReservaY", "double", [("o", "Operario")], """
return zonaReservaY + (Math.max(0, o.idOp - nPuestos) / 5 % 2) * 10;
""")

funcion("lugarRackX", "double", [("o", "Operario")], """
return rackX - 35 + (o.idOp % 8) * 10;
""")

funcion("lugarRackY", "double", [("o", "Operario")], """
return rackY + (o.idOp / 8 % 5) * 10;
""")

funcion("irALugarDelDia", "void", [("o", "Operario")], """
// Ausentes a su zona, reservas libres a la suya y el resto a un puesto que atiende hoy
if (!o.presente) {
	enviarPeaton(o, lugarAusenteX(o), lugarAusenteY(o));
	return;
}
if (o.puestosAtendidos.isEmpty()) {
	enviarPeaton(o, lugarReservaX(o), lugarReservaY(o));
	return;
}
for (int p : o.puestosAtendidos)
	if (Math.hypot(o.destX - pX[p], o.destY - pY[p]) < 1) return; // ya está en uno de sus puestos
int p = o.puestosAtendidos.get(0);
enviarPeaton(o, pX[p], pY[p]);
""")

funcion("ubicarOperarios", "void", [], """
for (Operario o : ops)
	if (o.estado == 0) irALugarDelDia(o); // quien está trabajando termina su tarea donde está
""")

# --- Movimiento peatonal (Pedestrian Library) --------------------------------
funcion("enviarPeaton", "void", [("o", "Operario"), ("x", "double"), ("y", "double")], """
// Cambia el destino del operario; el circuito peatonal (pedIr -> pedLlego -> pedEnPuesto) lo lleva
boolean cambia = Math.hypot(x - o.destX, y - o.destY) > 1;
o.destX = x;
o.destY = y;
if (!o.enPlanta) return; // pedEntrada lo ubica directamente en su destino
if (pedEnPuesto.contains(o)) {
	// Si lo espera una unidad hay que pasar por pedLlego para avisarle, aunque ya esté en el lugar
	if (cambia || o.balanzaEnCamino != null) pedEnPuesto.free(o);
} else if (cambia && pedIr.contains(o)) {
	pedIr.cancel(o); // sale por ccl y vuelve a pedIr con el destino nuevo
}
""")

funcion("llegoADestino", "boolean", [("o", "Operario")], """
return Math.hypot(o.getX() - o.destX, o.getY() - o.destY) < 0.5 * pxPorMetro;
""")

funcion("alLlegarPeaton", "void", [("o", "Operario")], """
// El operario llegó a su destino: si una unidad lo esperaba, la unidad sigue su proceso
Balanza b = o.balanzaEnCamino;
if (b == null) return;
o.balanzaEnCamino = null;
if (!caminar.free(b)) traceln("Aviso: la unidad " + b.ordenLiberacion + " no estaba esperando a su operario.");
""")

funcion("liberarUnidadesOF", "void", [], """
java.util.ArrayList<Integer> orden = new java.util.ArrayList<Integer>();
Integer[] modelos = { 0, 1, 2, 3, 4 };
if (reglaSecuencia == 1)
	java.util.Arrays.sort(modelos, (a, b) -> Double.compare(tiempoTotalModelo(b), tiempoTotalModelo(a)));
else if (reglaSecuencia == 2)
	java.util.Arrays.sort(modelos, (a, b) -> Double.compare(tiempoTotalModelo(a), tiempoTotalModelo(b)));
if (reglaSecuencia == 3) {
	// Intercalado: un equipo de cada modelo por vuelta
	int[] resto = ofDia.clone();
	boolean quedan = true;
	while (quedan) {
		quedan = false;
		for (int m = 0; m < 5; m++)
			if (resto[m] > 0) {
				orden.add(m);
				resto[m]--;
				quedan = true;
			}
	}
} else {
	for (int m : modelos)
		for (int k = 0; k < ofDia[m]; k++) orden.add(m);
}
colaLiberacion.addAll(orden);
liberadasSemana += orden.size();
fuenteOF.inject(orden.size());
""")

funcion("prepararUnidad", "void", [("b", "Balanza")], """
int m = colaLiberacion.isEmpty() ? 0 : colaLiberacion.removeFirst();
b.tipoModelo = m;
b.set_modelo(nombresModelo[m]);
b.paso = 0;
b.lineaArmado = -1;
b.lineaCF = -1;
b.tIngreso = time();
b.diaOF = diaGlobal;
b.ordenLiberacion = contadorLiberadas++;
enProceso++;
""")

# --- Ruteo y asignación de operarios ----------------------------------------
funcion("prioridad", "double", [("b", "Balanza")], """
// Las unidades más avanzadas pasan primero; entre iguales se respeta el orden de liberación
return b.paso * 100000.0 - b.ordenLiberacion;
""")

funcion("puestoSirvePaso", "boolean", [("p", "int"), ("tipo", "int"), ("num", "int")], """
if (pTipo[p] != tipo) return false;
// AILA 30KG tiene cuatro puestos de armado específicos; los puestos adicionales (num 0) son flexibles
if (tipo != T_ARMADO || num == 0 || pNum[p] == 0) return true;
return pNum[p] == ((num - 1) % nArmadoFijos) + 1;
""")

funcion("lineaPuedeProcesar", "boolean", [("linea", "int"), ("m", "int"), ("faseArmado", "boolean")], """
for (int k = 0; k < recLen[m]; k++) {
	int t = recTipo[m][k];
	if ((t <= T_AJUSTE) != faseArmado) continue;
	boolean hay = false;
	for (int p = 0; p < nPuestos && !hay; p++)
		if (pLinea[p] == linea && pAtiende[p] >= 0 && puestoSirvePaso(p, t, recNum[m][k])) hay = true;
	if (!hay) return false;
}
return true;
""")

funcion("puestoParaPaso", "int", [("b", "Balanza"), ("o", "Operario")], """
int m = b.tipoModelo;
if (!o.presente || b.paso >= recLen[m]) return -1;
int t = recTipo[m][b.paso];
int n = recNum[m][b.paso];
int fase = t <= T_AJUSTE ? 0 : 1;
int fija = fase == 0 ? b.lineaArmado : b.lineaCF;
// Si la línea asignada quedó sin personal para terminar el equipo, se la puede reasignar
if (fija >= 0 && !lineaCapaz[fija][m][fase]) fija = -1;
for (int p : o.puestosAtendidos) {
	if (!puestoSirvePaso(p, t, n)) continue;
	if (fija >= 0 ? pLinea[p] != fija : !lineaCapaz[pLinea[p]][m][fase]) continue;
	return p;
}
return -1;
""")

funcion("alTomarOperario", "void", [("b", "Balanza"), ("o", "Operario")], """
int p = puestoParaPaso(b, o);
b.opActual = o;
b.puestoActual = p;
if (p >= 0) {
	if (pTipo[p] <= T_AJUSTE) b.lineaArmado = pLinea[p];
	else b.lineaCF = pLinea[p];
}
o.estado = 1;
o.puestoTrabajo = p;
o.tInicioOcupado = time();
""")

funcion("planificarDespuesDeTomar", "void", [("b", "Balanza")], """
b.esperaTotal += time() - b.tInicioEspera;
if (b.paso == 0) {
	// Primer paso: el mismo operario va al rack único de materiales y después a su puesto
	b.fase = 1;
	b.destX = lugarRackX(b.opActual);
	b.destY = lugarRackY(b.opActual);
} else {
	b.fase = 2;
	b.destX = pX[b.puestoActual];
	b.destY = pY[b.puestoActual];
}
""")

funcion("iniciarCaminata", "void", [("b", "Balanza")], """
// La unidad queda en el Wait caminar hasta que su operario llega caminando (alLlegarPeaton);
// el tiempo de traslado sale de la simulación peatonal
Operario o = b.opActual;
b.tInicioCaminata = time();
o.estado = 1;
o.balanzaEnCamino = b;
enviarPeaton(o, b.destX, b.destY);
""")

funcion("finCaminata", "void", [("b", "Balanza")], """
double minutos = time() - b.tInicioCaminata;
b.tCaminata += minutos;
b.opActual.tCaminando += minutos;
caminataTotalMin += minutos;
""")

funcion("tiempoAleatorio", "double", [("media", "double")], """
// Triangular asimétrica con la media de SAP: mín 0,8·m, moda 0,9·m, máx 1,3·m (para variabilidad 1)
double k = Math.max(0, Math.min(3, variabilidadTiempos));
if (k == 0 || media <= 0) return media;
return triangular(media * (1 - 0.2 * k), media * (1 + 0.3 * k), media * (1 - 0.1 * k));
""")

funcion("tiempoTarea", "double", [("b", "Balanza")], """
return tiempoAleatorio(recTiempo[b.tipoModelo][b.paso]);
""")

funcion("alLiberarOperario", "void", [("b", "Balanza")], """
// Se ejecuta al entrar al Release, antes de que el operario quede libre
Operario o = b.opActual;
o.tOcupado += time() - o.tInicioOcupado;
o.estado = 0;
o.puestoTrabajo = -1;
irALugarDelDia(o); // por ejemplo, quien cubrió un puesto ayer vuelve al suyo
b.opActual = null;
""")

funcion("registrarTerminada", "boolean", [("b", "Balanza")], """
// Se llama desde la condicion de esPrimero, que AnyLogic puede evaluar dos veces:
// la unidad se registra una sola vez y despues se devuelve el mismo resultado
if (b.tIngresoRack > 0) return b.inspeccionar;
int m = b.tipoModelo;
enProceso--;
terminadasSemana++;
prodDia[m]++;
prodSemana[m]++;
prodTotal[m]++;
if (!enRecuperacion && b.diaOF == diaGlobal) aTiempoDia[m]++;
// Muestra de calidad: el primer equipo de cada modelo de la jornada se inspecciona enseguida
b.inspeccionar = prodDia[m] == 1;
b.posMuestra = b.inspeccionar ? 1 : 0;
b.tIngresoRack = time();
if (enRecuperacion && terminadasSemana >= liberadasSemana) eventoFinRecuperacion.restart(0);
return b.inspeccionar;
""")

# --- Cierre de jornada, recuperación y costos -------------------------------
funcion("registrarPresencia", "void", [("minutos", "double")], """
for (Operario o : ops) if (o.presente) o.minPresente += minutos;
""")

funcion("cerrarMuestras", "void", [], """
// Por cada modelo, el último equipo de la muestra de la jornada se inspecciona; el resto pasa a stock
Balanza[] ultimo = new Balanza[5];
for (int i = 0; i < rackCalidad.size(); i++) {
	Balanza b = rackCalidad.get(i);
	if (ultimo[b.tipoModelo] == null || b.tIngresoRack >= ultimo[b.tipoModelo].tIngresoRack) ultimo[b.tipoModelo] = b;
}
for (Balanza b : ultimo)
	if (b != null) {
		b.inspeccionar = true;
		b.posMuestra = 2;
	}
rackCalidad.freeAll();
""")

funcion("cerrarJornada", "void", [], """
int objetivo = 0, aTiempo = 0;
String detalle = "";
for (int m = 0; m < 5; m++) {
	objetivo += ofDia[m];
	aTiempo += aTiempoDia[m];
	int f = ofDia[m] - aTiempoDia[m];
	faltanteModelo[m] += f;
	if (f > 0) detalle += " " + abreviaturas[m] + ":" + f;
}
int faltante = objetivo - aTiempo;
diasSimulados++;
if (faltante > 0) diasSinCumplir++;
if (ausentesHoy > 0) {
	diasConAusencias++;
	faltanteConAusencias += faltante;
} else {
	diasSinAusencias++;
	faltanteSinAusencias += faltante;
}
registrarPresencia(duracionTurnoMin);
historial.add(String.format("S%d %-9s OF %3d | a tiempo %3d (%3.0f%%) | faltan %3d%s | aus %d cob %d sin cubrir %d",
	semana + 1, nombreDia(dia), objetivo, aTiempo, objetivo > 0 ? 100.0 * aTiempo / objetivo : 100.0,
	faltante, detalle, ausentesHoy, coberturasHoy, vacantesCriticasHoy));
traceln(historial.get(historial.size() - 1));
cerrarMuestras();
dia++;
if (dia < diasPorSemana) iniciarJornada();
else iniciarRecuperacion();
""")

funcion("iniciarRecuperacion", "void", [], """
int pendientes = liberadasSemana - terminadasSemana;
if (pendientes <= 0) {
	historial.add(String.format("S%d Fin de semana: no hace falta recuperar", semana + 1));
	traceln(historial.get(historial.size() - 1));
	finSemana();
	return;
}
// Jornada de recuperación: su OF es el faltante (unidades en proceso + sin iniciar)
enRecuperacion = true;
tInicioRecuperacion = time();
for (int m = 0; m < 5; m++) prodDia[m] = 0;
asignarAsistencia(probAusenciaFinDeSemana);
asignarCoberturas();
ubicarOperarios();
personasRecuperacion = 0;
for (Operario o : ops) if (o.presente) personasRecuperacion++;
pendientesInicioRecuperacion = pendientes;
eventoCierreJornada.restart(maxHorasRecuperacion * 60);
""")

funcion("finRecuperacion", "void", [], """
if (!enRecuperacion) return;
eventoCierreJornada.reset();
eventoFinRecuperacion.reset();
double minutos = time() - tInicioRecuperacion;
double horasHombre = minutos / 60.0 * personasRecuperacion;
double costo = horasHombre * valorHoraNormal * recargoFinDeSemana;
registrarPresencia(minutos);
horasExtraTotal += horasHombre;
costoHorasExtraTotal += costo;
int sinRecuperar = liberadasSemana - terminadasSemana;
historial.add(String.format("S%d Fin de semana: %d pendientes, %d personas, %.1f h -> %.0f h-hombre ($ %,.0f)%s",
	semana + 1, pendientesInicioRecuperacion, personasRecuperacion, minutos / 60.0, horasHombre, costo,
	sinRecuperar > 0 ? " | quedan " + sinRecuperar + " para la semana siguiente" : ""));
traceln(historial.get(historial.size() - 1));
enRecuperacion = false;
cerrarMuestras();
finSemana();
""")

funcion("finSemana", "void", [], """
semana++;
liberadasSemana -= terminadasSemana; // lo no recuperado pasa a la semana siguiente
terminadasSemana = 0;
for (int m = 0; m < 5; m++) {
	ofSemana[m] = 0;
	prodSemana[m] = 0;
}
if (semana < semanasSimuladas) {
	dia = 0;
	iniciarJornada();
} else {
	simulacionTerminada = true;
	traceln(resumenTexto());
	if (detenerAlFinal) finishSimulation();
}
""")

funcion("alFinalizarInspeccion", "void", [("b", "Balanza")], """
int m = b.tipoModelo;
inspeccionadas[m]++;
b.rechazada = randomTrue(probRechazo);
if (b.rechazada) rechazadas[m]++; // se registra; el retrabajo queda fuera del alcance
""")

funcion("alIngresarStock", "void", [("b", "Balanza")], """
int m = b.tipoModelo;
enStock[m]++;
sumaTiempoSistema[m] += time() - b.tIngreso;
sumaEspera[m] += b.esperaTotal;
""")

funcion("costoHorasNormales", "double", [], """
int empleados = nPuestos + operariosReserva + 1 + empleadosDeposito; // +1 inspector de calidad
return empleados * duracionTurnoMin / 60.0 * diasSimulados * valorHoraNormal;
""")

funcion("costoTotal", "double", [], """
return costoHorasNormales() + costoHorasExtraTotal + costoReorganizacion;
""")

funcion("utilizacion", "double", [("e", "Especialidad")], """
// Fracción del tiempo presente en que la especialidad trabaja o camina
double ocupado = 0, disponible = 0;
double transcurrido = simulacionTerminada ? 0 : time() - (enRecuperacion ? tInicioRecuperacion : tInicioJornada);
for (Operario o : ops) {
	if (o.especialidad != e) continue;
	ocupado += o.tOcupado + (o.estado != 0 ? time() - o.tInicioOcupado : 0);
	disponible += o.minPresente + (o.presente ? transcurrido : 0);
}
return disponible > 0 ? Math.min(1, ocupado / disponible) : 0;
""")

# --- Textos y colores del tablero -------------------------------------------
funcion("textoReloj", "String", [], """
if (simulacionTerminada) return String.format("Simulación terminada: %d jornadas, %d semanas. Resumen completo en la consola.", diasSimulados, semana);
if (diaGlobal == 0) return "Preparando la primera jornada...";
double t = time() - (enRecuperacion ? tInicioRecuperacion : tInicioJornada);
int h = (int) (t / 60), mi = (int) (t % 60);
if (enRecuperacion)
	return String.format("Semana %d · Recuperación de fin de semana · %02d:%02d h · pendientes %d · %d personas",
		semana + 1, h, mi, liberadasSemana - terminadasSemana, personasRecuperacion);
return String.format("Semana %d · %s · %02d:%02d h de un turno de %.0f h · tiempos: %s",
	semana + 1, nombreDia(dia), h, mi, duracionTurnoMin / 60, fuenteTiempos);
""")

funcion("textoOF", "String", [], """
StringBuilder s = new StringBuilder();
s.append(String.format("%-10s %7s %9s %8s %9s %12s%n", "Modelo", "OF día", "A tiempo", "Hoy", "Faltante", "Semana"));
for (int m = 0; m < 5; m++)
	s.append(String.format("%-10s %7d %9d %8d %9d %6d/%-5d%n", nombresModelo[m], ofDia[m], aTiempoDia[m],
		prodDia[m], Math.max(0, ofDia[m] - aTiempoDia[m]), prodSemana[m], ofSemana[m]));
int of = sumar(ofDia), aTiempo = sumar(aTiempoDia);
s.append(String.format("%-10s %7d %9d %8d %9d %6d/%-5d", "TOTAL", of, aTiempo, sumar(prodDia),
	Math.max(0, of - aTiempo), sumar(prodSemana), sumar(ofSemana)));
return s.toString();
""")

funcion("textoPersonal", "String", [], """
int presentes = 0;
double ocupado = 0;
for (Operario o : ops) {
	if (o.presente) presentes++;
	ocupado += o.tOcupado;
}
return String.format("Operarios de línea %d + reserva %d | presentes %d | ausentes %d%n", nPuestos, operariosReserva, presentes, ausentesHoy)
	+ String.format("Puestos vacantes %d | coberturas %d | críticos sin cubrir %d | puesto-min vacantes %.0f%n",
		vacantesHoy, coberturasHoy, vacantesCriticasHoy, minutosVacantesTotal)
	+ String.format("Utilización: Armador %3.0f%% | Ajustador %3.0f%% | Controlador %3.0f%% | Embalador %3.0f%%%n",
		100 * utilizacion(Especialidad.Armador), 100 * utilizacion(Especialidad.Ajustador),
		100 * utilizacion(Especialidad.Controlador), 100 * utilizacion(Especialidad.Embalador))
	+ String.format("Caminando: %.0f min (%.1f%% del tiempo ocupado) | rack de materiales en uso %d/%d",
		caminataTotalMin, ocupado > 0 ? 100 * caminataTotalMin / ocupado : 0, rackMateriales.busy(), rackMateriales.size());
""")

funcion("textoColas", "String", [], """
int[] cola = new int[4];
int nuevas = 0;
for (int i = 0; i < tomarOperario.size(); i++) {
	Balanza b = tomarOperario.get(i);
	if (b.paso == 0) nuevas++;
	else if (b.paso < recLen[b.tipoModelo]) cola[recTipo[b.tipoModelo][b.paso]]++;
}
return String.format("Esperando operario: sin iniciar %d | armado %d | ajuste %d | control final %d | embalaje %d%n",
		nuevas, cola[T_ARMADO], cola[T_AJUSTE], cola[T_CONTROL], cola[T_EMBALAJE])
	+ String.format("En proceso %d | rack de espera de calidad %d | esperando inspector %d | en stock %d",
		enProceso, rackCalidad.size(), tomarInspector.size(), sumar(enStock));
""")

funcion("textoCalidad", "String", [], """
StringBuilder s = new StringBuilder();
for (int m = 0; m < 5; m++)
	s.append(String.format("%-10s inspec. %3d | rechazos %2d | stock %5d | t. sistema %6.1f min | espera %6.1f min%n",
		nombresModelo[m], inspeccionadas[m], rechazadas[m], enStock[m],
		enStock[m] > 0 ? sumaTiempoSistema[m] / enStock[m] : 0, enStock[m] > 0 ? sumaEspera[m] / enStock[m] : 0));
return s.toString().trim();
""")

funcion("textoCostos", "String", [], """
return String.format("Jornadas %d | sin cumplir la OF %d (%.0f%%) | faltante acumulado %d u.%n",
		diasSimulados, diasSinCumplir, diasSimulados > 0 ? 100.0 * diasSinCumplir / diasSimulados : 0, sumar(faltanteModelo))
	+ String.format("Faltante medio por jornada: con ausencias %.1f u. (%d) | sin ausencias %.1f u. (%d)%n",
		diasConAusencias > 0 ? faltanteConAusencias / diasConAusencias : 0, diasConAusencias,
		diasSinAusencias > 0 ? faltanteSinAusencias / diasSinAusencias : 0, diasSinAusencias)
	+ String.format("Horas extra de fin de semana %.1f h-hombre | costo (x%.1f) $ %,.0f%n",
		horasExtraTotal, recargoFinDeSemana, costoHorasExtraTotal)
	+ String.format("Horas normales $ %,.0f | reorganización $ %,.0f | COSTO TOTAL $ %,.0f",
		costoHorasNormales(), costoReorganizacion, costoTotal());
""")

funcion("textoHistorial", "String", [], """
StringBuilder s = new StringBuilder();
for (int i = Math.max(0, historial.size() - 10); i < historial.size(); i++) s.append(historial.get(i)).append('\\n');
return historial.isEmpty() ? "Todavía no cerró ninguna jornada." : s.toString().trim();
""")

funcion("textoEscenario", "String", [], """
return String.format("Escenario: OF %d | secuencia %d | %d+%d líneas | extra A/J/C/E %d/%d/%d/%d | reserva %d | coberturas entre especialidades: %s",
	ofSeleccionada, reglaSecuencia, lineasArmado, lineasCF, extraArmadores, extraAjustadores, extraControladores,
	extraEmbaladores, operariosReserva, coberturaEntreEspecialidades ? "sí" : "no");
""")

funcion("resumenTexto", "String", [], """
StringBuilder s = new StringBuilder();
s.append("=== KRETZ | RESUMEN DEL ESCENARIO ===\\n").append(textoEscenario()).append('\\n');
s.append("--- Producción (última jornada) ---\\n").append(textoOF()).append('\\n');
s.append("--- Personal ---\\n").append(textoPersonal()).append('\\n');
s.append("--- Calidad y tiempos ---\\n").append(textoCalidad()).append('\\n');
s.append("--- Cumplimiento y costos ---\\n").append(textoCostos()).append('\\n');
s.append("--- Historial ---\\n");
for (String fila : historial) s.append(fila).append('\\n');
s.append("=== FIN DEL RESUMEN ===");
return s.toString();
""")

funcion("colorPuesto", "Color", [("p", "int")], """
if (pAtiende[p] < 0 || pAtiende[p] >= ops.size()) return new Color(220, 70, 70); // vacante sin cubrir
Operario o = ops.get(pAtiende[p]);
boolean trabajando = o.puestoTrabajo == p && o.estado == 2;
if (pAtiende[p] != pTitular[p]) return trabajando ? new Color(245, 140, 30) : new Color(252, 211, 150); // cubierto
return trabajando ? new Color(34, 160, 80) : new Color(175, 225, 190); // trabajando / ocioso
""")

funcion("etiquetaPuesto", "String", [("p", "int")], """
String[] siglas = { "A", "AJ", "CF", "EM" };
return siglas[pTipo[p]] + (pTipo[p] == T_ARMADO && pNum[p] > 0 ? String.valueOf(pNum[p]) : "");
""")

funcion("nombreLinea", "String", [("l", "int")], """
if (l >= lineasArmado + lineasCF) return "";
return l < lineasArmado ? "ARM " + (l + 1) : "CF " + (l - lineasArmado + 1);
""")

# ---------------------------------------------------------------------------
# Código de arranque y eventos
# ---------------------------------------------------------------------------
STARTUP = """// La primera jornada arranca cuando los operarios están creados y dentro de la planta
eventoInicioJornada.restart(0.01);"""

EVENTOS = [
    ("eventoInicioJornada", "iniciarJornada();"),
    ("eventoCierreJornada", "if (enRecuperacion) finRecuperacion();\nelse cerrarJornada();"),
    ("eventoFinRecuperacion", "finRecuperacion();"),
]
