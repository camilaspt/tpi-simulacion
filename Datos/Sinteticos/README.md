# Datos históricos SINTÉTICOS de KRETZ

> **Estos datos no son reales.** Los generó `scripts/generar_datos_sinteticos.py` para tener una referencia con la cual comparar el modelo mientras no lleguen los registros reales de KRETZ. Si se usan en el informe, hay que declararlos como **datos sintéticos / supuestos**, nunca como datos relevados de la planta.

Período: 26 semanas, del 2 de marzo al 28 de agosto de 2026, con 10 feriados aproximados (120 jornadas hábiles). Semilla fija (2026): correr el script de nuevo da exactamente los mismos archivos.

```
py -3 scripts/generar_datos_sinteticos.py
```

Formato: separador `;`, decimales con coma, UTF-8 con BOM (se abren directo en Excel con configuración argentina), igual que el resto de `Datos/`.

## Archivos

| Archivo | Una fila por | Contenido |
|---|---|---|
| `empleados.csv` | empleado (41) | Legajo, especialidad, línea y puesto habitual. 4 líneas de Armado (4 armadores + 1 ajustador), 2 de Control Final (2 controladores + 3 embaladores), 10 de depósito y 1 inspector (igual que el modelo). |
| `planilla_ausencias.csv` | ausencia (empleado y día) | Legajo, especialidad, línea, fecha, día de la semana y motivo (enfermedad, razones particulares, trámite, licencia por examen, sin aviso). Las enfermedades pueden durar varios días seguidos. |
| `resumen_ausentismo.csv` | especialidad | Porcentaje de ausencia por día de la semana y total. Es lo que se carga en el parámetro `probAusencia` del modelo. |
| `ordenes_fabricacion.csv` | OF y modelo | Cantidad pedida, producida en el turno, faltante, % de cumplimiento y si se cumplió. |
| `cumplimiento_diario.csv` | jornada | Totales de la OF, % de cumplimiento, ausentes (planta y líneas), ajustadores y controladores presentes, especialidad que limitó la jornada y eventos fuera del modelo (cortes de luz, demoras de materiales, etc.). |
| `horas_extra_fin_de_semana.csv` | semana | Faltante a recuperar, personas que asistieron el sábado, horas de la jornada, horas-hombre y costo (horas-hombre × $ 6.500 × 2). |

## Resultados del período

- 120 jornadas, de las que **78 (65 %) no cumplieron la OF**.
- Cumplimiento medio en el turno: **83,4 %**.
- Ausentismo de las líneas: alrededor del 6 %, más alto los lunes.
- **17 de 26 semanas** (65 %) necesitaron recuperación de fin de semana; **32,1 h-hombre por semana** en promedio ($ 417.250 por semana).
- El cuello de botella es **Ajuste** en 69 de las 78 jornadas que no cumplieron.

Calibración (noviembre de 2026): las OF se agrandaron un 15 %, igual que la OF de ejemplo del modelo (307 unidades por día), porque en la planta hay que recuperar el sábado en la mayoría de las semanas. La eficiencia del turno (93 % ± 2 %), la variación diaria de los tiempos (± 10 %), el rendimiento de la jornada del sábado (95 %, como el modelo) y el arrastre de las unidades atrasadas al día siguiente se ajustaron para que el historial quede dentro de los intervalos del 95 % del escenario actual del modelo (hoja *Validacion* de `Resultados/Resultados_KRETZ.xlsx`).

## Cómo se generaron

Para cada jornada:

1. **Asistencia.** Cada empleado tiene su propia propensión a faltar (media del 6 %), multiplicada por el factor de cada día de la semana que usa el modelo (lunes 1,25; martes 1,0; miércoles y jueves 0,9; viernes 1,1).
2. **OF del día.** Se elige una de tres mezclas típicas, agrandadas un 15 % (equilibrada, con mucha REPORT LT o con muchos equipos cortos), con ±10 % de variación por modelo. A veces algún modelo no entra en la OF.
3. **Capacidad.** Para cada especialidad se comparan los minutos disponibles de los presentes (480 min × eficiencia del 93 % ± 2 %) con los minutos que piden la OF del día y las unidades atrasadas del día anterior, según los tiempos de SAP (±10 % de variación diaria). La especialidad con menos holgura limita la producción. No hay coberturas entre especialidades (igual que el escenario actual del modelo). En el 4 % de los días hay un evento que baja la eficiencia.
4. **Faltante.** Primero se terminan las unidades atrasadas; los minutos que no se llegan a cubrir se reparten entre los modelos de la OF del día según su carga en la especialidad que limitó la jornada, y quedan pendientes para el día siguiente (columna `Atrasadas_dia_anterior`).
5. **Fin de semana.** Lo que sigue pendiente al cierre del viernes se recupera el sábado con una cuadrilla proporcional al faltante (entre 3 y 12 personas, el 10 % falta). La jornada dura lo necesario a un 95 % de rendimiento, con un mínimo de 4 h.

## Cuidado al usarlos para validar

Los datos salen de un modelo de capacidad más simple que el modelo de AnyLogic, pero usan los **mismos supuestos**: tiempos de SAP, 6 % de ausentismo y valor de la hora. Si el modelo «se parece» a estos datos, eso **muestra que es coherente con esos supuestos, no que valide contra la planta real**. La validación real necesita los registros de KRETZ. Hay que reemplazar los archivos manteniendo las mismas columnas.
