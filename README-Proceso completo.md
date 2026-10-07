# TPI Simulación KRETZ

Trabajo práctico de simulación (AnyLogic) de la línea de producción y el depósito de la fábrica de balanzas **KRETZ**. Este documento resume el problema, los datos relevados y lo que se tiene que completar en el tp.

## Objetivo

Construir un modelo de simulación de eventos discretos + peatonal en AnyLogic que represente:

1. El **armado** de las balanzas a lo largo de sus puestos de trabajo (líneas de Armado y de Control Final).
2. El **depósito**: recepción, almacenamiento y despacho de producto terminado.
3. El **movimiento real de las personas** (operarios) dentro de la planta, no solo los tiempos de proceso — se optó por modelar a los operarios como peatones (Pedestrian Library) desde el arranque, en vez de una animación simplificada.
4. El **funcionamiento** de un dia completo en la empresa, variando los objetivos de fabricacion y sacando conclusiones sobre cuando se llega, cuando no, como conviene organizarse para evitar perdidas. 

## La planta

El plano de fondo (`fondoplanta.jpg`) se armó a partir de una captura satelital (Google Maps/Earth) de la planta real, editada para que los techos de ambas naves queden lisos y de color gris uniforme (sin el detalle de tanques, rejillas, chapas, etc. que tiene la foto original), de forma que sirva como plano de referencia limpio dentro de AnyLogic. Queda pendiente sacar el relieve para que quede un 'plano'.

La planta física consta de dos naves:

| Nave | Dimensión aproximada | Uso |
|---|---|---|
| Planta de producción | 20 m × 25 m | Líneas de Armado y Control Final |
| Depósito | 22 m × 25 m | Almacenamiento y despacho de producto terminado |

**Nota sobre la escala:** la foto satelital es una vista oblicua (no un plano cenital puro), por lo que calcar el contorno fotografiado píxel a píxel introduce distorsión. Se optó por dibujar el piso como rectángulos a escala real (usando el `ScaleRuler` de AnyLogic) ubicados visualmente sobre la foto, en vez de perseguir el contorno exacto de la imagen. En la práctica, el piso quedó armado como un único rectángulo de ~40 m × 25 m, dividido con una pared interna en las dos zonas (producción / depósito).

## Estructura organizativa

- **6 líneas de producción**: 4 de Armado + 2 de Control Final.
- **5 puestos de trabajo por línea**.
- **51 empleados en total**: ~30 asignados a las 6 líneas de producción (5 por línea) y ~20 al depósito.
- Los empleados pueden especializarse en: **Ajustador**, **Controlador**, **Embalador** (los puestos de armado propiamente dicho no requieren una especialización particular). 1 inspector de calidad.
- **Las líneas y los puestos no son exclusivos de un equipo**: ninguna de las 4 líneas de Armado ni las 2 de Control Final está dedicada a un modelo de balanza en particular. Cualquier línea de Armado puede recibir cualquiera de los 5 equipos (y lo mismo para Control Final), así que el modelo tiene que resolver a qué línea/puesto se dirige cada unidad según disponibilidad, no según una asignación fija equipo→línea.

## Productos a simular

La simulación contempla **5 tipos de equipos** (modelos de balanza). Ya están cargados los 5, con el detalle completo de puestos y tiempos. **Todos los equipos, sin excepción, comienzan con el viaje a Depósito (Secuencia 1)** a buscar los materiales al rack único de fabricación; recién después el operario va a su primer puesto de trabajo:

### EQUIPO AILA 30KG (puestos y tiempos, según SAP)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Depósito | Depósito | Viaje a Depósito (retiro de materiales) | Armador | 2 |
| 2 | Armado | Celda 1 | Armado Puesto 1 | Armador | 3,5 |
| 3 | Armado | Celda 1 | Armado Puesto 2 | Armador | 7 |
| 4 | Armado | Celda 1 | Armado Puesto 3 | Armador | 7 |
| 5 | Armado | Celda 1 | Armado Puesto 4 | Armador | 7,5 |
| 6 | Armado | Celda 2 | Ajuste | Ajustador | 5 |
| 7 | Control Final | Control Final | Control Final | Controlador | 4,5 |
| 8 | Control Final | Embalaje | Embalaje | Embalador | 10 |

### BALANZA REPORT LT (modelo completo, versión más económica)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Depósito | Depósito | Viaje a Depósito (retiro de materiales) | Armador | 2 |
| 2 | Armado | Celda 1 | Armado | Armador | 11 |
| 3 | Armado | Celda 3 | Ensamble Final, Calibrado y Cierre de Equipo | Ajustador | 12 |
| 4 | Control Final | Control Final | Control Final y Metrológico | Controlador | 12 |
| 5 | Control Final | Embalaje | Embalaje | Embalador | 12 |


### BALANZA NOVEL ECO (gama media/baja)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Depósito | Depósito | Viaje a Depósito (retiro de materiales) | Armador | 2 |
| 2 | Armado | Celda 1 | Armado | Armador | 3,15 |
| 3 | Armado | Celda 2 | Ajuste | Ajustador | 3 |
| 4 | Control Final | Control Final | Control Final | Controlador | 2,25 |
| 5 | Control Final | Embalaje | Embalaje | Embalador | 3 |

### BALANZA LURA (traída de China)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Depósito | Depósito | Viaje a Depósito (retiro de materiales) | Ajustador | 2 |
| 2 | Armado | Celda 2 | Ajuste | Ajustador | 4 |
| 3 | Control Final | Control Final | Control Final | Controlador | 3,15 |
| 4 | Control Final | Embalaje | Embalaje | Embalador | 3,15 |

**Caso particular — sin Celda 1:** este equipo llega ya armado desde China, así que no pasa por Armado/Celda 1. Por eso el viaje a Depósito (que igual es el primer paso, como en todos los equipos) no lo hace un Armador sino el **Ajustador**, que es quien realiza el primer puesto real de este equipo (Ajuste en Celda 2). El que retira el material en Depósito es siempre el mismo operario que va a hacer el paso siguiente, sea cual sea su especialidad.

### BALANZA AURA (gama media)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Depósito | Depósito | Viaje a Depósito (retiro de materiales) | Armador | 2 |
| 2 | Armado | Celda 1 | Armado | Armador | 3,15 |
| 3 | Armado | Celda 2 | Ajuste | Ajustador | 3 |
| 4 | Control Final | Control Final | Control Final | Controlador | 2,5 |
| 5 | Control Final | Embalaje | Embalaje | Embalador | 2,88 |

**Viaje a Depósito:** el primer paso de **todos** los equipos es que el operario camine hasta el Depósito a buscar los materiales que necesita, y después vaya a su primer puesto de trabajo (Celda 1 en AILA 30KG, REPORT LT, NOVEL ECO y AURA; Celda 2 en LURA). Lo hace siempre el mismo operario que va a realizar ese primer puesto; no hay una dotación de Depósito dedicada a esto. Como ese operario es un `Operario` (peatón), esto además sirve para validar que el movimiento peatonal entre las dos naves funciona bien. Los materiales se retiran de un **rack único de fabricación**: todos los elementos para los 5 equipos están en el mismo rack, no hay racks separados por equipo. El resto de los racks se utilizan para guardar los equipos terminados. Una vez que se terminan pasan a un rack en el cual quedan a la espera de control de calidad para finalmente pasar a stock.

Con esto los 5 equipos ya tienen sus tiempos cargados en `Datos/tiempos_proceso.csv`.

## Proceso

Lo que se simula es **una jornada completa de trabajo**, no una corrida en régimen permanente. La lógica es:

1. **Punto de partida — la orden de fabricación (OF) del día**: cada corrida arranca con una OF concreta (qué equipos hay que producir y en qué cantidad ese día). El modelo tiene que permitir elegir entre varios ejemplos reales de OF, para poder comparar escenarios.
2. **Durante el día**: los operarios van cumpliendo esa OF puesto por puesto, con los tiempos de proceso relevados en `tiempos_proceso.csv`. Esos tiempos son **promedios**, no valores fijos — el objetivo de simular (y no solo calcular con la media) es capturar la variabilidad real de las tareas y cómo esa variabilidad, sumada a las restricciones de dotación y de puestos, afecta el resultado del día.
3. **Al cierre del día**: se compara lo efectivamente producido contra lo pedido por la OF, para determinar si se llegó o no, y por cuánto.

**Control de calidad:** no se controla el 100% de las unidades. Por cada tipo de equipo fabricado ese día se toma una muestra de la producción y se controla el **primer y el último equipo** de esa muestra (no toda la muestra, solo los dos extremos). Esto se repite para cada uno de los tipos de equipo que entraron en la OF del día, no una sola vez para el total de la jornada.

Con ese resultado, el análisis que tiene que responder el TP es:

- ¿Se generan pérdidas por incumplimiento de la cuota diaria? ¿En qué equipos o líneas se concentra el faltante?
- ¿Conviene contratar más empleados? ¿En qué línea o especialidad (Ajustador, Controlador, Embalador) hace más falta?
- ¿Conviene ampliar o agregar puestos en alguna línea?
- ¿Conviene reorganizar el orden/prioridad de fabricación dentro del día (por ejemplo, secuenciar primero los equipos con procesos más largos) para evitar pérdidas?

## Datos (`/Datos`)

- `tiempos_proceso.csv`: una fila por puesto/paso de proceso y equipo (Equipo, Secuencia, Linea_tipo, Celda, Puesto, Tarea, Tiempo_min, Tiempo_seg, Cantidad_operarios). Pensado para importarse directo a AnyLogic (Database → Import) y parametrizar los bloques de proceso.
- `dotacion_lineas.csv`: dotación y especializaciones disponibles por línea.

Los archivos usan `;` como separador y `,` como separador decimal (configuración regional argentina de Excel).

## Modelo en AnyLogic — decisiones de diseño

- **Edición**: AnyLogic Professional/University (habilita Material Handling Library, Warehousing Library y Pedestrian Library).
- **Unidad de tiempo del modelo**: minutos.
- **Agente `ProductoBalanza`**: representa a cada unidad que se arma, con parámetro `modelo` (ej. `"AILA 30KG"`) para poder distinguir tiempos por tipo de equipo más adelante.
- **Flujo de proceso (Process Modeling Library)**: `Source → Queue → Service (x7, uno por puesto del AILA 30KG) → Sink`. El `Source` arranca con una tasa provisoria de 1 unidad cada 10 min (a reemplazar cuando se tenga el dato real de arribo/órdenes de SAP).
- **Recursos = operarios como peatones**: en vez de usar el recurso genérico de Process Modeling Library, se creó un Agent Type `Operario` basado en `Pedestrian` (Pedestrian Library), con un parámetro de especialidad (Ajustador/Controlador/Embalador/Armador). Cada `ResourcePool` usa `Operario` como su tipo de agente, de forma que el operario efectivamente camina desde su posición base hasta el puesto que lo necesita, y vuelve, en vez de aparecer/desaparecer.
- **Un mismo operario que hace varias tareas seguidas (ej. buscar material y después armar)**: no se modela como dos `Service` independientes (eso podría asignar el traslado y el armado a dos operarios distintos). Se usa un único `Seize` del Operario, seguido de un `Delay` por cada ubicación física por la que pasa (ej. Depósito, luego Celda 1), y el `Release` recién al final — así el mismo `Operario` (peatón) camina físicamente entre esas ubicaciones.
- **Espacio peatonal**: piso delimitado con `Wall` (40 m × 25 m, dividido en dos con una pared interna), más `Rectangular Node` por zona para llevar estadísticas de densidad/ocupación y poder abrir/cerrar sectores a futuro.

## Próximos pasos

### Dónde está parado el modelo hoy

Revisando el `.alp` (no solo lo documentado más arriba), esto es lo que ya está construido:

- Piso de `Main` a escala real con `fondoplanta.jpg` de fondo.
- Agent type `Balanza` con parámetro `modelo`, y agent type `Operario` con parámetro `especialidad` (enum Armador/Ajustador/Controlador/Embalador) y un shape 3D (`3d/worker.dae`) para representarlo.
- Un flujo de proceso único: `Source → Queue → Service (ArmadoP1, ArmadoP2, ArmadoP3, ArmadoP4, Ajuste, ControlFinal, Embalaje) → Sink`, con 7 `ResourcePool` (uno por puesto) que instancian `Operario` como tipo de agente.
- Un experimento de Simulación por defecto (sin comparación de escenarios ni Monte Carlo todavía).

Y esto es lo que las decisiones de diseño de la sección anterior todavía **no** tienen reflejo en el modelo:

- `Operario` es un `Agent` genérico: no extiende `Pedestrian`, no hay `Wall` ni `Rectangular Node` en el piso, y la Pedestrian Library no está en uso — los operarios no caminan, son recursos abstractos como en cualquier `ResourcePool` estándar.
- El único flujo armado corresponde a la secuencia de 7 puestos del AILA 30KG. Los otros 4 equipos (REPORT LT, NOVEL ECO, LURA, AURA), con sus propias celdas y secuencias, todavía no están representados ni diferenciados por `modelo`.
- El flujo actual asume una sola línea fija; todavía no hay ruteo entre las 4 líneas de Armado ni las 2 de Control Final. Como ninguna línea es exclusiva de un equipo, falta la lógica que envíe cada unidad a una línea/puesto disponible (de cualquiera de las líneas del tipo que corresponda) en vez de a un camino único.
- No existe el paso "Viaje a Depósito" ni el patrón Seize único + Delays encadenados: cada `Service` es un bloque independiente, así que hoy el modelo podría asignar el traslado y el armado a operarios distintos.
- Los 7 `ResourcePool` quedaron con la configuración por defecto de la librería (sin `capacity` ni dotación cargada) — todavía no toman los números de `dotacion_lineas.csv`.
- `tiempos_proceso.csv` y `dotacion_lineas.csv` no están importados a la Database de AnyLogic; nada en el modelo lee esos CSV todavía.
- La tasa de arribo del `Source` sigue siendo una constante provisoria (no hay ninguna OF real cargada ni forma de elegir entre OFs de ejemplo).
- El depósito (racks, picking, despacho) no existe en el modelo.
- El bloque `ControlFinal` hoy procesa el 100% de las unidades: todavía no implementa la regla real de muestreo (tomar el primer y el último equipo de una muestra, por cada tipo de equipo fabricado ese día).

Lo construido hasta ahora es un esqueleto de proceso de una sola línea con recursos genéricos: el 90% del análisis pedido (cumplimiento de OF, pérdidas, dotación, reorganización) todavía depende de pasos que faltan.

### Para terminar el TP, en orden sugerido

1. Importar `tiempos_proceso.csv` y `dotacion_lineas.csv` a la Database de AnyLogic y parametrizar `Service`/`ResourcePool` desde esas tablas (tiempos, cantidad de operarios, especialidad requerida) en vez de valores fijos por puesto.
2. Extender el flujo de `Main` para cubrir los 5 equipos según `modelo` (usando la tabla importada), incluyendo el caso particular de LURA (sin Celda 1, primer traslado a cargo del Ajustador) y confirmando si Celda 3 (REPORT LT) es física o un alias de Celda 1/2. Esto incluye modelar las 4 líneas de Armado y las 2 de Control Final como líneas equivalentes (no dedicadas a un equipo) y agregar la lógica de ruteo que asigna cada unidad a una línea/puesto disponible.
3. Implementar el paso "Viaje a Depósito" con el patrón Seize único + Delays encadenados ya decidido, para los 5 equipos.
4. Implementar en `ControlFinal` la regla de muestreo real (por cada tipo de equipo fabricado en el día, tomar una muestra de la producción y controlar solo el primer y el último equipo de esa muestra), en vez del control al 100% que hay hoy.
5. Convertir `Operario` en un `Pedestrian` real: sumar la Pedestrian Library, agregar `Wall`/`Rectangular Node` sobre el piso ya escalado con `fondoplanta.jpg`, y ligar el shape 3D `worker.dae` a la animación peatonal (hoy ese asset está cargado pero no conectado a movimiento real).
6. Modelar el depósito: decidir si el flujo de gente se resuelve con recursos (como en la línea) o con bloques propios de Pedestrian Library, y ubicar el rack único de fabricación con Warehousing/Material Handling Library.
7. Reemplazar la tasa de arribo constante del `Source` por la carga de una OF real del día, con al menos 2–3 ejemplos de OF para poder compararlos en distintas corridas.
8. Agregar la lógica de cierre de día: comparar producción real vs. OF pedida, y exponer esa brecha (y sus causas — dotación, puestos, secuencia) en datasets/estadísticas.
9. Crear experimentos adicionales (comparación de escenarios / Monte Carlo) para correr distintas OF y distintas dotaciones, en vez de depender del único experimento de Simulación por defecto — es la forma de responder con evidencia las preguntas de la sección Proceso (contratar más gente, ampliar líneas, reorganizar OFs).

## Estructura de archivos

```
TPI-Simulacion-KRETZ/
├── TPI-Simulacion-KRETZ.alp     # Modelo de AnyLogic
├── fondoplanta.jpg              # Plano de fondo (techos aplanados a gris)
├── README.md                    # Este documento
└── Datos/
    ├── tiempos_proceso.csv
    └── dotacion_lineas.csv
```
