# Semana 04 - Marco tecnológico de la inteligencia artificial
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

---


## Resultado

Los resultados obtenidos se consideran correctos y razonables porque corresponden al comportamiento esperado de los algoritmos utilizados.

En el caso de **A***, se observa que cuando la meta es más sencilla, como en el caso del 80%, el algoritmo encuentra rápidamente una solución y necesita explorar pocos nodos. Al aumentar la dificultad a una meta del 90%, debe analizar muchas más posibilidades antes de encontrar el camino. Finalmente, con una meta del 95% y una confianza inicial menor, no logra encontrar una solución dentro del tiempo establecido. Esto demuestra que los resultados tienen relación directa con la dificultad del problema y con el tamaño del espacio de búsqueda.

En **Minimax**, el resultado de **-75.0** es razonable porque el algoritmo está considerando un escenario donde el posible infractor también toma decisiones para evitar ser detectado. Por esta razón, aunque el sistema selecciona la mejor estrategia disponible, no siempre puede garantizar la detección cuando se analiza una sola característica.

Además, la comparación con **poda alfa-beta** mantiene la misma decisión final, lo cual es coherente, ya que su función es reducir el número de ramas que se revisan y no cambiar la decisión tomada por Minimax.

En general, las pruebas permiten comprobar que los algoritmos están respondiendo de acuerdo con el problema planteado. También muestran una limitación importante: los resultados dependen de las condiciones iniciales, la meta establecida y la cantidad de información que se utilice para tomar la decisión. Por esto, para llevar el proyecto a un entorno real sería necesario realizar más pruebas con diferentes imágenes, condiciones de iluminación y características de los conductores.

## Analisis

### Ventajas

Una de las principales ventajas de **A*** es que permite buscar una solución teniendo en cuenta tanto el costo acumulado como una estimación de lo que falta para llegar a la meta. En nuestro proyecto esto permite buscar una combinación de transformaciones para mejorar la lectura de la matrícula sin probar todas las posibilidades de la misma manera.

En el caso de **Minimax**, la ventaja es que permite analizar situaciones en las que existe un posible intento de engaño. El sistema no solamente toma una decisión, sino que también considera cómo podría responder el posible infractor.

### Limitaciones

La principal limitación encontrada en A* es que, cuando el problema aumenta de dificultad, la cantidad de estados que debe explorar puede crecer considerablemente. Esto se evidenció en la prueba con una meta del 95%, donde el algoritmo superó los 772.822 nodos explorados y terminó por tiempo de espera.

En Minimax, una limitación importante es que el resultado depende de las características que se decidan analizar. Si solamente se utiliza una característica del casco, una persona podría modificarla o imitarla y dificultar la detección.

### Supuestos

Para las pruebas asumimos que cada transformación de la imagen tiene un costo definido y que la confianza del OCR aumenta de acuerdo con la transformación aplicada. También asumimos que el posible infractor actúa de manera inteligente y busca la forma de evitar ser detectado.

Estos supuestos permiten realizar la demostración, pero representan una simplificación del comportamiento que tendría el sistema en un entorno real.

### Posibles mejoras

Como mejora para **A***, se podría utilizar una heurística más precisa y limitar las transformaciones poco útiles para reducir el número de nodos explorados.

Para **Minimax**, sería conveniente combinar varias características del conductor en lugar de depender solamente del casco. Por ejemplo, se podría considerar conjuntamente la matrícula, color y tipo de casco, vestimenta y otras características visuales.

En general, los resultados muestran que los algoritmos funcionan para el escenario planteado, pero también dejan claro que todavía se necesita realizar pruebas con datos e imágenes reales antes de considerar el sistema como una solución definitiva.

## Resultados de Ejecución y Pruebas

### A* - Normalización de Matrícula

Ejecutamos tres escenarios diferentes para ver cómo el algoritmo se comporta bajo distintas dificultades:

**Caso 1: Búsqueda Normal (Meta: 90%)**
- Partimos con una matrícula con 45% de confianza
- Meta: llegar a 90%
- Resultado: Éxito en menos de 1 segundo
- Nodos explorados: 9,360
- Camino: 7 transformaciones (denoise, brillo, contraste, dos rotaciones, brillo nuevamente)
- Costo final: 7.0 unidades

Lo interesante aquí es que A* fue inteligente: primero aplicó denoise (caro pero muy efectivo: +25% confianza), luego combinó ajustes de brillo, contraste y rotaciones. No fue ciega ni se fue por la ruta más obvia, sino que buscó la más económica.

**Caso 2: Matrícula Muy Distorsionada (Meta: 95%)**
- Partimos con solo 35% de confianza (peor estado inicial)
- Meta: 95% (más exigente que Caso 1)
- Resultado: No encontró solución (timeout a los 120 segundos)
- Nodos explorados: 772,822+ (¡82 veces más que Caso 1!)

Este es el descubrimiento más valioso de todos. A* es matemáticamente óptimo, pero no es mágico. Cuando el problema se vuelve lo suficientemente difícil, la explosión combinatoria del espacio de búsqueda hace que sea intratabilidad computacional. Cada punto porcentual adicional de distancia requiere exponencialmente más nodos a explorar.

**Caso 3: Meta Modesta (Meta: 80%)**
- Partimos con 45% (igual que Caso 1)
- Meta: 80% (más fácil que Caso 1)
- Resultado: Éxito instantáneo
- Nodos explorados: solo 19 (495 veces más rápido que Caso 1)
- Camino: 4 pasos (denoise, dos rotaciones)
- Costo: 4.0 unidades

Aquí A* fue eficiente. Como la meta es más baja, no "desperdició" recursos en ajustes finos de brillo y contraste. Denoise + rotaciones bastaron.

**Lo que aprendemos:** La complejidad no es lineal. Cambiar la meta de 90% a 95% no es solo un 5% más difícil; es 8,200% más difícil. Es como la diferencia entre un crucigrama y un cubo de Rubik.

---

### Minimax - Detección de Fraude en Cascos

Evaluamos un sistema de seguridad (MAX) que trata de detectar si alguien cambió de casco, un ladrón inteligente (MIN) que intenta engañar. El sistema solo puede verificar una característica del casco.

**Los 3 casos convergieron al mismo resultado: -75.0 de utilidad**

Esto significa: "incluso si el sistema actúa de manera óptima, el ladrón inteligente tiene ventaja". Sonaría desalentador, pero en realidad es realista. ¿Por qué negativo? Porque el ladrón tiene respuestas para todo:

- Si verificamos COLOR → el ladrón pinta el casco (muy fácil)
- Si verificamos MARCA → lo cubre con una pegatina
- Si verificamos DAÑOS → usa un casco completamente nuevo
- Si verificamos TIPO → es relativamente fácil de cambiar

El ranking final fue: **TIPO de casco es lo mejor que puede verificar** (utilidad -75), pero sigue siendo insuficiente.

**La poda alfa-beta funcionó perfectamente:** Sin poda (exploración completa) llegó a -75.0. Con poda (más eficiente) también llegó a -75.0. La poda es una optimización que no sacrifica la decisión final, solo hace que sea más rápida. Es como tomar un atajo sin perderse.

---

## Conclusión: ¿Qué Significan Estos Resultados?

**A* nos enseña:** Los algoritmos óptimos son poderosos, pero tiene límites. A veces el problema es tan intrínsecamente difícil que ni la optimalidad nos puede salvar del tiempo computacional. Es como un examen imposible: ser inteligente ayuda, pero si el tiempo se acaba, no importa.

**Minimax nos enseña:** En juegos donde el adversario es tan inteligente como nosotros, a veces lo mejor que podemos hacer es "perder menos". No hay estrategia defensiva perfecta contra un enemigo que conoce todas nuestras opciones. Necesitaríamos información adicional o múltiples capas de verificación.

**En la práctica:** 
- Para normalizar matrículas: Funciona bien si la meta es razonable (80-90%), pero pide lo imposible si quieres 95% desde una imagen muy distorsionada
- Para detectar fraude: Verificar una sola característica no es suficiente; necesitamos combinar múltiples verificaciones
