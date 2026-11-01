# FINAL — Pendientes para cerrar el TP

Estado al 01/11/2026, rama `feature/pedestrian-library`.

## Lo que ya está desarrollado

El modelo (`TPI-Simulacion-KRETZ - copia.alp`, generado con `scripts/desarrollar_modelo.py`) cubre la especificación:

- Los 5 equipos con sus recetas, el viaje a Depósito (rack único) y el ruteo entre líneas equivalentes.
- Ausentismo y coberturas, muestreo de calidad (primer y último equipo por modelo).
- Cierre de jornada, recuperación de fin de semana con horas extra al doble y costos.
- Operarios como peatones (Pedestrian Library).
- 8 escenarios, réplicas con semilla registrada, exportación de resultados a `Resultados/*.csv` e informe automático (`scripts/analizar_resultados.py`).

## Lo que falta, en orden

1. **Probar el modelo en AnyLogic y corregir errores.** El código compila, pero todavía no se ejecutó. La parte peatonal es la más riesgosa. Para probarlo:
   - cerrar el modelo y borrar `TPI-Simulacion-KRETZ - copia.alp.autosave`;
   - abrir `TPI-Simulacion-KRETZ - copia.alp` y correr `Simulation`;
   - anotar los errores de la consola o de la pantalla.

   Qué puede aparecer:
   - un error al arrancar en `entrarPlanta`: un operario del pool no puede entrar al circuito peatonal;
   - peatones trabados cerca de un puesto o del rack: hay que separar más los lugares fijos;
   - el aviso «la unidad … no estaba esperando a su operario»;
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
