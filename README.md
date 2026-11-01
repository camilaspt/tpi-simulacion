# TPI Simulación KRETZ

Trabajo práctico de simulación (AnyLogic) de la línea de producción y el depósito de la fábrica de balanzas **KRETZ**. Este documento resume el problema, los datos relevados y las decisiones de modelado tomadas hasta ahora, para que cualquiera del equipo pueda retomar el trabajo sin depender de que se lo expliquen de palabra.

## Objetivo

Construir un modelo de simulación de eventos discretos + peatonal en AnyLogic que represente:

1. El **armado** de las balanzas a lo largo de sus puestos de trabajo (líneas de Armado y de Control Final).
2. El **depósito**: recepción, almacenamiento y despacho de producto terminado.
3. El **movimiento real de las personas** (operarios) dentro de la planta, no solo los tiempos de proceso — se optó por modelar a los operarios como peatones (Pedestrian Library) desde el arranque, en vez de una animación simplificada.

## La planta

La planta física consta de dos naves:


| Nave                 | Dimensión aproximada | Uso                                             |
| -------------------- | -------------------- | ----------------------------------------------- |
| Planta de producción | 20 m × 25 m          | Líneas de Armado y Control Final                |
| Depósito             | 22 m × 25 m          | Almacenamiento y despacho de producto terminado |


Se optó por dibujar el piso como rectángulos a escala real (usando el `ScaleRuler` de AnyLogic) ubicados visualmente sobre la foto de la planta.

## Estructura organizativa

- **6 líneas de producción**: 4 de Armado + 2 de Control Final.
- **5 puestos de trabajo por línea**.
- **50 empleados en total**: ~30 asignados a las 6 líneas de producción (5 por línea) y ~20 al depósito.
- Los empleados pueden especializarse en: **Ajustador**, **Controlador**, **Embalador** (los puestos de armado propiamente dicho no requieren una especialización particular).

## Productos a simular

La simulación contempla **5 tipos de equipos** (modelos de balanza). 

### EQUIPO AILA 30KG (puestos y tiempos, según SAP)


| Secuencia | Línea         | Celda         | Puesto                                 | Tarea       | Tiempo (min) |
| --------- | ------------- | ------------- | -------------------------------------- | ----------- | ------------ |
| 1         | Armado        | Depósito      | Salida Depósito (retiro de materiales) | Armador     | 2            |
| 2         | Armado        | Celda 1       | Armado Puesto 1                        | Armador     | 3,5          |
| 3         | Armado        | Celda 1       | Armado Puesto 2                        | Armador     | 7            |
| 4         | Armado        | Celda 1       | Armado Puesto 3                        | Armador     | 7            |
| 5         | Armado        | Celda 1       | Armado Puesto 4                        | Armador     | 7,5          |
| 6         | Armado        | Celda 2       | Ajuste                                 | Ajustador   | 5            |
| 7         | Control Final | Control Final | Control Final                          | Controlador | 4,5          |
| 8         | Control Final | Embalaje      | Embalaje                               | Embalador   | 10           |


### BALANZA REPORT LT (modelo completo, versión más económica)


| Secuencia | Línea         | Celda         | Puesto                                       | Tarea       | Tiempo (min) |
| --------- | ------------- | ------------- | -------------------------------------------- | ----------- | ------------ |
| 1         | Armado        | Depósito      | Salida Depósito (retiro de materiales)       | Armador     | 2            |
| 2         | Armado        | Celda 1       | Armado                                       | Armador     | 11           |
| 3         | Armado        | Celda 3       | Ensamble Final, Calibrado y Cierre de Equipo | Ajustador   | 12           |
| 4         | Control Final | Control Final | Control Final y Metrológico                  | Controlador | 12           |
| 5         | Control Final | Embalaje      | Embalaje                                     | Embalador   | 12           |


**Caso particular — viaje a Depósito:** el primer paso de este equipo no es un puesto/recurso propio: es el mismo Armador que va a hacer el Puesto 2 (Celda 1) el que primero camina hasta el Depósito a buscar los materiales que necesita para armar, y después va a Celda 1. No hay una dotación de Depósito dedicada a esto — por eso, en el modelo, no se representa con un `Service` independiente sino con un único `Seize` del Armador seguido de dos `Delay` encadenados (uno en Depósito, uno en Celda 1) y recién ahí el `Release`. Como el Armador es un `Operario` (peatón), esto además sirve para validar que el movimiento peatonal entre las dos naves funciona bien.

Se confirmaron las dos preguntas abiertas: (a) el viaje a Depósito aplica a **todos** los equipos (ya se agregó como Secuencia 1 en las tablas de esta sección, incluido AILA 30KG), y (b) los materiales se retiran de un **rack único de fabricación**: todos los elementos para los 5 equipos están en el mismo rack, no hay racks separados por equipo. Esto simplifica el modelado del depósito: alcanza con un solo punto/rack de referencia para esta operación, en vez de una red de racks distintos según el equipo.

### BALANZA NOVEL ECO (gama media/baja)


| Secuencia | Línea         | Celda         | Puesto                                 | Tarea       | Tiempo (min) |
| --------- | ------------- | ------------- | -------------------------------------- | ----------- | ------------ |
| 1         | Armado        | Depósito      | Salida Depósito (retiro de materiales) | Armador     | 2            |
| 2         | Armado        | Celda 1       | Armado                                 | Armador     | 3,15         |
| 3         | Armado        | Celda 2       | Ajuste                                 | Ajustador   | 3            |
| 4         | Control Final | Control Final | Control Final                          | Controlador | 2,25         |
| 5         | Control Final | Embalaje      | Embalaje                               | Embalador   | 3            |


### BALANZA LURA (traída de China)


| Secuencia | Línea         | Celda         | Puesto                                 | Tarea       | Tiempo (min) |
| --------- | ------------- | ------------- | -------------------------------------- | ----------- | ------------ |
| 1         | Armado        | Depósito      | Salida Depósito (retiro de materiales) | Ajustador   | 2            |
| 2         | Armado        | Celda 2       | Ajuste                                 | Ajustador   | 4            |
| 3         | Control Final | Control Final | Control Final                          | Controlador | 3,15         |
| 4         | Control Final | Embalaje      | Embalaje                               | Embalador   | 3,15         |


**Caso particular — sin Celda 1:** este equipo llega ya armado desde China, así que no pasa por Armado/Celda 1. Por eso el viaje a Depósito no lo hace un Armador sino el **Ajustador**, que es quien realiza el primer puesto real de este equipo (Ajuste en Celda 2). Confirma la regla general: el que retira el material en Depósito es siempre el mismo operario que va a hacer el paso siguiente, sea cual sea su especialidad.

### BALANZA AURA (gama media)


| Secuencia | Línea         | Celda         | Puesto                                 | Tarea       | Tiempo (min) |
| --------- | ------------- | ------------- | -------------------------------------- | ----------- | ------------ |
| 1         | Armado        | Depósito      | Salida Depósito (retiro de materiales) | Armador     | 2            |
| 2         | Armado        | Celda 1       | Armado                                 | Armador     | 3,15         |
| 3         | Armado        | Celda 2       | Ajuste                                 | Ajustador   | 3            |
| 4         | Control Final | Control Final | Control Final                          | Controlador | 2,5          |
| 5         | Control Final | Embalaje      | Embalaje                               | Embalador   | 2,88         |


Con esto los 5 equipos ya tienen sus tiempos cargados en `Datos/tiempos_proceso.csv`. Sigue pendiente el dato de Celda 3 para REPORT LT (si es una celda física distinta o un alias) y la pregunta (b) de arriba sobre el retiro puntual de material en Depósito.

## Datos (`/Datos`)

- `tiempos_proceso.csv`: una fila por puesto/paso de proceso y equipo (Equipo, Secuencia, Linea_tipo, Celda, Puesto, Tarea, Tiempo_min, Tiempo_seg, Cantidad_operarios). Pensado para importarse directo a AnyLogic (Database → Import) y parametrizar los bloques de proceso.
- `dotacion_lineas.csv`: dotación y especializaciones disponibles por línea.

Los archivos usan `;` como separador y `,` como separador decimal (configuración regional argentina de Excel).

## Modelo en AnyLogic

El modelo completo se genera con un script: `scripts/desarrollar_modelo.py` parte del modelo base `TPI-Simulacion-KRETZ.alp` (que no se modifica) y escribe `TPI-Simulacion-KRETZ - copia.alp`. Todo el código Java del modelo (parámetros, variables, funciones) está en `scripts/modelo_java.py`.

```
py -3 scripts/desarrollar_modelo.py                      # regenera el .alp
py -3 scripts/desarrollar_modelo.py --verificar CARPETA  # compila el código contra las librerías de AnyLogic
```

Hay que cerrar el modelo en AnyLogic antes de regenerarlo (y borrar el `.autosave` si quedó uno).

### Decisiones de diseño

- **Unidad de tiempo**: minutos. Escala del plano: 16 px = 1 m.
- **Proceso (Process Modeling Library)**: un único flujo para los 5 modelos. Cada unidad (`Balanza`) sigue su receta (`Datos/tiempos_proceso.csv`): `Seize` del operario → `caminar` (espera a que llegue) → retiro en el rack (solo el primer paso) → `tarea` → `Release`, y se repite por cada paso. Así el mismo operario que retira los materiales hace el primer puesto.
- **Ruteo entre líneas equivalentes**: la condición de elección del `Seize` busca un operario que atienda un puesto apto para el paso, en la línea ya asignada a la unidad o en cualquier línea capaz de completar el equipo con el personal del día.
- **Operarios como peatones (Pedestrian Library)**: el `ResourcePool` (estático) solo asigna operarios. Cada operario entra al espacio peatonal (`Enter → PedEnter`) y se mueve en el lazo `PedGoTo → PedSelectOutput → PedWait`. El traslado a Depósito y entre puestos sale de la simulación peatonal, con las paredes como obstáculos; la unidad espera en `caminar` hasta que su operario llega.
- **Ausentismo y coberturas**: al inicio de cada jornada se sortea la asistencia; los puestos vacantes que frenan una línea se cubren con reserva polivalente, misma especialidad u otro operario (armado).
- **Control de calidad por muestreo**: el primer equipo de cada modelo se inspecciona al llegar al rack de calidad y el último al cierre de la jornada.
- **Cierre de jornada y fin de semana**: se compara lo producido a tiempo contra la OF; el faltante de la semana se recupera en una jornada de fin de semana cuyas horas-hombre se pagan al doble.
- **Semilla**: con `semilla = 0` cada corrida sortea una semilla nueva y la registra; poniendo esa semilla se repite exactamente la corrida.

### Escenarios (experimentos)

| Experimento | Escenario |
|---|---|
| `Simulation` | Escenario actual (dotación actual con horas extra) |
| `EscenarioContratacion` | Contratar 2 Ajustadores |
| `EscenarioContratacionArmadores` | Contratar 2 Armadores |
| `EscenarioContratacionControlador` | Contratar 1 Controlador |
| `EscenarioContratacionEmbalador` | Contratar 1 Embalador |
| `EscenarioReserva` | Personal de reserva polivalente (2) |
| `EscenarioReorganizacion` | 3 armadores + 2 ajustadores por línea, coberturas entre especialidades |
| `EscenarioSecuencia` | Procesos largos primero |

## Réplicas y análisis de resultados

Cada corrida, al terminar, agrega una fila a `Resultados/resultados_corridas.csv` (indicadores de la corrida completa) y una fila por semana a `Resultados/resultados_semanas.csv`. Como la semilla cambia en cada corrida, **cada corrida es una réplica**.

Para correr muchas réplicas sin animación conviene crear en AnyLogic un experimento de **Variación de parámetros** (*Parameter Variation*): sin parámetros variados (o variando el escenario) y con *Replications* = 10 o más por escenario. También sirve correr varias veces cada experimento de Simulación con la ejecución en tiempo virtual.

Después, el análisis:

```
py -3 scripts/analizar_resultados.py
```

genera `Resultados/informe_resultados.md` (cumplimiento, faltantes, costos con intervalos de confianza del 95 %, ahorro neto frente al escenario actual, utilización, cuellos de botella y respuestas a las preguntas de simulación) y `Resultados/resumen_escenarios.csv`. El informe indica también cuántas réplicas hacen falta para estimar el costo total con ±5 % de precisión (`--precision` para cambiarla).

## Pendiente

- Probar el modelo con Pedestrian Library en AnyLogic y corregir lo que aparezca.
- Correr las réplicas de los 8 escenarios y generar el informe final.
- Reemplazar las 3 OF de ejemplo por OF reales de KRETZ, y la probabilidad de ausencia por la de la planilla de asistencia.

## Estructura de archivos

```
TPI-Simulacion-KRETZ/
├── TPI-Simulacion-KRETZ.alp            # Modelo base (no se modifica)
├── TPI-Simulacion-KRETZ - copia.alp    # Modelo completo generado por el script
├── fondoplanta.jpg                     # Plano de fondo
├── README.md                           # Este documento
├── README-Especificacion_1.md          # Especificación del modelo (Etapa 1)
├── Datos/
│   ├── tiempos_proceso.csv
│   └── dotacion_lineas.csv
├── Resultados/                         # Lo escribe el modelo y el análisis
└── scripts/
    ├── desarrollar_modelo.py           # Genera el .alp
    ├── modelo_java.py                  # Código Java del modelo
    └── analizar_resultados.py          # Informe de comparación de escenarios
```
