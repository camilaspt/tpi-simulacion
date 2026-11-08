# FINAL — Pendientes para cerrar el TP

Estado al 01/11/2026, rama `feature/pedestrian-library`.

## Entrega final (lo que hay que presentar)

| # | Entregable | Estado | Qué falta |
|---|---|---|---|
| 1 | **ALP de AnyLogic** | Generado: `TPI-Simulacion-KRETZ - copia.alp` | Probarlo en AnyLogic y corregir errores. Al entregar, renombrarlo (por ejemplo, `TPI-Simulacion-KRETZ-GRUPO07.alp`) y comprobar que abre y corre. |
| 2 | **Informe en PDF tipo paper** | No empezado | Secciones indispensables: **abstract, objetivos, metodología, resultados y conclusiones**. Los diez pasos de la simulación deben quedar **implícitos** en el texto, sin enumerarlos. Se arma en Overleaf, como la Etapa 1. |
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

El modelo (`TPI-Simulacion-KRETZ - copia.alp`, generado con `scripts/desarrollar_modelo.py`) cubre la especificación:

- Los 5 equipos con sus recetas, el viaje a Depósito (rack único) y el ruteo entre líneas equivalentes.
- Ausentismo y coberturas, muestreo de calidad (primer y último equipo por modelo).
- Cierre de jornada, recuperación de fin de semana con horas extra al doble y costos.
- Operarios que caminan por el plano a escala (línea recta y puerta entre naves). La Pedestrian Library se descartó: en la edición Personal Learning solo permite simular 5 horas.
- 8 escenarios, réplicas con semilla registrada, exportación de resultados a `Resultados/*.csv` e informe automático (`scripts/analizar_resultados.py`).

## Lo que falta, en orden

1. **Probar el modelo en AnyLogic y corregir errores.** El código compila, pero todavía no se ejecutó completo. Para probarlo:
   - cerrar el modelo y borrar `TPI-Simulacion-KRETZ - copia.alp.autosave`;
   - abrir `TPI-Simulacion-KRETZ - copia.alp` y correr `Simulation`;
   - anotar los errores de la consola o de la pantalla.

   Qué puede aparecer:
   - lentitud: si tarda demasiado, bajar `semanasSimuladas`.
2. **Crear el experimento de réplicas (Variación de parámetros) a mano en AnyLogic**, con *Replications* en 10 o más, y guardar el modelo. Después se usa como plantilla en el script para generarlo en los 8 escenarios.
3. **Cargar datos reales:**
   - OF reales de KRETZ, en lugar de las 3 de ejemplo (función `ofEjemplo` en `scripts/modelo_java.py`);
   - probabilidad de ausencia según la planilla de asistencia, en lugar del 6 % supuesto (parámetro `probAusencia`).

   Si no se consiguen, dejarlos declarados como supuestos en el informe.
4. **Correr las réplicas de los 8 escenarios** y generar el informe con `py -3 scripts/analizar_resultados.py`. El informe dice si alcanzan las réplicas para ±5 % de precisión en el costo total.
5. **Escribir el informe final de la Etapa 2** en Overleaf, siguiendo el formato de la Etapa 1:
   - descripción del modelo construido;
   - verificación y validación (por ejemplo, comparar la producción del escenario actual con la real);
   - resultados con intervalos de confianza (de `Resultados/informe_resultados.md`);
   - conclusiones respondiendo las preguntas de la sección 16 de la especificación.
6. **Unir la rama `feature/pedestrian-library` a `main`** cuando el modelo funcione.

## Detalles menores (opcionales)

- `Datos/dotacion_lineas.csv` no se lee desde el modelo: la dotación sale de los parámetros (`armadoresPorLinea`, `ajustadoresPorLinea`, etc.).
- El «faltante por línea» de la sección 14 se informa como unidades procesadas por línea. Como las líneas no están dedicadas a un equipo, el faltante no se puede asignar a una línea.
- Ordenar el repositorio: hay dos versiones de la especificación (`README-Especificacion.md` y `README-Especificacion_1.md`) y queda un `debug.log` en la raíz.
