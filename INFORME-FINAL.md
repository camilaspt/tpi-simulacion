# Simulación de la línea de producción y el depósito de KRETZ: horas extra de fin de semana frente a contratación, reorganización y personal de reserva

**Trabajo Práctico Integrador de Simulación — Etapa 2/2 — Grupo 7**
[[COMPLETAR: autores y correos electrónicos]]

> Borrador en Markdown para pasar después a Overleaf. Las fórmulas están escritas en sintaxis LaTeX (`$...$`) para copiarlas tal cual. Los valores marcados `[[COMPLETAR]]` o `[[RESULTADO]]` se llenan cuando estén las corridas.

---

## Resumen

KRETZ, fabricante de balanzas, no cumple todos los días la Orden de Fabricación (OF) y recupera el faltante con horas extra los fines de semana, que se pagan al doble. Construimos un modelo de simulación de eventos discretos en AnyLogic de la planta (6 líneas, 5 modelos de balanza, viaje a depósito, ausentismo, coberturas y control de calidad por muestreo) para comparar en costo la situación actual contra siete alternativas: contratar personal de distintas especialidades, tener personal de reserva polivalente, reorganizar las líneas y cambiar la secuencia de fabricación. Cada escenario se corrió con las mismas 30 semillas fijas, de modo que cada réplica es independiente de las demás y todos los escenarios enfrentan las mismas condiciones aleatorias. Las medidas de desempeño son el costo total, el cumplimiento de la OF y las horas extra de fin de semana. Sus medias se estimaron con intervalos de confianza del 95 % basados en el Teorema Central del Límite. [[RESULTADO: una o dos frases con el hallazgo principal, por ejemplo: «La alternativa X reduce el costo total en $ Y por semana (IC 95 %: …) frente a la situación actual».]]

**Palabras clave:** simulación de eventos discretos, AnyLogic, planificación de la producción, ausentismo, horas extra, intervalos de confianza.

---

## 1. Introducción (Paso 1: Formulación del problema)

KRETZ produce balanzas comerciales e industriales en una planta de dos naves: una de producción, con 4 líneas de Armado y 2 de Control Final de 5 puestos cada una, y un depósito con el rack de materiales, el rack de espera de control de calidad y los racks de producto terminado. Las líneas no están dedicadas a un modelo: cualquier línea de Armado puede recibir cualquier equipo, y lo mismo vale para las de Control Final.

La producción de cada día sigue una Orden de Fabricación (OF) que indica qué equipos producir y en qué cantidad. Los tiempos de proceso registrados en SAP son promedios, pero en la práctica varían. A eso se suman las ausencias del personal y la cantidad limitada de puestos. Por eso hay jornadas en las que la OF no se cumple. Hoy la empresa recupera ese faltante con horas extra de fin de semana pagadas al doble, lo que representa un costo importante.

Un cálculo con tiempos medios no alcanza para estudiar el problema, porque los incumplimientos los provoca justamente la variabilidad: un día con varias ausencias o con tiempos de tarea largos deja unidades sin terminar, aunque en promedio la capacidad alcance. Por eso elegimos simular el sistema con sus fuentes de variabilidad y comparar las alternativas sobre muchas réplicas.

## 2. Objetivos (Paso 2: Objetivos y plan general del estudio)

**Objetivo general.** Determinar, en términos de costo, si a KRETZ le conviene seguir recuperando el faltante con horas extra de fin de semana o adoptar alguna alternativa de dotación u organización.

**Objetivos específicos.**

1. Reproducir el funcionamiento de las jornadas de trabajo para medir con qué frecuencia no se cumple la OF y en qué equipos, puestos o especialidades se concentra el faltante.
2. Estimar las horas extra de fin de semana necesarias para recuperar el faltante y su costo.
3. Comparar el costo total de la situación actual con el de siete alternativas: contratar personal (Ajustadores, Armadores, Controlador o Embalador), tener personal de reserva polivalente, reorganizar los puestos de las líneas y cambiar la secuencia de fabricación.
4. Informar cada comparación con un intervalo de confianza que permita decir si la diferencia es estadísticamente significativa.

## 3. Metodología

### 3.1 Sistema y alcance (Paso 3: Modelo conceptual)

El modelo representa el recorrido de cada unidad de los 5 modelos seleccionados como representativos de la carga de la planta: AILA 30KG, REPORT LT, NOVEL ECO, LURA y AURA. Cada unidad se libera según la OF del día y termina cuando pasa a stock, después del control de calidad. Quedan fuera del alcance los demás modelos que fabrica KRETZ, la cadena de abastecimiento (el rack de materiales siempre tiene stock), el despacho a clientes, las fallas de equipos y el retrabajo de las unidades rechazadas.

Los tres aspectos centrales que el modelo debía capturar son:

- **Viaje a depósito.** Antes de empezar un equipo, el operario que hará su primer puesto camina hasta el rack único de materiales, retira lo necesario (2 min según SAP) y vuelve a su puesto. El tiempo de caminata forma parte del proceso.
- **Ausentismo y coberturas.** Al inicio de cada jornada se determina quién falta. El puesto del ausente queda vacante hasta que otro operario lo cubre dejando el suyo, de modo que la cobertura traslada el cuello de botella en lugar de eliminarlo.
- **Control de calidad por muestreo.** De la producción diaria de cada modelo, el inspector controla solo el primer y el último equipo.

### 3.2 Modelo conceptual (Paso 3: Modelo conceptual)

[[FIGURA: diagrama_conceptual.png — Diagrama conceptual del sistema]]

- **Entidades:** la balanza (unidad), con atributos de modelo, línea asignada, tiempos de inicio y fin y resultado de la inspección; la OF del día; la muestra de calidad por modelo.
- **Recursos:** los operarios, con una especialidad (Armador, Ajustador, Controlador o Embalador), un puesto habitual y un estado de asistencia; el rack único de materiales; el inspector de calidad.
- **Dotación de línea del escenario actual:** 4 líneas de Armado con 4 armadores y 1 ajustador cada una, y 2 líneas de Control Final con 2 controladores y 3 embaladores cada una (30 operarios de línea). A ellos se suman 10 empleados de depósito y 1 inspector, que entran solo en los costos.
- **Colas:** unidades liberadas esperando operario, retiro en el rack de materiales, colas por puesto (FIFO, capacidad ilimitada) y rack de espera de calidad.
- **Eventos principales:** inicio de jornada (OF y asistencia), coberturas, liberación de unidades, llegada del operario al rack o al puesto, fin de tarea, ingreso al rack de calidad, inspección, cierre de jornada y jornada de recuperación de fin de semana.

Las secuencias de puestos y los tiempos medios de cada modelo, relevados de SAP, se presentan en la Tabla 1.

**Tabla 1. Secuencia y tiempos medios por modelo (min). Todos empiezan con el retiro de materiales en el depósito (2 min).**

| Modelo | Armado | Ajuste / Ensamble | Control Final | Embalaje | Total sin caminata |
|---|---|---|---|---|---|
| AILA 30KG | 3,5 + 7 + 7 + 7,5 | 5 | 4,5 | 10 | 46,5 |
| REPORT LT | 11 | 12 | 12 | 12 | 49 |
| NOVEL ECO | 3,15 | 3 | 2,25 | 3 | 13,4 |
| LURA (importado, sin armado) | — | 4 | 3,15 | 3,15 | 12,3 |
| AURA | 3,15 | 3 | 2,5 | 2,88 | 13,53 |

### 3.3 Datos de entrada y supuestos (Paso 4: Recolección de datos)

| Dato | Valor en el modelo | Fuente |
|---|---|---|
| Tiempos de tarea | Triangular con mínimo $0{,}8\,m$, moda $0{,}9\,m$ y máximo $1{,}3\,m$, donde $m$ es la media de SAP (la media de la distribución es $m$) | SAP; asimetría supuesta: las demoras largas son más probables que las tareas muy cortas |
| Jornada | Turno de 480 min, 5 jornadas por semana | KRETZ |
| Ausentismo | 6 % por empleado y día, con un factor por día de la semana (lunes 1,25; martes 1,0; miércoles y jueves 0,9; viernes 1,1); 10 % en la recuperación de fin de semana | [[COMPLETAR: planilla de asistencia o declarar como supuesto]] |
| Velocidad de caminata | 1,3 m/s, en línea recta y pasando por la puerta entre naves | Valor típico de marcha; plano a escala (16 px = 1 m) |
| Inspección de calidad | 8 min por equipo inspeccionado; 3 % de rechazo | [[COMPLETAR]] |
| OF | 3 OF de ejemplo (equilibrada; con mucha REPORT LT; alto volumen de equipos cortos) | [[COMPLETAR: reemplazar por OF reales o declarar como supuesto]] |
| Costo de la hora normal | $ 6.500 por empleado, con cargas | [[COMPLETAR: fuente]] |
| Recargo de fin de semana | ×2 | KRETZ |
| Recuperación de fin de semana | Hasta 16 h; lo que no se recupera pasa a la semana siguiente | Supuesto |

Supuestos principales: los 5 modelos son representativos de la carga; el rack de materiales nunca se queda sin stock; la asistencia se define al inicio de la jornada; la jornada de fin de semana rinde por hora lo mismo que una jornada normal y solo cambia el costo; el operario que retira los materiales es siempre el que hace el primer puesto de la unidad.

### 3.4 Construcción del modelo (Paso 5: Traducción del modelo / construcción en AnyLogic)

El modelo se construyó en AnyLogic usando Process Modeling Library. Un único flujo atiende los 5 modelos: cada unidad recorre su receta y, en cada paso, toma un operario de la especialidad requerida (*Seize*), el operario camina hasta el puesto, ejecuta la tarea (*Delay*) y lo libera (*Release*). El primer paso incluye el retiro en el rack, con el mismo *Seize* que el primer puesto, para que el operario que retira los materiales sea el que hace la primera tarea.

Las líneas equivalentes se resuelven con una regla de ruteo en la condición del *Seize*: se elige un operario de un puesto apto en la línea ya asignada a la unidad o en cualquier línea capaz de completar el equipo con el personal presente ese día.

Los operarios son agentes que se desplazan sobre el plano a escala. Se evaluó la Pedestrian Library, que modela la caminata con paredes y obstáculos, pero la edición Personal Learning de AnyLogic limita esa librería a 5 horas de tiempo simulado, y cada réplica necesita 4 semanas. Por eso la caminata se calcula como distancia sobre velocidad, en línea recta y pasando por la puerta entre naves cuando el operario cambia de nave.

Al cierre de cada jornada se compara lo producido a tiempo con la OF. Al terminar la semana, el faltante acumulado se procesa en una jornada de recuperación de fin de semana con el personal que asiste ese día. Las horas-hombre de esa jornada se valorizan al doble.

### 3.5 Verificación y validación (Paso 6: Verificación — Paso 7: Validación)

**Verificación** (el modelo hace lo que dice la especificación):

- Corridas con variabilidad nula (`variabilidadTiempos = 0`) y sin ausencias, comparando el tiempo de proceso de una unidad aislada con la suma de los tiempos de la Tabla 1 más la caminata calculada a mano. [[RESULTADO]]
- Seguimiento de unidades individuales en la animación 3D: retiro en el rack, recorrido de puestos, rack de calidad y stock.
- Controles de conservación: unidades liberadas = terminadas + en proceso + pendientes al cierre de cada semana.
- Reproducibilidad: dos corridas con la misma semilla dan exactamente los mismos resultados.
- Inspección: solo el primer y el último equipo de cada modelo por día.

**Validación** (el escenario actual se parece a la planta real):

- Comparación del cumplimiento de la OF y de las horas extra de fin de semana simuladas en el escenario actual con el historial de KRETZ. [[COMPLETAR: datos reales y resultado de la comparación]]
- Revisión del comportamiento del modelo con personal de la planta (validación cara a cara): qué puestos se saturan y qué coberturas se hacen. [[COMPLETAR]]

### 3.6 Medidas de desempeño (Paso 8: Diseño de experimentos)

De cada réplica $i$ de un escenario se registran tres medidas de desempeño. Son las que responden directamente a la pregunta del estudio:

1. **Costo total semanal** $C_i$ ($ por semana): horas normales de toda la dotación, incluidas contrataciones y reserva, más horas extra de fin de semana al doble, más el costo de la reorganización prorrateado. Es la medida principal para decidir entre escenarios.
2. **Cumplimiento de la OF** $P_i$ (%): unidades terminadas dentro de la jornada sobre unidades pedidas, en el horizonte de la réplica.
3. **Horas extra de fin de semana** $H_i$ (horas-hombre por semana): horas necesarias para recuperar el faltante.

Como medidas complementarias, para explicar los resultados y no para elegir el escenario, se informan la utilización de operarios por especialidad, el tiempo medio de espera en cola por tipo de puesto (cuellos de botella), las coberturas por jornada y la fracción del tiempo de los operarios que se va en caminar.

### 3.7 Diseño de experimentos (Paso 8: Diseño de experimentos)

**Escenarios.** Se compararon 8 escenarios (Tabla 2). Todos usan la misma OF, el mismo horizonte y los mismos datos de entrada; solo cambian los parámetros indicados.

**Tabla 2. Escenarios evaluados.**

| # | Escenario | Cambio respecto del escenario actual |
|---|---|---|
| E0 | Escenario actual | Dotación actual, faltante recuperado con horas extra de fin de semana |
| E1 | Contratar 2 Ajustadores | +2 Ajustadores |
| E2 | Contratar 2 Armadores | +2 Armadores |
| E3 | Contratar 1 Controlador | +1 Controlador |
| E4 | Contratar 1 Embalador | +1 Embalador |
| E5 | Personal de reserva | 2 operarios polivalentes que cubren ausencias |
| E6 | Reorganización | 3 armadores + 2 ajustadores por línea de Armado, coberturas entre especialidades; costo de reorganización $ 1.500.000 |
| E7 | Cambio de secuencia | Se fabrican primero los equipos con procesos más largos |

**Horizonte y tipo de simulación.** Es una simulación con horizonte finito (terminante): cada réplica simula 4 semanas, es decir 20 jornadas de 480 min más hasta 4 jornadas de recuperación de fin de semana. Cada réplica arranca con la planta vacía, igual que una semana real arranca sin unidades en proceso, por lo que no hace falta descartar un período de calentamiento.

**Réplicas y semillas.** Cada escenario se corre $n = 30$ veces. Para asegurar que las réplicas sean independientes, cada una usa una semilla distinta del generador de números aleatorios. Las semillas no se sortean: se fija de antemano una lista y se usa **la misma lista en todos los escenarios**:

$$\mathcal{S} = \{s_1, s_2, \dots, s_{30}\} = \{1001, 1002, \dots, 1030\}$$

[[COMPLETAR: confirmar la lista usada en las corridas]]

Esto tiene tres consecuencias:

- **Independencia dentro de cada escenario.** Las 30 réplicas de un escenario usan semillas distintas, así que sus resultados $X_1, \dots, X_n$ son observaciones independientes e idénticamente distribuidas de la medida de desempeño.
- **Reproducibilidad.** Cualquier réplica se puede repetir exactamente con su semilla, y quien lea el informe puede volver a obtener los mismos números.
- **Comparación justa entre escenarios.** La réplica $j$ de cada escenario enfrenta las mismas condiciones aleatorias de partida (mismas ausencias y mismos tiempos sorteados en la medida en que los escenarios consumen los números en el mismo orden). Las diferencias entre escenarios se deben entonces a los cambios de dotación u organización y no a que a un escenario le tocaron, por azar, días con más ausencias. Esta técnica se conoce como números aleatorios comunes.

En AnyLogic, las réplicas se corren con un experimento de Variación de parámetros que recorre el parámetro `semilla` del modelo sobre la lista $\mathcal{S}$, una corrida por semilla, para cada escenario. Cada corrida guarda una fila con sus medidas en `Resultados/resultados_corridas.csv`.

**Cantidad de réplicas.** Se hizo primero una corrida piloto de $n_0 = 10$ réplicas del escenario actual para estimar el desvío del costo total. La cantidad de réplicas necesaria para estimar la media con un error relativo $\varepsilon$ (por ejemplo, $\varepsilon = 5\,\%$) es

$$n \ge \left( \frac{z_{\alpha/2}\, S}{\varepsilon\, \bar{X}} \right)^2 .$$

[[RESULTADO: valor de $n$ obtenido con el piloto; si da más de 30, usar ese $n$ y ampliar la lista de semillas]]. Además, se fijó un mínimo de 30 réplicas para que la aproximación normal del Teorema Central del Límite sea razonable.

### 3.8 Análisis estadístico (Paso 9: Corridas de producción y análisis)

**Intervalo de confianza para la media de cada escenario.** Sea $X_1, \dots, X_n$ la medida de desempeño (por ejemplo, el costo total semanal) en las $n$ réplicas de un escenario. Las réplicas son independientes porque cada una usa una semilla distinta, y tienen la misma distribución porque corren el mismo modelo con los mismos parámetros. Se calculan la media y el desvío muestrales:

$$\bar{X} = \frac{1}{n}\sum_{i=1}^{n} X_i, \qquad S = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}\left(X_i - \bar{X}\right)^2}.$$

Por el Teorema Central del Límite, para $n$ grande la media muestral se distribuye aproximadamente normal, $\bar{X} \sim N\!\left(\mu, \sigma^2/n\right)$, sea cual sea la distribución de cada $X_i$. Estandarizando se obtiene una normal estándar:

$$Z = \frac{\bar{X} - \mu}{S/\sqrt{n}} \sim N(0, 1).$$

Entonces $P\left(-z_{\alpha/2} \le Z \le z_{\alpha/2}\right) = 1 - \alpha$, y despejando $\mu$ se obtiene el intervalo de confianza:

$$\mu \in \left[\, \bar{X} - z_{\alpha/2}\,\frac{S}{\sqrt{n}} \; ; \; \bar{X} + z_{\alpha/2}\,\frac{S}{\sqrt{n}} \,\right].$$

Con un nivel de confianza del 95 % ($\alpha = 0{,}05$), $z_{0{,}025} = 1{,}96$.

**Comparación entre escenarios.** Para comparar una alternativa $k$ con el escenario actual se usa el ahorro de cada réplica. Como las dos corridas de la réplica $j$ usan la misma semilla $s_j$, se pueden emparejar:

$$D_j = C_j^{(E0)} - C_j^{(k)}, \qquad j = 1, \dots, n.$$

Las $D_j$ son independientes entre sí (cada par usa una semilla distinta), así que se aplica el mismo procedimiento: por el Teorema Central del Límite, $\bar{D}$ es aproximadamente normal, se estandariza a $Z$ y el intervalo del ahorro medio es

$$\bar{D} \pm z_{\alpha/2}\,\frac{S_D}{\sqrt{n}}.$$

Si el intervalo no contiene el cero, la diferencia es significativa al 95 %: si está entero por encima del cero, la alternativa ahorra; si está entero por debajo, la alternativa cuesta más. Como las dos corridas de cada par comparten la semilla, sus resultados están correlacionados positivamente, y por eso $S_D$ suele ser bastante menor que si los escenarios se hubieran corrido con semillas distintas: los intervalos de las diferencias son más angostos con la misma cantidad de réplicas.

## 4. Resultados (Paso 9: Corridas de producción y análisis)

> Los valores de esta sección salen de `Resultados/resultados_corridas.csv` después de correr los 8 escenarios con las 30 semillas.

### 4.1 Escenario actual

[[RESULTADO: párrafo con lo que muestra el escenario actual]]

- Jornadas en las que no se cumple la OF: [[RESULTADO]] % (IC 95 %: [[ ]]).
- Faltante concentrado en: [[RESULTADO: modelo]], cuello de botella en [[RESULTADO: tipo de puesto]], especialidad más cargada: [[RESULTADO]].
- Horas extra de fin de semana: [[RESULTADO]] h-hombre por semana, con un costo de $ [[RESULTADO]] por semana.
- Validación: [[RESULTADO: comparación con los datos reales de KRETZ]].

### 4.2 Medidas de desempeño por escenario

**Tabla 3. Media e intervalo de confianza del 95 % ($\bar{X} \pm 1{,}96\,S/\sqrt{n}$, $n = 30$).**

| Escenario | Costo total semanal ($) | Cumplimiento de la OF (%) | Horas extra (h-hombre/semana) |
|---|---|---|---|
| E0 Actual | [[ ]] ± [[ ]] | [[ ]] ± [[ ]] | [[ ]] ± [[ ]] |
| E1 +2 Ajustadores | | | |
| E2 +2 Armadores | | | |
| E3 +1 Controlador | | | |
| E4 +1 Embalador | | | |
| E5 Reserva (2) | | | |
| E6 Reorganización | | | |
| E7 Secuencia | | | |

[[FIGURA: gráfico de intervalos de confianza del costo total por escenario]]

### 4.3 Ahorro neto frente al escenario actual

**Tabla 4. Ahorro medio por semana ($\bar{D} \pm 1{,}96\,S_D/\sqrt{n}$) y significación.**

| Alternativa | Ahorro medio ($/semana) | IC 95 % | ¿Significativo? |
|---|---|---|---|
| E1 +2 Ajustadores | | [ ; ] | |
| E2 +2 Armadores | | [ ; ] | |
| E3 +1 Controlador | | [ ; ] | |
| E4 +1 Embalador | | [ ; ] | |
| E5 Reserva (2) | | [ ; ] | |
| E6 Reorganización | | [ ; ] | |
| E7 Secuencia | | [ ; ] | |

### 4.4 Medidas complementarias

[[RESULTADO: tabla de utilización por especialidad, espera media por tipo de puesto, coberturas y fracción de tiempo caminando, solo para explicar por qué cada alternativa mejora o no]]

## 5. Conclusiones (Paso 10: Documentación e implementación)

[[RESULTADO: responder en prosa, con los números de las tablas 3 y 4]]

1. **Situación actual.** Con la dotación y la organización actuales, la OF no se cumple en [[ ]] % de las jornadas; el faltante se concentra en [[ ]].
2. **Costo de las horas extra.** Recuperar el faltante requiere [[ ]] h-hombre por semana, con un costo de $ [[ ]].
3. **Contratación.** [[ ¿Conviene? ¿Cuántos y de qué especialidad? ]]
4. **Reorganización.** [[ ]]
5. **Personal de reserva.** [[ ]]
6. **Secuencia de fabricación.** [[ ]]

**Recomendación para KRETZ.** [[ ]]

**Limitaciones y trabajo futuro.** Los resultados dependen de [[ las OF de ejemplo / la probabilidad de ausencia supuesta / el costo de la hora ]]; conviene repetir el análisis con OF reales y con la probabilidad de ausencia estimada de la planilla de asistencia. La caminata se modeló en línea recta y no con la Pedestrian Library, por la limitación de la edición Personal Learning, lo que puede subestimar levemente los tiempos de traslado.

## Referencias

- Law, A. M. (2015). *Simulation Modeling and Analysis* (5.ª ed.). McGraw-Hill.
- Banks, J., Carson, J. S., Nelson, B. L. y Nicol, D. M. (2010). *Discrete-Event System Simulation* (5.ª ed.). Pearson.
- The AnyLogic Company. *AnyLogic Help: Process Modeling Library*. https://anylogic.help
- [[COMPLETAR: bibliografía de la cátedra]]

## Anexos (material entregado) (Paso 10: Documentación e implementación)

- Modelo de AnyLogic (`.alp`) y link de AnyLogic Cloud: [[COMPLETAR]]
- Planilla de cálculo con los resultados de las corridas: [[COMPLETAR]]
- Video de presentación: [[COMPLETAR]]
