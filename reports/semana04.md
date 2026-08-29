# Semana 03 - Marco tecnológico de la inteligencia artificial
## Descripcion del Problema
### A*
Normalizar imagenes de matriculas que cuenten con distorsiones por diferentes factoresm por medio de una secuencia óptima de acciones que nos permita identificar caracteres en las matriculas de manera clara para verificar con máxima confianza si el propietario que sale es el mismo que entró.
### Minimax
Analizar caracteristicas del casco de un conductor como lo son color, marca, tipo de casco, daños,marcas o calcomanias, considerando posibilidades de comparación. Con esto se obtendra mayor confianza de coincidencia mientra se represena un escenario de comparación más desfavorable para dificultar la identificación.

### Representación
| Titulo | Imagenes de matriculas con distorsion |
|---|---|

| Concepto |  Descripción |
| --- | --- |
| Estado inicial | Moto ingresa y la foto de su matricula es almacenada sin alteración del sistema (brillo, rotación, contraste, reducción de ruido) y se proporciona un porcentaje de confiabilidad (OCR) |
| Estados posibles | <li> Rotacion: medible en grados y con pasos de 5°<br><li>Brillo: medible en porcentaje y con pasos de 10% -<br><li> Contraste: medible en porcentaje  y con pasos de 10% <br><li> Reducción de ruido: medible como booleano <br><li> Posibles estados ~3000<br><li> Ejemplo: (5,30,-10,False) → Rotada 5°, Brillo +30%, Contraste -10%, Sin denoise|
| Acciones u operadores | Mejora en la confianza <br><li>Rotcación: Corregir el ángulo de captura (±5 hasta ±25) <br><li> Brillo: Mejorar Visibilidad (±10 hasta ± 50) <br><li> Contraste: Diferenciar entre caracteres y fondo (±10 hasta ±50) <br><li> Denoise: Reduce el ruido en la imagen (True/flase) <br><li> Recortar: aisla la zona de la matricula |
| Transiciones y sucesores | Estado actual: (0°, 0%, 0%, False, conf=45%)<br>Sucesores posibles (aplicando UNA acción):<br> 1. Rotar +5°  → (5°, 0%, 0%, False, conf=48%)    [g=1]<br>2. Rotar +10° → (10°, 0%, 0%, False, conf=51%)   [g=1]<br>3. Rotar +15° → (15°, 0%, 0%, False, conf=55%)   [g=1]<br>4. Rotar +20° → (20°, 0%, 0%, False, conf=58%)   [g=1]<br>5. Brillo +10% → (0°, 10%, 0%, False, conf=49%)  [g=1]<br>6. Brillo +20% → (0°, 20%, 0%, False, conf=52%)  [g=1]<br>7. Contraste +10% → (0°, 0%, 10%, False, conf=47%) [g=1]<br>8. Denoise → (0°, 0%, 0%, True, conf=70%)        [g=2] |
| Meta | En el momento que la imagen se encuentre en una medida >= 85% de Confiabilidad y lectura de 6 caracteres|
| Costo de camino | <li>Rotar → costo = 1 <br><li> Brillo → costo = 1 <br><li> Contraste → costo = 1 <br><li> Denoise → costo = 2 <br><li> Recorte → costo 1|
| Heurística, cuando corresponda | h(n) = (100 - confianza_OCR_actual) / 10<br>Donde:<br>- confianza_OCR_actual: confianza actual del nodo n<br>- 10: factor que asume cada acción mejora ~10% confianza<br> h es la estimación de acciones que se debe hace para llegar a una confianza admisible |
| Criterio utilizado para seleccionar la solución | Definimos que termina cuando tengamos un nodo de meta y nos aseguremos que no hay menor costo.|

## Justificación
### Problema
Para normalizar una matricula distorcionada es pertienente determinar una secuencia de acciones optimas y así conseguir la máxima confianza al momento de verificar. Este es nuestro punto inicial para integrar A* nuestro problema, ya que contamos con multiples caminos y una gran variedad de combinaciones al momento de transformar nuestra imagen a un OCR del 85% por el camino mas ótimo, al contar con suposiciones (heuristica) la desición de A* es definitiva.

### Representacion de Estados
**Estado:** Fotograma de cómo se ve la matricula en cada momento en que se efectua una secuencia.
**Acción:** Operacion de procesamientos de imagen (Rotación, Brillo, Cotraste, Reducción de ruido y Recortar).
**Transición:** Trazabilidad entre secuencias para aplicar una transformación (Estado_A → [Acción, Costo] → Estado_B).
**Meta:** Llegar al objetivo donde el OCR supera el umbral de 85% y cumple con la lectura de 6 caracteres.
**Costo:** Recurso consumido por una secuencia.
**Heuristica:** Contabiliza las acciones que considera que faltan para llegar a la meta de modo que sea la mas óptima.

### Minimax
| Concepto | Aplicación |
|---|---|
| Estado | <li> Caracteristica verificada<br><li> Nivel de engaño del ladron<br><li> confianza de sistema. <br> Se configura como Estado =(caracteristica_verificada, nivel_engaño_ladron, confianza_sistema) |
| Acciones disponibles Jugador MAX | <li>Verificar color del casco <br><li> Verificar daños del casco <br><li> Verificar visor del casco <br><li> Verificar calcomanias del casco  <br><li> Verificar matricula|
| Acciones disponibles Jugador MIN | <li>Usar mismo casco → No engaño <br><li> Cambiar a casco similar → Engaño parcial <br><li> Cambiar a casco distinto → Engaño total <br><li> Cambio de matricula |
| Jugador MAX | Sistema de seguridad: Maximiza la detección del fraude|
| Jugador MIN | Ladrón: Minimiza la probabilidad de ser detectado por medio de estrategias|
| Estados terminales | <li> Ladrón detectado <br><li> Ladrón pasa desapercibido <br><li> Falso positivo (persona legitima bloqueada)|
| Decisión seleccionada | |
| Función de utilidad| - Fraude detectado → +100 <br> - Persona legitima permitida → +50 <br> - Resultado neutral/dudoso → 0 <br> - Falso positivo → -50 <br> - Fraude no detectado → -100 |
| Decisión Seleccionada | <li> MAX: verifica caracteristicas del casco <br><li> Ladron baraja entre las diferentes posibilidades <br><li> Utilidad esperada: +70

### PODA ALFA-BETA
Optimización que evita explorar ramas innecesarias sin alterar la decisión final; Consisite en ignorar ramas que prometen ser peores a la encontrada previamente, debido a esto las ramas sin potencial no se exploran al completo.

## Implementacion
### A*
**Archivo creado** → semana04_astar.py

El programa encuentra la secuencia mas optima de acciones para llegar a la meta; esto lo hace por medio del calculo de f(n) = g(n) + h(n). Donde, g(h) es el costo real gastado y h(n) es la estimación de costo restante, esto lo repite hasta alcanzar la meta. Dentro de las secuencias encontramos transformaciones del fotograma con tecnicas como: rotacion, ajuste de brillo, ajuste de contraste, reduccion de ruido y/o recorte. Con todo esto nos aseguramos que la mejor respuesta es encontrada primero

### Pruebas A*
El proyecto genera 3 casos de prueba en forma de menu de la siguiente forma:
1. Búsqueda normal (matrícula estándar)
2. Matrícula muy distorsionada (meta 95%)
3. Meta baja (meta 80%, más fácil)
La salida esperada es: Camino de transformaciones, nodos explorados, confianza final

### Minimax
**Archivo Creado** → semana04_minimax.py

Encuentra la mejor decisión cuando el enemigo actua inteligentemente. El sistema (MAX) elige que verificar del casco del conductor (color, daño, marca, etc).Ladrón (MIN) responde con mejor estrategia de engaño. Esto nos garantiza que si el ladron responte de manera efectiva, el sistema esta preparado.

### Pruebas Minimax 
El proyecto genera 3 casos de prueba en forma de menu de la siguiente forma:
1. Minimax completo (muestra árbol)
2. Minimax con poda α-β (optimizado)
3. Comparativa sin/con poda
Salida esperada: Árbol de decisión, utilidad, estrategia óptima, rankings