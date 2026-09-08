# TPI Simulación KRETZ

Trabajo práctico de simulación (AnyLogic) de la línea de producción y el depósito de la fábrica de balanzas **KRETZ**. Este documento resume el problema, los datos relevados y las decisiones de modelado tomadas hasta ahora.

## Objetivo

Construir un modelo de simulación de eventos discretos + peatonal en AnyLogic que represente:

1. El **armado** de las balanzas a lo largo de sus puestos de trabajo (líneas de Armado y de Control Final).
2. El **depósito**: recepción, almacenamiento y despacho de producto terminado.
3. El **movimiento real de las personas** (operarios) dentro de la planta, no solo los tiempos de proceso — se optó por modelar a los operarios como peatones (Pedestrian Library) desde el arranque, en vez de una animación simplificada.


## La planta

El plano de fondo (`fondoplanta.jpg`) se armó a partir de una captura satelital (Google Maps/Earth) de la planta real, editada para que los techos de ambas naves queden lisos y de color gris uniforme (sin el detalle de tanques, rejillas, chapas, etc. que tiene la foto original), de forma que sirva como plano de referencia limpio dentro de AnyLogic.

La planta física consta de dos naves:

| Nave | Dimensión aproximada | Uso |
|---|---|---|
| Planta de producción | 20 m × 25 m | Líneas de Armado y Control Final |
| Depósito | 22 m × 25 m | Almacenamiento y despacho de producto terminado |

**Nota sobre la escala:** la foto satelital es una vista oblicua (no un plano cenital puro), por lo que calcar el contorno fotografiado píxel a píxel introduce distorsión. Se optó por dibujar el piso como rectángulos a escala real (usando el `ScaleRuler` de AnyLogic) ubicados visualmente sobre la foto, en vez de perseguir el contorno exacto de la imagen. En la práctica, el piso quedó armado como un único rectángulo de ~40 m × 25 m, dividido con una pared interna en las dos zonas (producción / depósito).

## Estructura organizativa

- **6 líneas de producción**: 3 de Armado + 2 de Control Final (la composición exacta de la 6ª línea está pendiente de confirmar con el dato real de SAP).
- **5 puestos de trabajo por línea**.
- **50 empleados en total**: ~30 asignados a las 6 líneas de producción (5 por línea) y ~20 al depósito.
- Los empleados pueden especializarse en: **Ajustador**, **Controlador**, **Embalador** (los puestos de armado propiamente dicho no requieren una especialización particular).

## Productos a simular

La simulación contempla **5 tipos de equipos** (modelos de balanza). Por ahora se cargó el detalle completo de dos, para validar el modelo antes de escalar:

### EQUIPO AILA 30KG (puestos y tiempos, según SAP)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Armado | Celda 1 | Armado Puesto 1 | Armador | 3,5 |
| 2 | Armado | Celda 1 | Armado Puesto 2 | Armador | 7 |
| 3 | Armado | Celda 1 | Armado Puesto 3 | Armador | 7 |
| 4 | Armado | Celda 1 | Armado Puesto 4 | Armador | 7,5 |
| 5 | Armado | Celda 2 | Ajuste | Ajustador | 5 |
| 6 | Control Final | Control Final | Control Final | Controlador | 4,5 |
| 7 | Control Final | Embalaje | Embalaje | Embalador | 10 |

### BALANZA REPORT LT (modelo completo, versión más económica)

| Secuencia | Línea | Celda | Puesto | Tarea | Tiempo (min) |
|---|---|---|---|---|---|
| 1 | Armado | Depósito | Salida Depósito (retiro de materiales) | Armador | 2 |
| 2 | Armado | Celda 1 | Armado | Armador | 11 |
| 3 | Armado | Celda 3 | Ensamble Final, Calibrado y Cierre de Equipo | Ajustador | 12 |
| 4 | Control Final | Control Final | Control Final y Metrológico | Controlador | 12 |
| 5 | Control Final | Embalaje | Embalaje | Embalador | 12 |

**Caso particular — viaje a Depósito:** el primer paso de este equipo no es un puesto/recurso propio: es el mismo Armador que va a hacer el Puesto 2 (Celda 1) el que primero camina hasta el Depósito a buscar los materiales que necesita para armar, y después va a Celda 1. No hay una dotación de Depósito dedicada a esto — por eso, en el modelo, no se representa con un `Service` independiente sino con un único `Seize` del Armador seguido de dos `Delay` encadenados (uno en Depósito, uno en Celda 1) y recién ahí el `Release`. Como el Armador es un `Operario` (peatón), esto además sirve para validar que el movimiento peatonal entre las dos naves funciona bien.

Los otros 3 equipos quedan pendientes de cargar con el mismo formato.

## Datos (`/Datos`)

- `tiempos_proceso.csv`: una fila por puesto/paso de proceso y equipo (Equipo, Secuencia, Linea_tipo, Celda, Puesto, Tarea, Tiempo_min, Tiempo_seg, Cantidad_operarios). Pensado para importarse directo a AnyLogic (Database → Import) y parametrizar los bloques de proceso.
- `dotacion_lineas.csv`: dotación y especializaciones disponibles por línea.

Los archivos usan `;` como separador y `,` como separador decimal (configuración regional argentina de Excel).

## Modelo en AnyLogic — decisiones de diseño

- **Edición**: AnyLogic Professional/University
- **Unidad de tiempo del modelo**: minutos.
- **Agente `ProductoBalanza`**: representa a cada unidad que se arma, con parámetro `modelo` (ej. `"AILA 30KG"`) para poder distinguir tiempos por tipo de equipo más adelante.
- **Flujo de proceso (Process Modeling Library)**: `Source → Queue → Service (x7, uno por puesto del AILA 30KG) → Sink`. El `Source` arranca con una tasa provisoria de 1 unidad cada 10 min (a reemplazar cuando se tenga el dato real de arribo/órdenes de SAP).
- **Recursos = operarios como peatones**: en vez de usar el recurso genérico de Process Modeling Library, se creó un Agent Type `Operario` basado en `Pedestrian` (Pedestrian Library), con un parámetro de especialidad (Ajustador/Controlador/Embalador/Armador). Cada `ResourcePool` usa `Operario` como su tipo de agente, de forma que el operario efectivamente camina desde su posición base hasta el puesto que lo necesita, y vuelve, en vez de aparecer/desaparecer.
- **Un mismo operario que hace varias tareas seguidas (ej. buscar material y después armar)**: no se modela como dos `Service` independientes (eso podría asignar el traslado y el armado a dos operarios distintos). Se usa un único `Seize` del Operario, seguido de un `Delay` por cada ubicación física por la que pasa (ej. Depósito, luego Celda 1), y el `Release` recién al final — así el mismo `Operario` (peatón) camina físicamente entre esas ubicaciones.
- **Espacio peatonal**: piso delimitado con `Wall` (40 m × 25 m, dividido en dos con una pared interna), más `Rectangular Node` por zona para llevar estadísticas de densidad/ocupación y poder abrir/cerrar sectores a futuro.

## Estado actual

- Línea de AILA 30KG funcionando de punta a punta con tiempos fijos y recursos dedicados por puesto (verificado: los puestos con mayor tiempo de servicio muestran mayor ocupación, como se espera).
- En transición de un movimiento de recursos simplificado a Pedestrian Library completo: paredes del piso ya definidas, Agent Type `Operario` (peatón) creado, pendiente terminar de conectarlo a cada `ResourcePool` y de filtrar la asignación de operarios por especialidad en cada `Service`.

## Próximos pasos

- Cerrar la asignación de operarios por especialidad en cada puesto.
- Definir cómo se modela el depósito (Warehousing/Material Handling Library: racks, picking, despacho) y si el flujo de gente ahí se resuelve con recursos (como en la línea) o con un flujo de Pedestrian Library propio (`PedService` por líneas o por área — pendiente de decidir según el proceso real de depósito).
- Cargar tiempos de proceso de los 4 equipos restantes en `tiempos_proceso.csv`.
- Reemplazar la tasa de arribo provisoria (10 min) por el dato real de órdenes/producción de SAP.
- Confirmar la composición exacta de las 6 líneas (armado/control final) y la dotación del depósito.

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
