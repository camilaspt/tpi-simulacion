# Resultados de la simulación — KRETZ

Informe generado por `scripts/analizar_resultados.py` a partir de las réplicas guardadas por el modelo en `Resultados/resultados_corridas.csv`. Cada réplica es una corrida completa (por defecto, 4 semanas de 5 jornadas más la recuperación de fin de semana) con una semilla distinta. Los intervalos son de confianza del 95 % (t de Student) sobre la media de las réplicas. Las diferencias entre escenarios se calculan por pares de réplicas con la misma semilla (números aleatorios comunes).

## Semillas (números aleatorios comunes)

Todos los escenarios tienen que correr con el mismo listado de semillas: la réplica n usa la misma semilla en todos, así las diferencias entre escenarios no se deben al azar.

| Escenario | Semillas distintas | Mismas que Escenario actual |
|---|---|---|
| Escenario actual | 30 | sí |
| Contratar 1 Embalador | 30 | sí |
| Secuencia: procesos largos primero | 30 | sí |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | sí |
| Personal de reserva polivalente (2) | 30 | sí |
| Contratar 2 Ajustadores | 30 | sí |
| Contratar 1 Controlador | 30 | sí |
| Contratar 2 Armadores | 30 | sí |

## Réplicas por escenario

| Escenario | Réplicas | Semanas por réplica | Réplicas para ±5 % en el costo de horas extra | Réplicas para que el ahorro frente al actual sea significativo |
|---|---|---|---|---|
| Escenario actual | 30 | 4 | 652 | — |
| Contratar 1 Embalador | 30 | 4 | 647 | 30 |
| Secuencia: procesos largos primero | 30 | 4 | 626 | 30 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | 4 | 11456 | 30 |
| Personal de reserva polivalente (2) | 30 | 4 | 6604 | 30 |
| Contratar 2 Ajustadores | 30 | 4 | 11528 | 30 |
| Contratar 1 Controlador | 30 | 4 | 575 | 30 |
| Contratar 2 Armadores | 30 | 4 | 648 | 30 |

El costo total casi no varía entre réplicas (las horas normales son fijas para cada dotación), así que la precisión se mide sobre su parte aleatoria, el costo de las horas extra. La última columna estima cuántas réplicas emparejadas hacen falta para que el intervalo del ahorro neto no incluya el cero: n = (t·s_d / |ahorro|)².

## Cumplimiento de la OF

| Escenario | Cumplimiento a tiempo | Jornadas sin cumplir | Efecto de las ausencias (u. de faltante por jornada) |
|---|---|---|---|
| Escenario actual | 93,1 % ± 1,4 % | 25,7 % ± 3,8 % | 24,2 ± 5,7 (30 réplicas) |
| Contratar 1 Embalador | 93,5 % ± 1,3 % | 24,5 % ± 3,7 % | 23,1 ± 6,4 (30 réplicas) |
| Secuencia: procesos largos primero | 93,4 % ± 1,4 % | 25,5 % ± 3,7 % | 23,2 ± 5,9 (30 réplicas) |
| Reorganización: 3 armadores + 2 ajustadores por línea | 97,9 % ± 0,8 % | 7,5 % ± 2,6 % | 7,0 ± 4,0 (30 réplicas) |
| Personal de reserva polivalente (2) | 98,0 % ± 0,6 % | 7,3 % ± 1,9 % | 5,9 ± 3,6 (30 réplicas) |
| Contratar 2 Ajustadores | 97,5 % ± 0,9 % | 8,0 % ± 2,8 % | 8,4 ± 4,8 (30 réplicas) |
| Contratar 1 Controlador | 93,5 % ± 1,4 % | 30,5 % ± 3,9 % | 24,1 ± 6,7 (30 réplicas) |
| Contratar 2 Armadores | 92,4 % ± 1,4 % | 27,7 % ± 4,4 % | 25,3 ± 6,7 (30 réplicas) |

El efecto de las ausencias compara cada día de la semana consigo mismo (jornadas con ausencias contra jornadas sin ausencias del mismo día), porque el atraso se acumula de lunes a viernes. Un valor positivo indica más faltante cuando falta alguien.

### Faltante acumulado por modelo (unidades por réplica)

| Escenario | AILA 30KG | REPORT LT | NOVEL ECO | LURA | AURA |
|---|---|---|---|---|---|
| Escenario actual | 0,0 | 10,4 | 99,2 | 49,9 | 209,3 |
| Contratar 1 Embalador | 0,0 | 8,8 | 92,5 | 45,0 | 200,1 |
| Secuencia: procesos largos primero | 12,2 | 2,2 | 184,2 | 86,2 | 67,7 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 0,0 | 3,5 | 21,5 | 27,9 | 59,8 |
| Personal de reserva polivalente (2) | 0,0 | 2,0 | 25,8 | 18,8 | 58,7 |
| Contratar 2 Ajustadores | 0,0 | 5,6 | 28,4 | 32,0 | 68,0 |
| Contratar 1 Controlador | 0,0 | 8,5 | 89,3 | 44,2 | 205,8 |
| Contratar 2 Armadores | 0,0 | 15,3 | 135,3 | 47,4 | 208,7 |

## Costos

| Escenario | Horas extra (h-hombre) | Costo horas extra | Costo horas normales | Costo total | Ahorro neto vs. actual |
|---|---|---|---|---|---|
| Escenario actual | 58,5 ± 13,6 | $ 760.299 ± 177.185 | $ 42.640.000 | $ 43.400.299 ± 177.185 | — |
| Contratar 1 Embalador | 58,8 ± 13,6 | $ 763.915 ± 177.378 | $ 43.680.000 | $ 44.443.915 ± 177.378 | -$ 1.043.616 ± 7.115 (significativo), 30 pares |
| Secuencia: procesos largos primero | 55,9 ± 12,8 | $ 726.735 ± 165.986 | $ 42.640.000 | $ 43.366.735 ± 165.986 | $ 33.564 ± 29.357 (significativo), 30 pares |
| Reorganización: 3 armadores + 2 ajustadores por línea | 10,7 ± 10,5 | $ 139.199 ± 136.005 | $ 42.640.000 | $ 44.279.199 ± 136.005 | -$ 878.901 ± 169.988 (significativo), 30 pares |
| Personal de reserva polivalente (2) | 12,3 ± 9,1 | $ 160.267 ± 118.887 | $ 44.720.000 | $ 44.880.267 ± 118.887 | -$ 1.479.969 ± 151.777 (significativo), 30 pares |
| Contratar 2 Ajustadores | 13,6 ± 13,3 | $ 177.013 ± 173.489 | $ 44.720.000 | $ 44.897.013 ± 173.489 | -$ 1.496.714 ± 177.757 (significativo), 30 pares |
| Contratar 1 Controlador | 58,0 ± 12,7 | $ 754.547 ± 165.061 | $ 43.680.000 | $ 44.434.547 ± 165.061 | -$ 1.034.248 ± 66.230 (significativo), 30 pares |
| Contratar 2 Armadores | 60,8 ± 14,1 | $ 790.727 ± 183.643 | $ 44.720.000 | $ 45.510.727 ± 183.643 | -$ 2.110.428 ± 32.074 (significativo), 30 pares |

El costo total suma las horas normales de toda la dotación (incluidas las contrataciones y el personal de reserva), las horas extra de fin de semana pagadas al doble y el costo de reorganización. El ahorro neto es la media de las diferencias réplica a réplica (escenario actual menos alternativa) y es significativo cuando su intervalo del 95 % no incluye el cero. Son 7 comparaciones contra el escenario actual, cada una al 95 %: para un nivel conjunto del 95 % habría que usar Bonferroni (99,3 % por comparación).

### Horas extra por semana

Las semanas de una misma réplica no son independientes (lo que no se recupera pasa a la semana siguiente): primero se promedian las semanas de cada réplica y el intervalo se calcula entre réplicas.

| Escenario | Réplicas | Horas extra por semana | Costo por semana | Semanas con recuperación |
|---|---|---|---|---|
| Escenario actual | 30 | 14,6 ± 3,4 | $ 190.075 ± 44.296 | 35 de 120 |
| Contratar 1 Embalador | 30 | 14,7 ± 3,4 | $ 190.979 ± 44.345 | 35 de 120 |
| Secuencia: procesos largos primero | 30 | 14,0 ± 3,2 | $ 181.684 ± 41.496 | 35 de 120 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 30 | 2,7 ± 2,6 | $ 34.800 ± 34.001 | 6 de 120 |
| Personal de reserva polivalente (2) | 30 | 3,1 ± 2,3 | $ 40.067 ± 29.722 | 7 de 120 |
| Contratar 2 Ajustadores | 30 | 3,4 ± 3,3 | $ 44.253 ± 43.372 | 6 de 120 |
| Contratar 1 Controlador | 30 | 14,5 ± 3,2 | $ 188.637 ± 41.265 | 39 de 120 |
| Contratar 2 Armadores | 30 | 15,2 ± 3,5 | $ 197.682 ± 45.911 | 38 de 120 |

## Personal, cuellos de botella y traslados

| Escenario | Util. Armador | Util. Ajustador | Util. Controlador | Util. Embalador | Coberturas | Vacantes críticas sin cubrir | Tiempo caminando |
|---|---|---|---|---|---|---|---|
| Escenario actual | 36,0 % | 82,0 % | 67,6 % | 54,6 % | 24,1 | 0,1 | 3,7 % del tiempo ocupado |
| Contratar 1 Embalador | 36,0 % | 82,0 % | 67,6 % | 46,9 % | 24,0 | 0,1 | 3,7 % del tiempo ocupado |
| Secuencia: procesos largos primero | 35,7 % | 82,1 % | 67,7 % | 54,7 % | 24,1 | 0,1 | 3,7 % del tiempo ocupado |
| Reorganización: 3 armadores + 2 ajustadores por línea | 48,4 % | 42,5 % | 68,0 % | 55,0 % | 16,1 | 0,0 | 3,7 % del tiempo ocupado |
| Personal de reserva polivalente (2) | 34,5 % | 79,4 % | 65,8 % | 53,5 % | 29,6 | 0,0 | 3,7 % del tiempo ocupado |
| Contratar 2 Ajustadores | 36,3 % | 55,4 % | 68,0 % | 54,9 % | 22,2 | 0,0 | 3,7 % del tiempo ocupado |
| Contratar 1 Controlador | 36,0 % | 82,1 % | 54,2 % | 54,7 % | 24,0 | 0,1 | 3,7 % del tiempo ocupado |
| Contratar 2 Armadores | 32,7 % | 81,8 % | 67,5 % | 54,5 % | 14,6 | 0,1 | 3,6 % del tiempo ocupado |

| Escenario | Espera armado (media / máx., min) | Espera ajuste (media / máx., min) | Espera control (media / máx., min) | Espera embalaje (media / máx., min) |
|---|---|---|---|---|
| Escenario actual | 26,1 / 175,1 | 135,6 / 533,6 | 11,4 / 351,9 | 8,9 / 704,4 |
| Contratar 1 Embalador | 26,1 / 173,3 | 135,5 / 534,6 | 11,4 / 408,9 | 5,6 / 709,2 |
| Secuencia: procesos largos primero | 28,3 / 159,3 | 140,4 / 552,4 | 15,1 / 454,7 | 12,8 / 694,8 |
| Reorganización: 3 armadores + 2 ajustadores por línea | 34,9 / 328,0 | 20,8 / 133,3 | 55,1 / 323,6 | 11,6 / 622,2 |
| Personal de reserva polivalente (2) | 24,9 / 105,2 | 123,2 / 462,4 | 7,8 / 284,4 | 5,9 / 577,9 |
| Contratar 2 Ajustadores | 26,2 / 126,8 | 66,4 / 366,4 | 45,8 / 438,3 | 12,6 / 710,0 |
| Contratar 1 Controlador | 26,1 / 172,3 | 135,5 / 538,2 | 2,1 / 246,6 | 14,4 / 575,8 |
| Contratar 2 Armadores | 23,1 / 181,2 | 150,4 / 682,5 | 11,2 / 373,3 | 8,7 / 711,1 |

## Respuestas a las preguntas de simulación

1. **Cumplimiento con la dotación actual.** En promedio, no se cumple la OF en el 25,7 % de las jornadas y se entrega a tiempo el 93,1 % de lo pedido. El faltante se concentra en **AURA** (209,3 u. por réplica), el mayor tiempo de espera en cola está en **ajuste** (135,6 min de media) y la especialidad más cargada es **ajustador** (82,0 %).
2. **Horas extra de fin de semana.** Recuperar el faltante requiere 58,5 h-hombre por réplica (14,6 por semana), con un costo de $ 760.299 ($ 190.075 por semana) pagadas al doble.
3. **Contratación.** La mejor opción de contratación evaluada es «Contratar 1 Controlador», con un ahorro neto de -$ 1.034.248 por réplica frente al escenario actual: no conviene frente a seguir pagando horas extra.
4. **Reorganización de áreas.** «Reorganización: 3 armadores + 2 ajustadores por línea» cuesta $ 878.901 por réplica frente al escenario actual, con un cumplimiento medio del 97,9 %.
5. **Personal de reserva.** «Personal de reserva polivalente (2)» cuesta $ 1.479.969 por réplica frente al escenario actual, con un cumplimiento medio del 98,0 %.
6. **Cambio de secuencia.** «Secuencia: procesos largos primero» ahorra $ 33.564 por réplica frente al escenario actual, con un cumplimiento medio del 93,4 %.

**Alternativa de menor costo total:** «Secuencia: procesos largos primero» ($ 43.366.735 por réplica, ahorro neto de $ 33.564).
