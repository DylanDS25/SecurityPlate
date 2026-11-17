# SecurityPlate
Proyecto para clase de Inteligencia Artificial

**Integrantes**
- Yeison Dario Ayala Beltran
- Dylan Leonardo Duitama Soriano

Consulta la [guía práctica de las semanas 7 a 11](guias/GUIA_PRACTICA_SEMANAS_07_11.md) para ver comandos, resultados y puntos clave de cada práctica.

Para repasar ingeniería del conocimiento y redes semánticas, usa la
[guía de estudio de las semanas 13 y 14](guias/GUIA_ESTUDIO_SEMANAS_13_14.md):
conceptos, reglas, trazas, ejercicios resueltos y autoevaluación.

Para la organización de bases de conocimiento empresarial y preparación de la sustentación oral, consulta la
[guía de estudio de la semana 15](guias/GUIA_ESTUDIO_SEMANA_15.md):
pirámide del conocimiento, modelo relacional, ciclo editorial, ejercicios y respuestas a las 10 preguntas obligatorias.

Para repasar la arquitectura de sistemas inteligentes y el motor de referencia, consulta la
[guía de estudio de la semana 16](guias/GUIA_ESTUDIO_SEMANA_16.md):
arquitectura de seis componentes, motor de referencia vs. inferencia, control de calidad, abstención y banco de preguntas de sustentación.

### Semana 16 - Diseño de sistemas inteligentes: Arquitectura y motor de referencia

Implementación de un motor de referencia determinista aplicado a SecurityPlate que recibe preguntas en lenguaje natural, normaliza el texto, busca en un catálogo estructurado de referencias técnicas y entrega respuestas basadas **exclusivamente en fuentes validadas**, acompañadas de su identificador y procedencia, absteniéndose formalmente ante falta de datos (`SIN_DATOS`) o falta de cobertura (`SIN_REFERENCIA`).

Arquitectura de seis componentes:
1. **Interfaz (`app.py`):** Captura de preguntas interactivas por consola o modo `--demo`.
2. **Normalizador (`motor_referencia.py`):** Limpieza con Unicode `NFD`, eliminación de tildes y extracción alfanumérica en minúsculas.
3. **Base de conocimiento (`base_conocimiento.py`):** Catálogo `REFERENCIAS` con metadatos (`id`, `titulo`, `claves`, `respuesta`, `fuente`, `validada`).
4. **Motor de referencia (`motor_referencia.py`):** Intersección de palabras clave, exclusión de borradores (`validada=False`) y ordenamiento determinista por coincidencias e ID.
5. **Generador de respuestas:** Respuesta textual fundamentada con trazabilidad (`id`, `fuente`, `coincidencias`).
6. **Control de calidad (`tests/test_motor.py`):** Gestión estricta de estados (`ENCONTRADA`, `SIN_REFERENCIA`, `SIN_DATOS`) y 7 pruebas unitarias automatizadas.

Entregables exactos:
- Base de conocimiento: `base_conocimiento.py`.
- Motor de referencia: `motor_referencia.py`.
- Interfaz interactiva y modo demo: `app.py`.
- Pruebas unitarias de calidad: `tests/test_motor.py`.
- Reporte académico completo: `reports/reporte_semana16.md`.
- Guía de estudio y sustentación: `guias/GUIA_ESTUDIO_SEMANA_16.md`.

Comandos de ejecución y sustentación:
```bash
# 1. Demostración interactiva (escribe preguntas o 'salir')
python app.py

# 2. Demostración automática de todos los escenarios (ENCONTRADA, exclusión, abstención, vacía)
python app.py --demo

# 3. Ejecución de las 7 pruebas unitarias automatizadas
python -m unittest discover -s tests -p "test_motor.py" -v
```

Puntos clave de sustentación:
- **Diferencia motor referencia vs. inferencia:** El motor de referencia (Semana 16) recupera conocimiento existente aprobado y cita su fuente; el motor de inferencia (Semana 13) deduce conclusiones nuevas aplicando reglas sobre hechos.
- **Abstención responsable:** Ante preguntas fuera de cobertura o borradores no aprobados, el sistema devuelve `SIN_REFERENCIA` y deriva a revisión humana, sin fabricar información.

### Semana 15 - Base de conocimiento empresarial aplicada a SecurityPlate

Implementación de un repositorio relacional estructurado en SQLite y Python para organizar, validar y consultar el conocimiento técnico y operativo de SecurityPlate. Modela dominios de conocimiento, aplicaciones del sistema, expertos responsables y herramientas de desarrollo.

Entregables exactos:
- Esquema relacional: `sql/esquema.sql`.
- Datos iniciales de SecurityPlate: `sql/datos.sql`.
- Lógica y demostración de ciclo de vida: `src/base_conocimiento.py`.
- Pruebas unitarias de integridad: `tests/test_base_conocimiento.py`.
- Reporte académico completo: `reports/reporte_semana15.md`.

Comandos de ejecución y sustentación:
```bash
# 1. Demostración interactiva (Registro en BORRADOR -> Validación -> Consulta publicada)
python src/base_conocimiento.py

# 2. Ejecución de las 7 pruebas unitarias automatizadas en entorno aislado
python -m unittest discover -s tests -p "test_base_conocimiento.py" -v
```

Puntos clave del modelo:
- **Dominios:** `Vision por Computador`, `Control de Acceso Vehicular`, `Auditoria y Trazabilidad`.
- **Aplicaciones:** `Modulo de Reconocimiento OCR`, `Detector de Calidad Visual`, `Motor de Inferencia y Reglas IPCS`, `Controlador de Barrera y Alertas`, `Consola de Auditoria y Evidencias`.
- **Expertos:** Yeison Ayala (Líder de Visión y CNN), Dylan Duitama (Sistemas Expertos y Protocolo IPCS), Carlos Rodriguez (Seguridad Física), Mariana Torres (Monitoreo Manual).
- **Herramientas:** PyTorch y Torchvision, OpenCV y Scikit-Image, SQLite, Motor de Reglas y Red Semántica, Unittest.
- **Regla editorial:** Nuevos artículos inician estrictamente como `BORRADOR`. Solo los artículos en estado `VALIDADO` son visibles mediante `buscar_articulos()`.
- **Integridad referencial:** Se activa `PRAGMA foreign_keys = ON;` en cada conexión, rechazando dominios o expertos no registrados (`sqlite3.IntegrityError`).

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
|15| Organización de Base de Conocimiento Empresarial <br> Implementación de una base de conocimiento estructurada y relacional en SQLite y Python aplicada a SecurityPlate. Se definieron los dominios *Visión por Computador*, *Control de Acceso Vehicular* y *Auditoría y Trazabilidad*, vinculando aplicaciones, expertos responsables, herramientas de desarrollo y artículos técnicos. Se implementó un ciclo editorial estricto (estado inicial BORRADOR que pasa a VALIDADO tras aprobación), consultas con SQL JOIN y 7 pruebas unitarias con unittest para validar integridad referencial y gobernanza del conocimiento.|
|16| Arquitectura de Sistemas Inteligentes y Motor de Referencia <br> Implementación de una arquitectura de seis componentes (interfaz, normalizador, base de conocimiento, motor de referencia, generador de respuestas y control de calidad) en Python estándar. El motor recupera referencias aprobadas de SecurityPlate a partir de palabras clave normalizadas, garantizando trazabilidad de fuentes (`id`, `fuente`, `coincidencias`), exclusión de borradores no validados y abstención formal (`SIN_REFERENCIA` / `SIN_DATOS`) para evitar la invención de respuestas.|
