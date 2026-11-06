# SecurityPlate
Proyecto para clase de Inteligencia Artificial

**Integrantes**
- Yeison Dario Ayala Beltran
- Dylan Leonardo Duitama Soriano

Consulta la [guía práctica de las semanas 7 a 11](guias/GUIA_PRACTICA_SEMANAS_07_11.md) para ver comandos, resultados y puntos clave de cada práctica.

### Semana 14 - redes semanticas aplicadas a SecurityPlate

Ejecuta `python main.py` para interpretar frases simples, recorrer la jerarquia
`placa_moto -> placa -> identificador_vehicular -> dato_verificacion` y
evaluar los cinco casos de `data/casos_semana07.csv`.

El concepto principal combina una moto, su placa, una foto adecuada, una
comparacion y un resultado visual. Una foto alcanza calidad suficiente con
`calidad_imagen >= 0.80`. La red infiere autorizacion solo cuando coinciden
placa, conductor, registro y protocolo `IPCS`; de lo contrario devuelve
verificacion manual.

Entregables exactos:
- Red semantica: `src/red_semantica.py`.
- Demostracion: `main.py`.
- Pruebas exactas: `tests/test_red_semantica.py`.
- Integracion SecurityPlate: `src/semana14_redes_semanticas.py`.
- Evidencia JSON: `artifacts/semana14_red_semantica.json`.
- Reporte: `reports/reporte_semana14.md`.

Prueba solo esta practica con
`.venv\Scripts\python.exe -m unittest discover -s tests -p "test_red_semantica.py" -v`
y con `test_semana14.py`.

Conceptos principales: `moto`, `vehiculo`, `placa`, `foto_placa`,
`comparacion_placa`, `resultado_visual`, `personal_seguridad` y
`verificacion_manual`.

Relaciones importantes:
- `(moto, tiene, placa)`.
- `(placa, requiere, foto_placa)`.
- `(placa, corresponde_a, moto)`.
- `(foto_placa, habilita, comparacion_placa)`.
- `(placa_moto, es_un, placa)`.
- `(comparacion_placa, requiere_revision, verificacion_manual)`.

La transitividad se aplica solo a `es_un`. Otras relaciones no se interpretan
como herencia automatica. El parser reconoce frases simples; una oracion fuera
de los patrones produce un `ValueError`. Una consulta sin evidencia no demuestra
una negacion universal, solamente indica que falta informacion para inferir.

### Semana 13 - ingenieria del conocimiento aplicada a la salida

Ejecuta `python src/semana13_conocimiento.py` desde la raiz para cargar los cinco casos de `data/casos_semana07.csv`, aplicar las siete reglas de inferencia y generar `artifacts/semana13_inferencia.json` junto con los reportes `reports/semana13.md` y `reports/reporte_semana13.md`.

Entregables exactos:
- Motor independiente: `src/motor_inferencia.py`.
- Pruebas unittest: `tests/test_motor_inferencia.py`.
- Reporte académico completo: `reports/reporte_semana13.md`.
- La evidencia, reglas y casos se muestran además en `artifacts/semana13_inferencia.json`.

Prueba el motor con `.venv\Scripts\python.exe -m unittest discover -s tests -p "test_motor_inferencia.py" -v`. El programa demuestra dos casos, sus hechos iniciales, trazas y conclusiones.

La Semana 13 se consulta desde el dashboard general, dentro de la sección `Semana 13`, junto con sus reglas, trazas y decisiones. También puede ejecutarse `python src/semana13_conocimiento.py --serve` para generar la evidencia y el reporte, sin depender de un dashboard separado.

### Semana 11 - benchmark de caracteres

Ejecuta `python src/semana11_benchmark.py` desde la raiz para comparar Logistic Regression, Random Forest y MLP sobre los recortes de caracteres anotados de `data/dataset`, usando las particiones oficiales `train` y `test`. El benchmark corre tres veces por modelo y genera `artifacts/benchmark.csv` y `reports/semana11_adr.md`. Se puede aumentar el numero de repeticiones con `--repeats`; no se aceptan menos de tres.

### Semana 09 - vision de placas

El modulo procesa `data/imagen_proyecto.png` con Canny, umbral de Otsu y regiones conectadas. Ejecuta `python src/semana09_vision.py` para regenerar la evidencia `artifacts/semana09_vision.png` y el informe `reports/semana09.md`. Para generar los entregables y abrir la interfaz de carga interactiva en el puerto 8000, ejecuta `python src/semana09_vision.py --serve` y visita `http://127.0.0.1:8000/dashboard/`.

### Semana 10 - segmentacion y texturas de placas

El modulo `src/semana10_texturas.py` procesa dos imagenes etiquetadas de placas del conjunto de prueba: calcula histogramas de intensidad, umbral Otsu, regiones conectadas y descriptores LBP. Desde la raiz del repositorio, ejecuta `python src/semana10_texturas.py` para regenerar `artifacts/semana10_features.npy`, `artifacts/semana10_histograma.png` y `reports/semana10.md`. Para comparar temporalmente entre 2 y 4 imagenes propias desde el dashboard, ejecuta `python src/semana09_vision.py --serve` y visita `http://127.0.0.1:8000/dashboard/`; las cargas se procesan en memoria, tienen un limite total de 20 MB y no reemplazan los entregables. Los archivos de imagen del conjunto se distribuyen bajo licencia CC BY 4.0; la fuente y atribucion se indican en el informe.

### Evidencia

|Semana|Descripción|
|---|---|
|2| Resumen de lo realizado <br> Durante esta semana comenzamos a conocer los fundamentos de la Inteligencia Artificial y a entender cómo estos conceptos se pueden aplicar a nuestro proyecto de **reconocimiento de placas vehiculares**.\nPrimero vimos qué es la Inteligencia Artificial y entendimos que no se trata solamente de crear o entrenar un modelo, sino de combinar diferentes elementos como los datos, los algoritmos, el aprendizaje y la toma de decisiones. También conocimos un poco sobre la evolución de la IA y hacia dónde se dirige actualmente.<br> Después empezamos a organizar la base de nuestro proyecto. Configuramos el entorno de trabajo utilizando **Python, Visual Studio Code y Git**, y planteamos una estructura de carpetas que nos permitirá ir agregando los diferentes componentes del proyecto a medida que avance el semestre. <br> Como parte de la práctica, trabajamos con un primer modelo de aprendizaje automático utilizando **Scikit-learn**. El objetivo fue entender de manera práctica cómo se prepara la información, cómo se entrena un modelo y cómo podemos comprobar qué tan bien funciona mediante el *accuracy* y la matriz de confusión. <br> Aunque este primer ejercicio utiliza un conjunto de datos de ejemplo, nos sirve como punto de partida para nuestro proyecto. La idea es que, en el transcurso de la semana, podamos reemplazar estos ejemplos por nuestros propios datos de **placas vehiculares** y comenzar a incorporar el procesamiento de imágenes y el reconocimiento de caracteres. <br> En conclusión, esta semana nos permitió **sentar las bases del proyecto**, tanto en la parte conceptual como en la parte práctica. También entendimos que el proyecto se va a desarrollar paso a paso y que cada semana iremos agregando nuevos componentes hasta llegar a nuestro sistema inteligente de reconocimiento de placas.|
|3| En esta semana seguimos dando forma a nuestro proyecto de Inteligencia Artificial, que busca crear un sistema inteligente para controlar el ingreso y salida de vehículos en un parqueadero. <br> Lo primero que aprendimos es que antes de elegir una técnica de IA, debemos entender bien el tipo de problema que queremos resolver. Esto nos llevó a explorar varias áreas:<br>- Machine Learning y Deep Learning, útiles para entrenar modelos que reconozcan patrones.<br>- Visión por computador, clave en nuestro caso porque trabajaremos con imágenes de placas y conductores.<br>- Sistemas expertos y reglas de decisión, que nos ayudan a definir qué hacer cuando hay coincidencias o discrepancias.<br>- Representación del conocimiento y búsqueda y planificación, que aportan estructura y estrategias de validación.<br>**Cómo funcionará el sistema**<br>*Ingreso:* se captura la placa y una imagen del conductor como referencia.<br>*Salida:* se vuelve a capturar la información y se compara con el registro inicial.<br>*Decisión:* si todo coincide, se autoriza la salida; si no, se bloquea y se genera una alerta para revisión manual.<br>**Arquitectura del proyecto**<br>Nuestro sistema no dependerá de una sola técnica, sino que será un Sistema Inteligente Híbrido. Esto significa que combinará:<br>- Visión por computador para el reconocimiento visual.<br>- Modelos de aprendizaje automático para verificar coincidencias.<br>- Reglas de decisión para manejar excepciones y alertas. <br> La práctica nos mostró la importancia de la taxonomía de la IA: clasificar problemas y usar palabras clave para identificar qué técnicas aplicar. Gracias a esto, ahora tenemos más claro qué componentes debemos desarrollar en las próximas semanas.|
