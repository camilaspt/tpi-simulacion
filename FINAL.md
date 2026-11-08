# FINAL — Pendientes para cerrar el TP

Estado al 08/11/2026, rama `feature/pedestrian-library`.

## Entrega final (lo que hay que presentar)

| # | Entregable | Estado | Qué falta |
|---|---|---|---|
| 1 | **ALP de AnyLogic** | Corre en AnyLogic: `TPI-Simulacion-KRETZ - copia.alp` | Correr una simulación completa (4 semanas) sin errores. Al entregar, renombrarlo (por ejemplo, `TPI-Simulacion-KRETZ-GRUPO07.alp`) junto con la carpeta `3d/` y comprobar que abre y corre. |
| 2 | **Informe en PDF tipo paper** | Borrador en `INFORME-FINAL.md` (faltan resultados y autores) | Secciones indispensables: **abstract, objetivos, metodología, resultados y conclusiones**. Los diez pasos de la simulación deben quedar **implícitos** en el texto, sin enumerarlos. Se arma en Overleaf, como la Etapa 1. |
| 3 | **Planilla de cálculo con los resultados de las corridas** | Se arma con los CSV del modelo | Correr las réplicas y pasar `Resultados/resultados_corridas.csv`, `resultados_semanas.csv` y `resumen_escenarios.csv` a una planilla Excel (una hoja por archivo y una de resumen). |
| 4 | **Link de AnyLogic Cloud del TPI** | No empezado | Subir el modelo a AnyLogic Cloud. Poner **nombres y correos electrónicos de los autores** y, si hace falta, instrucciones de uso. |
| 5 | **Video breve (link de YouTube)** | No empezado | Explicar el problema, la solución y mostrar el uso del modelo. |

### Los diez pasos de la simulación (deben quedar implícitos en el informe)

Sirve como guía para controlar que el informe los cubra sin nombrarlos como pasos:

1. Formulación del problema → introducción y objetivos (OF que no se cumple, costo de las horas extra de fin de semana).
2. Objetivos y plan del estudio → objetivos y escenarios a comparar.
3. Modelo conceptual → metodología: sistema, entidades, recursos, supuestos y diagrama conceptual.
4. Recolección de datos → metodología: tiempos de SAP, dotación, OF y ausentismo.
5. Construcción del modelo → metodología: AnyLogic y Process Modeling Library (explicar por qué no se usó la Pedestrian Library: la edición Personal Learning limita a 5 horas).
6. Verificación → metodología: el modelo hace lo que dice la especificación.
7. Validación → metodología o resultados: el escenario actual se parece a la realidad de la planta.
8. Diseño de experimentos → metodología: escenarios, réplicas, semillas y horizonte simulado.
9. Corridas y análisis → resultados: intervalos de confianza y ahorro neto.
10. Documentación e implementación → conclusiones y recomendaciones para KRETZ.

### Antes de la entrega del Cloud y del video

- La subida a AnyLogic Cloud desde la edición Personal Learning puede tener límites (tamaño del modelo, librerías). Probar la subida con tiempo.
- En Cloud probablemente no se pueda acceder a los CSV que escribe el modelo: los resultados para la planilla conviene sacarlos de las corridas locales.
- Grabar el video con el modelo ya corregido. Sirve mostrar la vista 3D y el tablero de indicadores.

## Lo que ya está desarrollado

El modelo (`TPI-Simulacion-KRETZ - copia.alp`) corre en AnyLogic y cubre la especificación:

- Los 5 equipos con sus recetas, el viaje a Depósito y el ruteo entre líneas equivalentes.
- Ausentismo y coberturas, muestreo de calidad (primer y último equipo por modelo).
- Cierre de jornada, recuperación de fin de semana con horas extra al doble y costos (41 empleados: 30 de línea, 10 de depósito y 1 inspector).
- Plano 3D: mesas (*Table*), cajas de producto (*box_1_closed*) y tres racks *Storage* con la Material Handling Library (materiales, espera de calidad y stock).
- Despacho: camión (`CamionRetiro`) a las 3 h y 6 h de cada jornada, cargado por 3 empleados de depósito.
- Operarios que caminan por el plano a escala. La Pedestrian Library se descartó: en la edición Personal Learning solo permite simular 5 horas.
- 8 escenarios, réplicas con semilla registrada, exportación de resultados a `Resultados/*.csv` e informe automático (`scripts/analizar_resultados.py`).
- Los cambios al modelo se aplican con `scripts/editar_alp.py` (conserva lo editado en AnyLogic); hay que cerrar el modelo antes.

## Lo que falta, en orden

1. **Correr una simulación completa (4 semanas)** y confirmar que termina, que crea `Resultados/resultados_corridas.csv` y que no quedan cajas al pie de los racks de calidad o stock (AnyLogic informa 200 celdas en cada uno; si se llenan, agrandarlos).
2. **Experimento de réplicas:** crear a mano en AnyLogic una *Variación de parámetros* (por ejemplo, `semilla` de 1 a 30) y guardar el modelo; después se replica para los 8 escenarios con el script. Con las mismas semillas en todos los escenarios, la comparación es más precisa.
3. **Datos reales o supuestos declarados:** OF reales de KRETZ (hoy 3 de ejemplo en `ofEjemplo`) y probabilidad de ausencia de la planilla de asistencia (hoy 6 %, `probAusencia`).
4. **Correr las réplicas** de los 8 escenarios (sin animación) y generar `Resultados/informe_resultados.md` con `py -3 scripts/analizar_resultados.py`.
5. **Planilla de cálculo** (entregable 3): armarla desde los CSV de resultados.
6. **Informe PDF** (entregable 2): completar `INFORME-FINAL.md` con los resultados y los autores, y pasarlo a Overleaf.
7. **AnyLogic Cloud** (entregable 4): subir el modelo, con nombres y correos de los autores e instrucciones de uso.
8. **Video** (entregable 5): grabarlo con el modelo final.
9. **Cierre del repositorio:** unir `feature/pedestrian-library` a `main`.

## Detalles menores (opcionales)

- `Datos/dotacion_lineas.csv` no se lee desde el modelo: la dotación sale de los parámetros (`armadoresPorLinea`, `ajustadoresPorLinea`, etc.).
- El «faltante por línea» de la sección 14 se informa como unidades procesadas por línea. Como las líneas no están dedicadas a un equipo, el faltante no se puede asignar a una línea.
- Ordenar el repositorio: hay dos versiones de la especificación (`README-Especificacion.md` y `README-Especificacion_1.md`), un `debug.log` en la raíz y `scripts/desarrollar_modelo.py`, que ya no se usa para generar el modelo (solo para el arnés de compilación y las definiciones del flujo).
- La especificación de la Etapa 1 todavía dice 51 empleados (≈ 20 de depósito).
