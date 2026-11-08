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
    ("empleadosDeposito", "int", "10", "Empleados de depósito (solo para costos)"),
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
    # Despacho: un camión retira el stock dos veces por jornada (no en la recuperación)
    ("horaCamion1Min", "double", "180", "Llegada del primer camión (min desde el inicio de la jornada)"),
    ("horaCamion2Min", "double", "360", "Llegada del segundo camión (min desde el inicio de la jornada)"),
    ("cargadoresDeposito", "int", "3", "Empleados de depósito que cargan el camión (de los de depósito)"),
    ("tiempoCargaCajaMin", "double", "0.5", "Tiempo para subir una caja al camión (min)"),
    ("velocidadCamion", "double", "2.8", "Velocidad del camión en el predio (m/s)"),
    # Réplicas y resultados
    ("nombreEscenario", "String", '"Escenario actual"', "Nombre del escenario (para los resultados)"),
    ("semilla", "long", "0", "Semilla (0 = aleatoria; la usada queda registrada)"),
    ("guardarResultados", "boolean", "true", "Guardar resultados en Resultados/*.csv"),
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
    # Puestos: columnas de 6 mesas pegadas a lo largo del eje Y. (pX, pY) es el lugar
    # del operario, al costado derecho de su mesa; la mesa está mesaOffset px a la izquierda
    ("origenPuestosX", "double", "997"),
    ("origenPuestosY", "double", "235"),
    ("mesasPorColumna", "int", "6"),
    ("separacionColumnas", "double", "52"),
    ("largoMesa", "double", "40"),
    ("mesaOffset", "double", "17"),
    # Cajas de producto (alturas en px sobre el piso)
    ("alturaMesa", "double", "14"),
    ("alturaCajaEnMano", "double", "12"),
    # Mesa del inspector y puntos de entrega (los racks son elementos Storage del plano)
    ("inspectorX", "double", "1330"),
    ("inspectorY", "double", "420"),
    ("stockFrenteX", "double", "1380"),
    ("stockFrenteY", "double", "395"),
    # Pie de los racks: si un rack se llenara, las cajas quedan en el piso delante de él
    ("pieCalidadX", "double", "1480"),
    ("pieCalidadY", "double", "532"),
    ("pieStockX", "double", "1440"),
    ("pieStockY", "double", "395"),
    ("contadorPie", "int", "0"),
    ("kitsEnRack", "int", "0"),
    ("celdasRackMateriales", "int", "60"),
    ("diagnosticoRacks", "boolean", "false"),
    # Recorrido del camión por el camino de afuera y andén frente a la puerta del depósito
    ("camionEntradaX", "double", "1720"),
    ("camionEntradaY", "double", "660"),
    ("andenX", "double", "1432"),
    ("andenY", "double", "640"),
    ("camionSalidaX", "double", "940"),
    ("camionSalidaY", "double", "660"),
    ("camionActual", "CamionRetiro", "null"),
    ("colaCamiones", "java.util.LinkedList<CamionRetiro>", "new java.util.LinkedList<CamionRetiro>()"),
    ("cajasPorCargar", "int", "0"),
    ("cajasEnCamion", "int", "0"),
    ("contadorCargadores", "int", "0"),
    ("paredNavesX", "double", "1281.6"),
    ("puertaX", "double", "1281.6"),
    ("puertaY", "double", "515"),
    ("rackX", "double", "1448"),
    ("rackY", "double", "275"),
    ("zonaAusentesX", "double", "962"),
    ("zonaAusentesY", "double", "603"),
    ("zonaReservaX", "double", "1142"),
    ("zonaReservaY", "double", "543"),
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
    # Indicadores acumulados para la exportación de resultados
    ("semillaUsada", "long", "0"),
    ("ofTotal", "int[]", "new int[5]"),
    ("aTiempoTotal", "int[]", "new int[5]"),
    ("sumaEsperaTipo", "double[]", "new double[4]"),
    ("maxEsperaTipo", "double[]", "new double[4]"),
    ("nEsperaTipo", "int[]", "new int[4]"),
    ("unidadesLinea", "int[]", "new int[12]"),
    ("faltanteSemana", "int", "0"),
    ("horasExtraSemana", "double", "0"),
    ("costoExtraSemana", "double", "0"),
    ("pendientesSemana", "int", "0"),
]

VARIABLES_BALANZA = [
    ("tipoModelo", "int", "0"),
    ("paso", "int", "0"),
    ("lineaArmado", "int", "-1"),
    ("lineaCF", "int", "-1"),
    ("puestoActual", "int", "-1"),
    ("opActual", "Operario", "null"),
    ("fase", "int", "0"),
    ("tramos", "java.util.LinkedList<double[]>", "new java.util.LinkedList<double[]>()"),
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
    # Caja que representa a la unidad en la animación
    ("color", "Color", "new Color(160, 120, 60)"),
    ("mostrarCaja", "boolean", "true"),
    ("cajaEnRack", "boolean", "false"),
    ("cajaAlPie", "boolean", "false"),
    ("decisionRack", "int", "0"),
    ("retirarDeRack", "boolean", "false"),
    ("cargador", "Operario", "null"),
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
if (nPuestos > 36) traceln("Hay " + nPuestos + " puestos: el plano dibuja solo los primeros 36 (6 columnas de 6 mesas).");
plantaConstruida = true;
""")

funcion("agregarPuesto", "void", [("linea", "int"), ("tipo", "int"), ("num", "int")], """
if (nPuestos >= pLinea.length || linea >= columnasLinea.length) {
	traceln("Se alcanzó el máximo de puestos del modelo; se ignora un puesto adicional.");
	return;
}
columnasLinea[linea]++;
int p = nPuestos++;
pLinea[p] = linea;
pTipo[p] = tipo;
pNum[p] = num;
pX[p] = posicionPuestoX(p);
pY[p] = posicionPuestoY(p);
pTitular[p] = -1;
pAtiende[p] = -1;
""")

# La misma fórmula la usa desarrollar_modelo.py para dibujar las mesas 3D
funcion("posicionPuestoX", "double", [("p", "int")], """
// Columnas de mesasPorColumna mesas; más de 6 columnas no entran en la nave, así que
// los puestos siguientes se intercalan entre las columnas existentes
int columna = p / mesasPorColumna;
return origenPuestosX + (columna % 6) * separacionColumnas + (columna / 6) * separacionColumnas / 2;
""")

funcion("posicionPuestoY", "double", [("p", "int")], """
return origenPuestosY + (p % mesasPorColumna) * largoMesa;
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
o.setSpeed(velocidadOperario, MPS);
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
// Los operarios los crea el ResourcePool; si todavía no están, se reintenta enseguida
if (ops.size() < nPuestos + operariosReserva) {
	eventoInicioJornada.restart(0.01);
	return;
}
enRecuperacion = false;
diaGlobal++;
tInicioJornada = time();
for (int m = 0; m < 5; m++) {
	ofDia[m] = ofEjemplo(ofSeleccionada, m);
	ofSemana[m] += ofDia[m];
	ofTotal[m] += ofDia[m];
	prodDia[m] = 0;
	aTiempoDia[m] = 0;
}
asignarAsistencia(Math.min(1, probAusencia * factorAusenciaDia[dia % 5]));
asignarCoberturas();
ubicarOperarios();
liberarUnidadesOF();
eventoCierreJornada.restart(duracionTurnoMin);
eventoCamion1.restart(horaCamion1Min);
eventoCamion2.restart(horaCamion2Min);
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

funcion("asegurarEspacio", "void", [("a", "Agent")], """
// El ResourcePool y la Source crean a operarios y unidades sin espacio asignado;
// como el modelo los mueve por código, se los incorpora al espacio y nivel de Main
if (a.getSpace() == null) a.setSpace(this);
if (a.getLevel() == null) a.setLevel(level);
""")

funcion("ubicarOperarios", "void", [], """
int ausentes = 0, reservas = 0;
for (Operario o : ops) asegurarEspacio(o);
for (Operario o : ops) {
	if (o.estado != 0) continue; // quien está trabajando termina su tarea donde está
	if (!o.presente) {
		o.jumpTo(zonaAusentesX + (ausentes % 10) * 14, zonaAusentesY + (ausentes / 10) * 14);
		ausentes++;
	} else if (!o.puestosAtendidos.isEmpty()) {
		int p = o.puestosAtendidos.get(0);
		o.jumpTo(pX[p], pY[p]);
	} else {
		o.jumpTo(zonaReservaX + (reservas % 5) * 14, zonaReservaY);
		reservas++;
	}
}
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
eventoReponerKits.restart(0);
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
// La caja del kit entra al rack de materiales cuando hay una celda libre (reponerKits) y queda
// ahí hasta que el operario la retira; mientras espera lugar no se dibuja
asegurarEspacio(b);
b.color = colorModelo(m);
b.mostrarCaja = false;
""")

funcion("colorModelo", "Color", [("m", "int")], """
Color[] colores = { new Color(37, 99, 235), new Color(234, 88, 12), new Color(22, 163, 74),
	new Color(147, 51, 234), new Color(220, 38, 38) };
return colores[m];
""")

funcion("recogerCaja", "void", [("b", "Balanza")], """
// El operario sale del rack con la caja de materiales en la mano
b.cajaEnRack = false;
b.jumpTo(b.opActual.getX(), b.opActual.getY() + 6, alturaCajaEnMano);
""")

funcion("moverCaja", "void", [("b", "Balanza"), ("x", "double"), ("y", "double"), ("minutos", "double")], """
// La caja llega a las manos del operario al mismo tiempo que él: desde el rack la lleva
// encima; entre pasos viaja desde la mesa anterior. Mientras está en un rack o al pie no se mueve
if (b.cajaEnRack || b.cajaAlPie) return;
double metros = Math.hypot(x - b.getX(), y + 6 - b.getY()) / pxPorMetro;
if (metros <= 0.05 || minutos <= 0) {
	b.jumpTo(x, y + 6, alturaCajaEnMano);
	return;
}
b.setSpeed(metros / (minutos * 60), MPS);
b.moveTo(x, y + 6, alturaCajaEnMano);
""")

funcion("dejarCajaEnMesa", "void", [("b", "Balanza")], """
int p = b.puestoActual;
if (p >= 0) b.jumpTo(pX[p] - mesaOffset, pY[p], alturaMesa);
""")

funcion("llevarAInspeccion", "void", [("b", "Balanza")], """
b.jumpTo(inspectorX, inspectorY, alturaMesa);
""")

# --- Capacidad de los racks ----------------------------------------------------
funcion("hayLugar", "boolean", [("s", "Storage")], """
// Cada celda de un Storage guarda una sola caja; se deja una de margen
return celdasLibres(s) > 1;
""")

funcion("celdasLibres", "int", [("s", "Storage")], """
// Si el rack todavía no armó sus celdas (no guardó nada y no informa lugar), se toma su capacidad
int libres = s.nFreeCells();
if (libres <= 0 && s.size() == 0) libres = s.capacity();
return libres;
""")

funcion("reponerKits", "void", [], """
// Los kits de la OF entran al rack de materiales a medida que se retiran los que ya están.
// Se lleva la cuenta propia de kits en el rack: no depende de cuándo el rack arma sus celdas
// ni de cuándo cada Store reserva la suya
if (!diagnosticoRacks) {
	diagnosticoRacks = true;
	traceln(String.format("Racks al iniciar: materiales capacidad %d, libres %d | calidad %d, libres %d | stock %d, libres %d",
		almacenMateriales.capacity(), almacenMateriales.nFreeCells(), almacenCalidad.capacity(),
		almacenCalidad.nFreeCells(), almacenStock.capacity(), almacenStock.nFreeCells()));
}
int capacidad = almacenMateriales.capacity() > 0 ? almacenMateriales.capacity() : celdasRackMateriales;
int entran = Math.min(esperaLugarKit.size(), capacidad - 1 - kitsEnRack);
for (int k = 0; k < entran; k++) esperaLugarKit.free(esperaLugarKit.get(0));
// Si quedaron kits esperando y no hay ninguno en el rack, nadie va a disparar la reposición
if (esperaLugarKit.size() > 0 && kitsEnRack + Math.max(0, entran) == 0) eventoReponerKits.restart(1);
""")

funcion("decidirRack", "boolean", [("b", "Balanza"), ("s", "Storage")], """
// Se decide una sola vez por rack (AnyLogic puede evaluar dos veces la condición de un
// SelectOutput, y guardar la caja cambia las celdas libres antes de la segunda evaluación)
if (b.decisionRack == 0) b.decisionRack = hayLugar(s) ? 1 : 2;
return b.decisionRack == 1;
""")

funcion("llegarAlRack", "void", [("b", "Balanza"), ("pieX", "double"), ("pieY", "double")], """
// Si el rack estaba lleno la caja queda en el piso, delante de él. retirarDeRack no cambia hasta
// el próximo rack: lo usan los SelectOutput que deciden si hay que pasar por el Retrieve
b.decisionRack = 0;
b.retirarDeRack = b.cajaEnRack;
if (b.cajaEnRack) return;
b.cajaAlPie = true;
int k = contadorPie++;
b.jumpTo(pieX - 20 + (k % 6) * 8, pieY + (k / 6 % 3) * 8, (k / 18 % 4) * 8);
""")

# --- Despacho: camión y cargadores de depósito -------------------------------
funcion("prepararCamion", "void", [("c", "CamionRetiro")], """
asegurarEspacio(c);
c.jumpTo(camionEntradaX, camionEntradaY);
""")

funcion("moverCamion", "double", [("c", "CamionRetiro"), ("x", "double"), ("y", "double")], """
// Devuelve los minutos del trayecto: lo usa el Delay como tiempo de viaje
double metros = Math.hypot(x - c.getX(), y - c.getY()) / pxPorMetro;
c.setSpeed(velocidadCamion, MPS);
if (metros > 0.05) c.moveTo(x, y);
return metros / velocidadCamion / 60.0;
""")

funcion("alLlegarCamion", "void", [("c", "CamionRetiro")], """
// Si otro camión todavía está cargando, este espera su turno en el andén
if (camionActual == null) iniciarCarga(c);
else colaCamiones.add(c);
""")

funcion("iniciarCarga", "void", [("c", "CamionRetiro")], """
// Se carga lo que hay en el rack de stock al llegar; lo que entra después espera al próximo camión
camionActual = c;
cajasEnCamion = 0;
cajasPorCargar = esperaDespacho.size();
if (cajasPorCargar == 0) eventoSalidaCamion.restart(0);
else esperaDespacho.freeAll();
""")

funcion("cajaCargada", "void", [], """
// En un evento propio: la salida libera agentes de otros bloques
if (--cajasPorCargar <= 0) eventoSalidaCamion.restart(0);
""")

funcion("despacharCamion", "void", [], """
if (camionActual == null) return;
enCamion.freeAll(); // las cajas se van con el camión
CamionRetiro c = camionActual;
camionActual = null;
cargandoCamion.free(c);
if (!colaCamiones.isEmpty()) iniciarCarga(colaCamiones.removeFirst());
""")

funcion("prepararCargador", "void", [("o", "Operario")], """
// Empleados de depósito (de los ya contados en costos), no forman parte de los operarios de línea
asegurarEspacio(o);
o.especialidad = Especialidad.Polivalente;
o.presente = true;
o.estado = 0;
o.setSpeed(velocidadOperario, MPS);
o.jumpTo(stockFrenteX - 20 + (contadorCargadores++ % 4) * 14, stockFrenteY + 26);
""")

funcion("alTomarCargador", "void", [("b", "Balanza"), ("o", "Operario")], """
b.cargador = o;
o.estado = 1;
""")

funcion("caminarCargador", "double", [("b", "Balanza"), ("x", "double"), ("y", "double")], """
// El cargador camina en línea recta; si ya retiró la caja, la lleva en la mano
Operario o = b.cargador;
double metros = Math.hypot(x - o.getX(), y - o.getY()) / pxPorMetro;
double minutos = metros / velocidadOperario / 60.0;
if (metros > 0.05) o.moveTo(x, y);
moverCaja(b, x, y, minutos);
o.estado = 1;
return minutos;
""")

funcion("finCaminataCargador", "void", [("b", "Balanza")], """
Operario o = b.cargador;
if (o.isMoving()) o.jumpTo(o.getTargetX(), o.getTargetY());
if (!b.cajaEnRack) {
	// Si la caja estaba al pie del rack, el cargador la levanta acá
	b.cajaAlPie = false;
	b.jumpTo(o.getX(), o.getY() + 6, alturaCajaEnMano);
}
""")

funcion("subirCaja", "void", [("b", "Balanza")], """
// La caja queda apilada en la caja del camión
b.cargador.estado = 2;
int k = cajasEnCamion++;
b.jumpTo(andenX - 28 + (k % 8) * 8, andenY - 6 + (k / 8 % 2) * 8, 16 + (k / 16) * 8);
""")

funcion("alLiberarCargador", "void", [("b", "Balanza")], """
b.cargador.estado = 0;
b.cargador = null;
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
double espera = time() - b.tInicioEspera;
b.esperaTotal += espera;
// Espera en cola por tipo de puesto (identifica cuellos de botella)
int tipo = recTipo[b.tipoModelo][b.paso];
sumaEsperaTipo[tipo] += espera;
maxEsperaTipo[tipo] = Math.max(maxEsperaTipo[tipo], espera);
nEsperaTipo[tipo]++;
if (b.paso == 0) {
	// Primer paso: el mismo operario va al rack único de materiales y después a su puesto
	b.fase = 1;
	planificarCaminata(b, rackX, rackY);
} else {
	b.fase = 2;
	planificarCaminata(b, pX[b.puestoActual], pY[b.puestoActual]);
}
""")

funcion("planificarCaminata", "void", [("b", "Balanza"), ("destinoX", "double"), ("destinoY", "double")], """
b.tramos.clear();
Operario o = b.opActual;
boolean origenEnProduccion = o.getX() < paredNavesX;
boolean destinoEnProduccion = destinoX < paredNavesX;
// Entre naves se pasa por la puerta de la pared interna
if (origenEnProduccion != destinoEnProduccion) b.tramos.add(new double[] { puertaX, puertaY });
b.tramos.add(new double[] { destinoX, destinoY });
""")

funcion("iniciarTramo", "double", [("b", "Balanza")], """
// El tramo se saca de la lista al empezar a caminar: asi la condicion de masTramos
// no cambia entre que se evalua y que la unidad sale del Delay
double[] destino = b.tramos.removeFirst();
Operario o = b.opActual;
double metros = Math.hypot(destino[0] - o.getX(), destino[1] - o.getY()) / pxPorMetro;
double minutos = metros / velocidadOperario / 60.0;
if (metros > 0.05) o.moveTo(destino[0], destino[1]);
moverCaja(b, destino[0], destino[1], minutos);
o.estado = 1;
b.tCaminata += minutos;
o.tCaminando += minutos;
caminataTotalMin += minutos;
return minutos;
""")

funcion("finTramo", "void", [("b", "Balanza")], """
// Asegura que el operario quede exactamente en el destino del tramo
Operario o = b.opActual;
if (o.isMoving()) o.jumpTo(o.getTargetX(), o.getTargetY());
if (!b.cajaEnRack) b.jumpTo(o.getX(), o.getY() + 6, alturaCajaEnMano);
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
if (!o.presente) o.jumpTo(zonaAusentesX, zonaAusentesY);
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
if (!enRecuperacion && b.diaOF == diaGlobal) {
	aTiempoDia[m]++;
	aTiempoTotal[m]++;
}
if (b.lineaArmado >= 0) unidadesLinea[b.lineaArmado]++;
if (b.lineaCF >= 0) unidadesLinea[b.lineaCF]++;
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
faltanteSemana += faltante;
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
	pendientesSemana = 0;
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
horasExtraSemana = horasHombre;
costoExtraSemana = costo;
pendientesSemana = pendientesInicioRecuperacion;
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
exportarSemana();
faltanteSemana = 0;
horasExtraSemana = 0;
costoExtraSemana = 0;
pendientesSemana = 0;
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
	exportarCorrida();
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

# --- Exportación de resultados (una fila por corrida y una por semana) -------
funcion("anexarCSV", "void", [("archivo", "String"), ("encabezado", "String"), ("fila", "String")], """
// Separador ; y coma decimal, como Datos/*.csv (Excel con configuración argentina)
if (!guardarResultados) return;
try {
	java.io.File f = new java.io.File(archivo);
	if (f.getParentFile() != null) f.getParentFile().mkdirs();
	boolean nuevo = !f.exists() || f.length() == 0;
	try (java.io.PrintWriter w = new java.io.PrintWriter(new java.io.OutputStreamWriter(
			new java.io.FileOutputStream(f, true), java.nio.charset.StandardCharsets.UTF_8))) {
		if (nuevo) w.println(encabezado);
		w.println(fila);
	}
} catch (Exception e) {
	traceln("No se pudo escribir " + archivo + ": " + e.getMessage());
}
""")

funcion("num", "String", [("v", "double")], """
return String.format(java.util.Locale.forLanguageTag("es-AR"), "%.4f", v);
""")

funcion("columnasEscenario", "String", [], """
return "escenario;semilla;of;regla_secuencia;lineas_armado;lineas_cf;armadores_linea;ajustadores_linea;"
	+ "controladores_linea_cf;embaladores_linea_cf;extra_armadores;extra_ajustadores;extra_controladores;"
	+ "extra_embaladores;reserva;cobertura_entre_especialidades;prob_ausencia;costo_reorganizacion";
""")

funcion("valoresEscenario", "String", [], """
return nombreEscenario + ";" + semillaUsada + ";" + ofSeleccionada + ";" + reglaSecuencia + ";" + lineasArmado + ";"
	+ lineasCF + ";" + armadoresPorLinea + ";" + ajustadoresPorLinea + ";" + controladoresPorLineaCF + ";"
	+ embaladoresPorLineaCF + ";" + extraArmadores + ";" + extraAjustadores + ";" + extraControladores + ";"
	+ extraEmbaladores + ";" + operariosReserva + ";" + (coberturaEntreEspecialidades ? 1 : 0) + ";"
	+ num(probAusencia) + ";" + num(costoReorganizacion);
""")

funcion("exportarSemana", "void", [], """
int of = sumar(ofSemana);
anexarCSV("Resultados/resultados_semanas.csv",
	columnasEscenario() + ";semana;of_semana;faltante_jornadas;pendientes_recuperacion;horas_extra;costo_horas_extra",
	valoresEscenario() + ";" + (semana + 1) + ";" + of + ";" + faltanteSemana + ";" + pendientesSemana + ";"
		+ num(horasExtraSemana) + ";" + num(costoExtraSemana));
""")

funcion("exportarCorrida", "void", [], """
StringBuilder h = new StringBuilder(columnasEscenario());
StringBuilder v = new StringBuilder(valoresEscenario());
int of = sumar(ofTotal), aTiempo = sumar(aTiempoTotal);
h.append(";semanas;jornadas;jornadas_sin_cumplir;of_total;a_tiempo_total;cumplimiento");
v.append(";" + semana + ";" + diasSimulados + ";" + diasSinCumplir + ";" + of + ";" + aTiempo + ";"
	+ num(of > 0 ? (double) aTiempo / of : 1));
for (int m = 0; m < 5; m++) {
	h.append(";faltante_" + abreviaturas[m].toLowerCase() + ";cumplimiento_" + abreviaturas[m].toLowerCase());
	v.append(";" + (ofTotal[m] - aTiempoTotal[m]) + ";" + num(ofTotal[m] > 0 ? (double) aTiempoTotal[m] / ofTotal[m] : 1));
}
h.append(";horas_extra;costo_horas_extra;costo_horas_normales;costo_total;sin_recuperar");
v.append(";" + num(horasExtraTotal) + ";" + num(costoHorasExtraTotal) + ";" + num(costoHorasNormales()) + ";"
	+ num(costoTotal()) + ";" + (liberadasSemana - terminadasSemana));
h.append(";coberturas;vacantes_criticas;puesto_min_vacantes;faltante_medio_con_ausencias;faltante_medio_sin_ausencias");
v.append(";" + coberturasTotal + ";" + vacantesCriticasTotal + ";" + num(minutosVacantesTotal) + ";"
	+ num(diasConAusencias > 0 ? faltanteConAusencias / diasConAusencias : 0) + ";"
	+ num(diasSinAusencias > 0 ? faltanteSinAusencias / diasSinAusencias : 0));
h.append(";util_armador;util_ajustador;util_controlador;util_embalador;caminata_min;caminata_fraccion");
double ocupado = 0;
for (Operario o : ops) ocupado += o.tOcupado;
v.append(";" + num(utilizacion(Especialidad.Armador)) + ";" + num(utilizacion(Especialidad.Ajustador)) + ";"
	+ num(utilizacion(Especialidad.Controlador)) + ";" + num(utilizacion(Especialidad.Embalador)) + ";"
	+ num(caminataTotalMin) + ";" + num(ocupado > 0 ? caminataTotalMin / ocupado : 0));
String[] tipos = { "armado", "ajuste", "control", "embalaje" };
for (int t = 0; t < 4; t++) {
	h.append(";espera_media_" + tipos[t] + ";espera_max_" + tipos[t]);
	v.append(";" + num(nEsperaTipo[t] > 0 ? sumaEsperaTipo[t] / nEsperaTipo[t] : 0) + ";" + num(maxEsperaTipo[t]));
}
for (int m = 0; m < 5; m++) {
	h.append(";t_sistema_" + abreviaturas[m].toLowerCase());
	v.append(";" + num(enStock[m] > 0 ? sumaTiempoSistema[m] / enStock[m] : 0));
}
for (int l = 0; l < lineasArmado + lineasCF && l < unidadesLinea.length; l++) {
	h.append(";unidades_" + nombreLinea(l).toLowerCase().replace(' ', '_'));
	v.append(";" + unidadesLinea[l]);
}
h.append(";inspeccionadas;rechazadas");
v.append(";" + sumar(inspeccionadas) + ";" + sumar(rechazadas));
anexarCSV("Resultados/resultados_corridas.csv", h.toString(), v.toString());
traceln("Resultados guardados en Resultados/resultados_corridas.csv (semilla " + semillaUsada + ")");
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
return String.format("%s (semilla %d) | OF %d | secuencia %d | %d+%d líneas | extra A/J/C/E %d/%d/%d/%d | reserva %d | coberturas entre especialidades: %s",
	nombreEscenario, semillaUsada, ofSeleccionada, reglaSecuencia, lineasArmado, lineasCF, extraArmadores, extraAjustadores, extraControladores,
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
// Las líneas ocupan varias columnas de mesas, así que cada mesa dice a qué línea pertenece
String[] siglas = { "A", "AJ", "CF", "EM" };
return nombreLinea(pLinea[p]) + " · " + siglas[pTipo[p]]
	+ (pTipo[p] == T_ARMADO && pNum[p] > 0 ? String.valueOf(pNum[p]) : "");
""")

funcion("nombreLinea", "String", [("l", "int")], """
if (l >= lineasArmado + lineasCF) return "";
return l < lineasArmado ? "ARM " + (l + 1) : "CF " + (l - lineasArmado + 1);
""")

# ---------------------------------------------------------------------------
# Código de arranque y eventos
# ---------------------------------------------------------------------------
STARTUP = """// Semilla de la corrida: la elegida o una al azar, que queda registrada para poder repetirla
semillaUsada = semilla != 0 ? semilla : 1 + (long) (Math.random() * 999999999L);
getDefaultRandomGenerator().setSeed(semillaUsada);
// La primera jornada arranca apenas el ResourcePool crea a los operarios
eventoInicioJornada.restart(0.01);"""

EVENTOS = [
    ("eventoInicioJornada", "iniciarJornada();"),
    ("eventoCierreJornada", "if (enRecuperacion) finRecuperacion();\nelse cerrarJornada();"),
    ("eventoFinRecuperacion", "finRecuperacion();"),
    ("eventoCamion1", "llegaCamion.inject(1);"),
    ("eventoCamion2", "llegaCamion.inject(1);"),
    ("eventoSalidaCamion", "despacharCamion();"),
    ("eventoReponerKits", "reponerKits();"),
]
