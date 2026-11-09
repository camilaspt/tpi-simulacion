# Resultados de la simulación — KRETZ

Informe generado por `scripts/analizar_resultados.py` a partir de las réplicas guardadas por el modelo en `Resultados/resultados_corridas.csv`. Cada réplica es una corrida completa (por defecto, 4 semanas de 5 jornadas más la recuperación de fin de semana) con una semilla distinta. Los intervalos son de confianza del 95 % (t de Student) sobre la media de las réplicas. Las diferencias entre escenarios se calculan por pares de réplicas con la misma semilla (números aleatorios comunes).

## Semillas (números aleatorios comunes)

Todos los escenarios tienen que correr con el mismo listado de semillas: la réplica n usa la misma semilla en todos, así las diferencias entre escenarios no se deben al azar.

| Escenario | Semillas distintas | Mismas que Escenario actual |
|---|---|---|
| Escenario actual | 30 | sí |
| Contratar 2 Ajustadores | 30 | sí |
| Contratar 2 Armadores | 30 | sí |
| Contratar 1 Controlador | 30 | sí |
| Contratar 1 Embalador | 30 | sí |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | sí |
| Personal de reserva polivalente (2) | 30 | sí |
| Secuencia: procesos largos primero | 30 | sí |

## Réplicas por escenario

| Escenario | Réplicas | Semanas por réplica | Réplicas para ±5 % en el costo de horas extra | Réplicas para que el ahorro frente al actual sea significativo |
|---|---|---|---|---|
| Escenario actual | 30 | 4 | 291 | — |
| Contratar 2 Ajustadores | 30 | 4 | 1513 | 30 |
| Contratar 2 Armadores | 30 | 4 | 256 | 30 |
| Contratar 1 Controlador | 30 | 4 | 319 | 30 |
| Contratar 1 Embalador | 30 | 4 | 308 | 30 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | 4 | 1370 | 30 |
| Personal de reserva polivalente (2) | 30 | 4 | 1700 | 30 |
| Secuencia: procesos largos primero | 30 | 4 | 324 | 36 |

El costo total casi no varía entre réplicas (las horas normales son fijas para cada dotación), así que la precisión se mide sobre su parte aleatoria, el costo de las horas extra. La última columna estima cuántas réplicas emparejadas hacen falta para que el intervalo del ahorro neto no incluya el cero: n = (t·s_d / |ahorro|)².

## Cumplimiento de la OF

| Escenario | Cumplimiento a tiempo | Jornadas sin cumplir | Efecto de las ausencias (u. de faltante por jornada) |
|---|---|---|---|
| Escenario actual | 82,3 % ± 3,0 % | 60,0 % ± 5,6 % | 46,8 ± 13,2 (30 réplicas) |
| Contratar 2 Ajustadores | 94,2 % ± 1,5 % | 36,0 % ± 4,1 % | 22,6 ± 8,5 (30 réplicas) |
| Contratar 2 Armadores | 82,4 % ± 2,9 % | 61,5 % ± 4,9 % | 45,3 ± 15,3 (30 réplicas) |
| Contratar 1 Controlador | 83,0 % ± 3,0 % | 54,7 % ± 5,6 % | 43,6 ± 15,2 (30 réplicas) |
| Contratar 1 Embalador | 82,9 % ± 2,9 % | 57,2 % ± 5,7 % | 43,8 ± 14,3 (30 réplicas) |
| Reorganización: 3 armadores + 2 ajustadores por línea | 94,9 % ± 1,3 % | 33,8 % ± 4,3 % | 19,4 ± 6,8 (30 réplicas) |
| Personal de reserva polivalente (2) | 95,0 % ± 1,2 % | 26,7 % ± 4,7 % | 14,8 ± 7,7 (30 réplicas) |
| Secuencia: procesos largos primero | 83,7 % ± 3,0 % | 60,7 % ± 5,8 % | 51,0 ± 13,0 (30 réplicas) |

El efecto de las ausencias compara cada día de la semana consigo mismo (jornadas con ausencias contra jornadas sin ausencias del mismo día), porque el atraso se acumula de lunes a viernes. Un valor positivo indica más faltante cuando falta alguien.

### Faltante acumulado por modelo (unidades por réplica)

| Escenario | AILA 30KG | REPORT LT | NOVEL ECO | LURA | AURA |
|---|---|---|---|---|---|
| Escenario actual | 1,5 | 41,6 | 258,9 | 187,3 | 595,4 |
| Contratar 2 Ajustadores | 0,2 | 11,1 | 67,5 | 66,5 | 207,8 |
| Contratar 2 Armadores | 3,1 | 57,8 | 282,0 | 158,0 | 581,4 |
| Contratar 1 Controlador | 1,5 | 40,4 | 241,4 | 181,7 | 577,7 |
| Contratar 1 Embalador | 1,4 | 38,6 | 250,4 | 177,9 | 583,9 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 0,0 | 7,8 | 54,6 | 59,7 | 193,4 |
| Personal de reserva polivalente (2) | 0,0 | 6,0 | 64,2 | 41,9 | 197,8 |
| Secuencia: procesos largos primero | 54,6 | 11,3 | 353,3 | 378,6 | 201,9 |

## Costos

| Escenario | Horas extra (h-hombre) | Costo horas extra | Costo horas normales | Costo total | Ahorro neto vs. actual |
|---|---|---|---|---|---|
| Escenario actual | 118,5 ± 18,5 | $ 1.540.587 ± 239.900 | $ 42.640.000 | $ 44.180.587 ± 239.900 | — |
| Contratar 2 Ajustadores | 45,5 ± 16,1 | $ 591.165 ± 209.869 | $ 44.720.000 | $ 45.311.165 ± 209.869 | -$ 1.130.578 ± 297.098 (significativo), 30 pares |
| Contratar 2 Armadores | 123,9 ± 18,1 | $ 1.611.111 ± 235.179 | $ 44.720.000 | $ 46.331.111 ± 235.179 | -$ 2.150.524 ± 37.461 (significativo), 30 pares |
| Contratar 1 Controlador | 115,3 ± 18,8 | $ 1.499.250 ± 244.090 | $ 43.680.000 | $ 45.179.250 ± 244.090 | -$ 998.663 ± 99.005 (significativo), 30 pares |
| Contratar 1 Embalador | 117,2 ± 18,8 | $ 1.523.709 ± 243.813 | $ 43.680.000 | $ 45.203.709 ± 243.813 | -$ 1.023.123 ± 18.629 (significativo), 30 pares |
| Reorganización: 3 armadores + 2 ajustadores por línea | 40,3 ± 13,6 | $ 523.614 ± 176.905 | $ 42.640.000 | $ 44.663.614 ± 176.905 | -$ 483.027 ± 271.375 (significativo), 30 pares |
| Personal de reserva polivalente (2) | 35,4 ± 13,3 | $ 459.693 ± 172.985 | $ 44.720.000 | $ 45.179.693 ± 172.985 | -$ 999.107 ± 231.314 (significativo), 30 pares |
| Secuencia: procesos largos primero | 114,1 ± 18,7 | $ 1.483.809 ± 243.591 | $ 42.640.000 | $ 44.123.809 ± 243.591 | $ 56.778 ± 62.077 (no significativo), 30 pares |

El costo total suma las horas normales de toda la dotación (incluidas las contrataciones y el personal de reserva), las horas extra de fin de semana pagadas al doble y el costo de reorganización. El ahorro neto es la media de las diferencias réplica a réplica (escenario actual menos alternativa) y es significativo cuando su intervalo del 95 % no incluye el cero. Son 7 comparaciones contra el escenario actual, cada una al 95 %: para un nivel conjunto del 95 % habría que usar Bonferroni (99,3 % por comparación).

### Horas extra por semana

Las semanas de una misma réplica no son independientes (lo que no se recupera pasa a la semana siguiente): primero se promedian las semanas de cada réplica y el intervalo se calcula entre réplicas.

| Escenario | Réplicas | Horas extra por semana | Costo por semana | Semanas con recuperación |
|---|---|---|---|---|
| Escenario actual | 30 | 29,6 ± 4,6 | $ 385.147 ± 59.975 | 75 de 120 |
| Contratar 2 Ajustadores | 30 | 11,4 ± 4,0 | $ 147.791 ± 52.467 | 40 de 120 |
| Contratar 2 Armadores | 30 | 31,0 ± 4,5 | $ 402.778 ± 58.795 | 79 de 120 |
| Contratar 1 Controlador | 30 | 28,8 ± 4,7 | $ 374.813 ± 61.022 | 71 de 120 |
| Contratar 1 Embalador | 30 | 29,3 ± 4,7 | $ 380.927 ± 60.953 | 74 de 120 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | 10,1 ± 3,4 | $ 130.903 ± 44.226 | 36 de 120 |
| Personal de reserva polivalente (2) | 30 | 8,8 ± 3,3 | $ 114.923 ± 43.246 | 29 de 120 |
| Secuencia: procesos largos primero | 30 | 28,5 ± 4,7 | $ 370.952 ± 60.898 | 78 de 120 |

## Personal, cuellos de botella y traslados

| Escenario | Util. Armador | Util. Ajustador | Util. Controlador | Util. Embalador | Coberturas | Vacantes críticas sin cubrir | Tiempo caminando |
|---|---|---|---|---|---|---|---|
| Escenario actual | 41,0 % | 92,4 % | 76,8 % | 62,2 % | 24,1 | 0,1 | 3,7 % del tiempo ocupado |
| Contratar 2 Ajustadores | 41,8 % | 63,9 % | 78,4 % | 63,4 % | 22,2 | 0,0 | 3,7 % del tiempo ocupado |
| Contratar 2 Armadores | 36,9 % | 92,2 % | 76,7 % | 62,1 % | 14,6 | 0,1 | 3,7 % del tiempo ocupado |
| Contratar 1 Controlador | 41,1 % | 92,6 % | 61,8 % | 62,3 % | 24,0 | 0,1 | 3,7 % del tiempo ocupado |
| Contratar 1 Embalador | 41,0 % | 92,4 % | 76,8 % | 53,6 % | 24,0 | 0,1 | 3,7 % del tiempo ocupado |
| Reorganización: 3 armadores + 2 ajustadores por línea | 56,0 % | 49,1 % | 78,4 % | 63,5 % | 16,1 | 0,0 | 3,7 % del tiempo ocupado |
| Personal de reserva polivalente (2) | 39,4 % | 91,3 % | 75,9 % | 61,8 % | 29,6 | 0,0 | 3,7 % del tiempo ocupado |
| Secuencia: procesos largos primero | 41,2 % | 92,8 % | 77,1 % | 62,3 % | 24,1 | 0,1 | 3,7 % del tiempo ocupado |

| Escenario | Espera armado (media / máx., min) | Espera ajuste (media / máx., min) | Espera control (media / máx., min) | Espera embalaje (media / máx., min) |
|---|---|---|---|---|
| Escenario actual | 25,8 / 180,1 | 165,1 / 675,3 | 13,3 / 358,6 | 9,7 / 736,0 |
| Contratar 2 Ajustadores | 26,4 / 130,5 | 74,0 / 381,1 | 51,4 / 442,6 | 14,7 / 741,7 |
| Contratar 2 Armadores | 23,1 / 194,8 | 180,8 / 797,5 | 13,1 / 379,9 | 9,6 / 745,1 |
| Contratar 1 Controlador | 25,8 / 181,3 | 165,1 / 673,8 | 2,5 / 248,1 | 16,7 / 675,3 |
| Contratar 1 Embalador | 25,8 / 180,1 | 165,1 / 671,3 | 13,3 / 378,5 | 6,2 / 727,4 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 35,0 / 387,4 | 23,8 / 169,2 | 60,8 / 332,6 | 13,4 / 692,2 |
| Personal de reserva polivalente (2) | 25,1 / 111,0 | 139,4 / 477,6 | 8,8 / 302,7 | 6,4 / 692,3 |
| Secuencia: procesos largos primero | 27,6 / 168,8 | 173,7 / 717,4 | 17,5 / 454,4 | 14,5 / 634,5 |

## Respuestas a las preguntas de simulación

1. **Cumplimiento con la dotación actual.** En promedio, no se cumple la OF en el 60,0 % de las jornadas y se entrega a tiempo el 82,3 % de lo pedido. El faltante se concentra en **AURA** (595,4 u. por réplica), el mayor tiempo de espera en cola está en **ajuste** (165,1 min de media) y la especialidad más cargada es **ajustador** (92,4 %).
2. **Horas extra de fin de semana.** Recuperar el faltante requiere 118,5 h-hombre por réplica (29,6 por semana), con un costo de $ 1.540.587 ($ 385.147 por semana) pagadas al doble.
3. **Contratación.** La mejor opción de contratación evaluada es «Contratar 1 Controlador», con un ahorro neto de -$ 998.663 por réplica frente al escenario actual: no conviene frente a seguir pagando horas extra.
4. **Reorganización de áreas.** «Reorganización: 3 armadores + 2 ajustadores por línea» cuesta $ 483.027 por réplica frente al escenario actual, con un cumplimiento medio del 94,9 %.
5. **Personal de reserva.** «Personal de reserva polivalente (2)» cuesta $ 999.107 por réplica frente al escenario actual, con un cumplimiento medio del 95,0 %.
6. **Cambio de secuencia.** «Secuencia: procesos largos primero» ahorra $ 56.778 por réplica frente al escenario actual, con un cumplimiento medio del 83,7 % (la diferencia no es significativa con las réplicas actuales).

**Alternativa de menor costo medio:** «Secuencia: procesos largos primero», con un ahorro neto de $ 56.778 por réplica que **no es significativo** con las réplicas actuales.
