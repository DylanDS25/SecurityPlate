# Semana 03 - Taxonomía de Inteligencia Artificial

## Resultado automático frente a clasificación manual de referencia

| Caso | Categoría automática principal | Categorías detectadas | Manual | Estado |
|---:|---|---|---|---|
| 1 | Visión por computador | Visión por computador | Visión por computador | Coincide |
| 2 | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Coincide |
| 3 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Coincide |
| 4 | Búsqueda y optimización | Búsqueda y optimización | Búsqueda y optimización | Coincide |
| 5 | Sistemas de recomendación | Sistemas de recomendación | Sistemas de recomendación | Coincide |
| 6 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Coincide |
| 7 | Visión por computador | Visión por computador | Visión por computador | Coincide |
| 8 | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Coincide |
| 9 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Coincide |
| 10 | Sistemas expertos | Sistemas expertos | Sistemas expertos | Coincide |
| 11 | Visión por computador | Visión por computador | Visión por computador | Coincide |
| 12 | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Coincide |
| 13 | Robótica y sistemas autónomos | Robótica y sistemas autónomos | Robótica y sistemas autónomos | Coincide |
| 14 | Búsqueda y optimización | Búsqueda y optimización | Búsqueda y optimización | Coincide |
| 15 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Coincide |
| 16 | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Procesamiento de lenguaje natural | Coincide |
| 17 | Visión por computador | Visión por computador, Robótica y sistemas autónomos | Visión por computador | Coincide |
| 18 | Sistemas expertos | Sistemas expertos | Sistemas expertos | Coincide |
| 19 | Robótica y sistemas autónomos | Robótica y sistemas autónomos | Robótica y sistemas autónomos | Coincide |
| 20 | Búsqueda y optimización | Búsqueda y optimización | Búsqueda y optimización | Coincide |
| 21 | Visión por computador | Visión por computador | Aprendizaje automático predictivo | Revisar |
| 22 | Requiere análisis | Requiere análisis | Visión por Computador | Revisar |
| 23 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Detección de Anomalías | Revisar |
| 24 | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | Aprendizaje Automático Predictivo | Revisar |
| 25 | Sistemas de recomendación | Sistemas de recomendación | Búsqueda y Optimización | Revisar |
| 26 | Requiere análisis | Requiere análisis | Sistemas de Recomendación | Revisar |
| 27 | Visión por computador | Visión por computador | Detección de Anomalías | Revisar |
| 28 | Detección de Anomalías | Detección de Anomalías, Sistemas expertos | Visión por Computador | Revisar |
| 29 | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | Sistemas Expertos | Revisar |
| 30 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Aprendizaje Automático Predictivo | Revisar |
| 31 | Visión por computador | Visión por computador | Detección de Anomalías | Revisar |
| 32 | Requiere análisis | Requiere análisis | Visión por Computador | Revisar |
| 33 | Detección de Anomalías | Detección de Anomalías, Robótica y sistemas autónomos | Detección de Anomalías | Coincide |
| 34 | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | Robótica y Sistemas Autónomos | Revisar |
| 35 | Aprendizaje automático predictivo | Aprendizaje automático predictivo | Búsqueda y Optimización | Revisar |
| 36 | Visión por computador | Visión por computador | Aprendizaje Automático Predictivo | Revisar |
| 37 | Requiere análisis | Requiere análisis | Visión por Computador | Revisar |
| 38 | Sistemas expertos | Sistemas expertos | Visión por Computador | Revisar |
| 39 | Robótica y sistemas autónomos | Robótica y sistemas autónomos | Sistemas Expertos | Revisar |
| 40 | Aprendizaje automático predictivo | Aprendizaje automático predictivo, Búsqueda y optimización | Robótica y Sistemas Autónomos | Revisar |

Coincidencia con la referencia: **52.50%** (21/40).

## Cinco reglas propias

Reemplaza o amplía las cinco reglas de ejemplo de `CUSTOM_RULES` y explica aquí por qué son pertinentes para tu dominio.

## Discrepancias y análisis

Para cada discrepancia explica: (1) qué palabra o frase activó la regla, (2) por qué la clasificación manual difiere y (3) qué regla modificarías.

## Nota técnica

Un problema real puede pertenecer a varias áreas de IA. La columna 'principal' usa la categoría con mayor cantidad de coincidencias; las demás coincidencias se conservan como categorías secundarias.

# Reglas y palabras agregadas

### **Regla Agregada:** Detección de Anomalías
- **Palabras**: "anomalía", "anomalías", "sospechoso", "alerta", "alertas"
- **Relevancia**: El proyecto requiere identificar comportamientos fuera de lo normal, lo cual genera una categoria diferente a aprendizaje predictivo
- **Ejemplo**: Detectar ocupantes sospechosos, intentos de robo.

### **Terminos Agregados:** "placa", "matricula", "matriculas", "casco", "cascos", "vestimenta", "ropa", "prenda"
- **Regla**: Visión por computador
- **Relevancia**: Son elmentos visuales caracteristicos en motos que no se incluyen dentro de comportamientos y requieren el procesamiento de imagen para su identificación.

### **Terminos Agregados:** "protocolo", "protocolos", "alerta", "alertas", "regla", "basado en reglas", "notifique"
- **Regla**: Sistemas expertos
- **Relevancia**: Sistemas de seguridad funcionan con reglas determinístas y difiere del aprendijaze de patrones (Aprendizaje automatico)

# Análisi de Discrepancias

# Punto 5: Discrepancias Casos 21-40

| Caso | Automática | Manual | Palabra/Frase Activadora | Observación | Regla a Modificar |
|---|---|---|---|---|---|
| 21 | Visión por Computador | Aprendizaje Automático Predictivo | "imagen" | La palabra "imagen" activó Visión por Computador, pero el objetivo real es predecir comportamientos basados en datos históricos. El medio (imagen) no es el objetivo (predicción). | Priorizar "predecir", "probabilidad" sobre "imagen" cuando hay contexto predictivo; agregar jerarquía: si hay predicción + imagen = Aprendizaje Predictivo |
| 22 | Requiere análisis | Visión por Computador | Sin palabra clave detectada | El sistema no reconoció palabras visuales ("cámara", "video", "foto") por ser muy genéricas o estar en contexto distinto. | Expandir palabras clave de Visión: agregar "cámara", "video", "visual", "fotográfico" como términos primarios |
| 23 | Aprendizaje Automático Predictivo | Detección de Anomalías | "predecir" | "Predecir" activó Aprendizaje Predictivo, pero el caso es identificar comportamientos ANORMALES en el presente, no futuros. | Crear regla diferenciadora: "anomalía", "sospechoso", "inusual" en contexto presente > "predecir" en contexto futuro |
| 24 | Aprendizaje + Búsqueda | Aprendizaje Automático Predictivo | "predecir", "optimizar" | Detectó ambas palabras clave; "optimizar" agregó erróneamente Búsqueda como categoría secundaria. | Implementar orden de prioridad: si "predecir/probabilidad" está presente y es núcleo del problema, ignorar "optimizar" como secundaria |
| 25 | Sistemas de Recomendación | Búsqueda y Optimización | "recomendar" | "Recomendar" fue interpretado como sugerencia personalizada (Recomendación), pero "combinación óptima" requiere Búsqueda y Optimización. | Diferenciar: "recomendar" + "combinación óptima/presupuesto/capacidad" = Búsqueda; "recomendar" + "preferencia/historial" = Recomendación |
| 26 | Requiere análisis | Sistemas de Recomendación | Sin palabra clave detectada | Palabras clave como "sugerir", "personalizado", "preferencia" no fueron detectadas o están mal formuladas. | Ampliar palabras clave de Recomendación: "personalizar", "preferencia individual", "adaptado", "basado en usuario" |
| 27 | Visión por Computador | Detección de Anomalías | "video", "cámara" | Palabras de captura visual activaron Visión, ignorando que el objetivo es detectar PATRONES SOSPECHOSOS, no procesar la imagen. | Priorizar "sospechoso", "patrón anómalo", "comportamiento inusual" sobre "video/cámara" cuando hay contexto de detección |
| 28 | Detección de Anomalías + Sistemas Expertos | Visión por Computador | Ninguna palabra visual detectada | El clasificador no encontró "ocupante", "vestimenta", "accesorio", "reconocer" porque no están en palabras clave de Visión. | Agregar a Visión: "ocupante", "vestimenta", "ropa", "accesorio", "prenda", "identificar visualmente", "reconocer" |
| 29 | Aprendizaje + Búsqueda | Sistemas Expertos | "predecir", "optimizar" | Detectó términos de ML, pero el caso es un SISTEMA DE REGLAS determinístico (IF-THEN), no aprendizaje. | Crear palabras clave de Sistemas Expertos: "basado en reglas", "IF-THEN", "lógica determinística", "motor de reglas" con alta prioridad |
| 30 | Aprendizaje Automático Predictivo | Aprendizaje Automático Predictivo | "predecir", "probabilidad" | Clasificación correcta | Sin cambios |
| 31 | Visión por Computador | Detección de Anomalías | "video", "cámara" | Similar al caso 27: procesamiento visual es el MEDIO; el OBJETIVO es detectar comportamientos anómalos en tiempo real. | Implementar jerarquía: "patrón anómalo/sospechoso" > "video/cámara" en contexto de seguridad |
| 32 | Requiere análisis | Visión por Computador | Sin palabra clave detectada | Palabras como "analizar imagen", "clasificar", "leer" (en contexto visual) no fueron reconocidas. | Expandir vocabulario visual: "analizar imagen", "clasificar visualmente", "leer", "extraer información visual", "procesamiento de imagen" |
| 33 | Detección de Anomalías + Robótica | Detección de Anomalías | "anomalía", "patrón" | Detectó correctamente Detección de Anomalías; Robótica se agregó como secundaria (probablemente por "robot"/"dron"). | Sin cambios fundamentales; la categoría principal es correcta |
| 34 | Aprendizaje + Búsqueda | Robótica y Sistemas Autónomos | "predecir", "optimizar" (no "autónomo") | Detectó ML y Búsqueda pero ignoró palabras de autonomía. "Autónomo", "robot", "sin intervención" no fueron priorizadas. | Crear regla de Robótica Autónoma: "autónomo", "robot", "dron", "patrullaje sin intervención" con mayor peso que predicción/optimización |
| 35 | Aprendizaje Automático Predictivo | Búsqueda y Optimización | "predecir", "probabilidad" (falta "optimizar") | Detectó predicción pero el caso es OPTIMIZAR una ruta/recurso/combinación. "Combinación óptima" debería estar presente y priorizar. | Priorizar "optimizar", "mejor", "combinación óptima", "máxima eficiencia" sobre "predecir" cuando el objetivo es búsqueda |
| 36 | Visión por Computador | Aprendizaje Automático Predictivo | "imagen", "foto" | "Imagen" activó Visión, ignorando que se usa para PREDECIR. Visión es el medio, predicción es el objetivo. | Implementar regla: "imagen/foto" + "predecir/clasificar/comportamiento" = Aprendizaje Predictivo (no Visión pura) |
| 37 | Requiere análisis | Visión por Computador | Sin palabra clave detectada | "Detectar", "reconocer", "identificar" (en contexto visual) no fueron incluidas como palabras clave de Visión. | Agregar a Visión: "detectar", "reconocer", "identificar", "extraer" (cuando van acompañados de contexto visual) |
| 38 | Sistemas Expertos | Visión por Computador | "reglas", "políticas" | "Reglas" activó Sistemas Expertos, ignorando que el procesamiento es VISUAL. El contexto debería ser visual, no de reglas. | Diferenciar: si hay "imagen/foto/visual" + "reglas" = Visión + Sistemas Expertos (pero Visión primaria); si solo "reglas" = Sistemas Expertos |
| 39 | Robótica y Sistemas Autónomos | Sistemas Expertos | "robot", "dron" | "Robot"/"dron" activó Robótica, pero el caso es un SISTEMA DE REGLAS determinístico, no una máquina física. | Diferenciar palabras clave: "robot/dron FÍSICO" vs "sistema basado en REGLAS LÓGICAS"; agregar "motor de reglas", "regla lógica" como exclusivas de Sistemas Expertos |
| 40 | Aprendizaje + Búsqueda | Robótica y Sistemas Autónomos | "predecir", "optimizar" (no "autónomo") | Detectó componentes de ML y Búsqueda pero ignoró que el sistema opera COMPLETAMENTE AUTÓNOMO. "Autónomo", "patrullaje sin intervención" no fueron priorizar. | Crear regla fuerte: "autónomo", "sin intervención humana", "patrullaje autónomo", "dron autónomo" = Robótica (máxima prioridad sobre predicción/optimización) |

# Limitaciones y mejoras
El algoritmo se basa en coincidencia literal de palabras clave (normalizadas). No captura sinónimos, contextos semánticos o frases compuestas más complejas. Se limita a las palabras que se encuentran en las categorias y las reglas.
Una mejora que podemos implementar es la comprension de lenguaje natural para mantener un contexto de fraces que se correlacionen con la categoria o regla.