# Semana 15 - Organización de Base de Conocimiento Empresarial aplicada a SecurityPlate

## 1. Información General y Objetivos
- **Asignatura:** Inteligencia Artificial · Ingeniería de Sistemas · Décimo Semestre.
- **Proyecto:** SecurityPlate — Sistema Inteligente de Control de Acceso y Reconocimiento de Placas Vehiculares.
- **Integrantes:** Yeison Dario Ayala Beltran, Dylan Leonardo Duitama Soriano.
- **Tema Sílabo:** Semana 15: Organización de bases de conocimiento en la empresa, dominios, aplicaciones, recursos humanos y herramientas de desarrollo.

### Objetivo de la Práctica
Diseñar e implementar un repositorio estructurado de conocimiento organizacional para **SecurityPlate**, organizando el conocimiento técnico y procedimental mediante:
1. **Dominios de conocimiento** específicos del problema vehicular y visión artificial.
2. **Aplicaciones y sistemas** donde se explota y aplica dicho saber.
3. **Recursos humanos y expertos** responsables de la auditoría y calidad del contenido.
4. **Herramientas de desarrollo y soporte** involucradas en el ciclo de vida.
5. **Mecanismo editorial estricto:** los nuevos artículos inician como `BORRADOR` y únicamente pueden ser consultados tras la aprobación a estado `VALIDADO`.

---

## 2. Modelado de la Base de Conocimiento en SecurityPlate

A diferencia del ejemplo pedagógico genérico de clase (Seguridad / Soporte TI), en **SecurityPlate** el conocimiento se modeló a partir de las arquitecturas desarrolladas durante el semestre (Visión por Computador, Redes Convolucionales, Inferencia por Reglas IPCS, Auditoría de Evidencias y Redes Semánticas):

### A. Dominios de Conocimiento (`dominio`)
1. **`Vision por Computador`:** Concentra el saber sobre procesamiento de imágenes, filtros digitales (Otsu, Canny, LBP), extracción de características y redes neuronales convolucionales (CNN) para caracteres de placas vehiculares.
2. **`Control de Acceso Vehicular`:** Regula la lógica del negocio, correspondencia de placa e ingreso, verificación de identidad del conductor y evaluación secuencial del protocolo `IPCS`.
3. **`Auditoria y Trazabilidad`:** Gestiona el registro histórico de evidencias, resguardo de capturas fotográficas, logs transaccionales y auditoría forense ante incidentes.

### B. Aplicaciones y Subsistemas (`aplicacion`)
1. **`Modulo de Reconocimiento OCR`** (pertenece a *Visión por Computador*): Inferencia del modelo CNN sobre recortes 32x32 de caracteres de placa.
2. **`Detector de Calidad Visual`** (pertenece a *Visión por Computador*): Algoritmo de descarte de imágenes desenfocadas, oscuras o de baja calidad previa al OCR.
3. **`Motor de Inferencia y Reglas IPCS`** (pertenece a *Control de Acceso Vehicular*): Sistema experto basado en reglas encadenadas (R1 a R7) que evalúa si una salida es admisible.
4. **`Controlador de Barrera y Alertas`** (pertenece a *Control de Acceso Vehicular*): Interfaz con hardware de acceso físico y disparo de avisos sonoros/visuales en cabina.
5. **`Consola de Auditoria y Evidencias`** (pertenece a *Auditoría y Trazabilidad*): Interfaz de consulta de registros históricos y evidencias SQLite.

### C. Expertos Responsables (`experto`)
1. **`Yeison Ayala`** — *Líder de Visión y Modelos CNN*: Valida arquitecturas de red, matrices de confusión y preprocesamiento de imágenes.
2. **`Dylan Duitama`** — *Especialista en Sistemas Expertos y Protocolo IPCS*: Valida reglas de inferencia, autómatas finitos y diagramas de decisión.
3. **`Carlos Rodriguez`** — *Oficial de Seguridad Física y Control de Acceso*: Revisa protocolos de contingencia y operación de barreras vehiculares.
4. **`Mariana Torres`** — *Operadora de Monitoreo y Verificación Manual*: Evalúa procedimientos de inspección presencial y resolución de alertas.

### D. Herramientas de Desarrollo y Soporte (`herramienta`)
1. **`PyTorch y Torchvision`**: Framework de aprendizaje profundo para entrenamiento e inferencia de la CNN de caracteres.
2. **`OpenCV y Scikit-Image`**: Librerías de preprocesamiento, detección de bordes Canny, umbralización Otsu y descriptores de textura LBP.
3. **`SQLite y Motor Relacional`**: Persistencia relacional local de evidencias fotográficas, metadatos y repositorio de conocimiento.
4. **`Motor de Reglas y Red Semántica`**: Motor de punto fijo para encadenamiento hacia adelante y ontología GraphML.
5. **`Unittest de Python`**: Framework de pruebas automatizadas para verificación de integridad referencial y cobertura funcional.

### E. Artículos Iniciales y Trazabilidad (`articulo`)
| ID | Título | Dominio | Aplicación | Experto Responsable | Fuente | Estado |
|:--:|:---|:---|:---|:---|:---|:--:|
| 1 | Procedimiento de captura y preprocesamiento de placas | Visión por Computador | Módulo de Reconocimiento OCR | Yeison Ayala | Manual de Percepción Visual v2.1 | **VALIDADO** |
| 2 | Umbrales de calidad de imagen y confianza de lectura | Visión por Computador | Detector de Calidad Visual | Yeison Ayala | Especificación Técnica Semanas 08-10 | **VALIDADO** |
| 3 | Protocolo de autorización de salida mediante secuencia IPCS | Control de Acceso Vehicular | Motor de Inferencia y Reglas IPCS | Dylan Duitama | Reglas de Inferencia R1-R7 Semana 13 | **VALIDADO** |
| 4 | Procedimiento de contingencia y derivación a revisión manual | Control de Acceso Vehicular | Controlador de Barrera y Alertas | Dylan Duitama | Guía de Operaciones en Cabina | **BORRADOR** |
| 5 | Política de auditoría y resguardo de evidencia fotográfica | Auditoría y Trazabilidad | Consola de Auditoría y Evidencias | Carlos Rodriguez | Política Corporativa de Seguridad Física | **BORRADOR** |

---

## 3. Modelo Relacional y Restricciones de Integridad

El esquema (`sql/esquema.sql`) implementa las cinco entidades requeridas con claves primarias (`id INTEGER PRIMARY KEY`), claves foráneas (`REFERENCES`) y restricciones avanzadas:

```text
  dominio (1) ──────────< (N) aplicacion
     │
     └──────────────────< (N) articulo (N) >────────── (1) experto
                                 │
                                 ├── (0..1) aplicacion
                                 └── (0..1) herramienta
```

### Reglas de Integridad en SQLite:
1. **Activación de Claves Foráneas:** Se ejecuta obligatoriamente `PRAGMA foreign_keys = ON;` al abrir cada conexión transaccional. Esto impide asociar un artículo a un `dominio_id` o `experto_id` inexistente.
2. **Restricción de Estado Editorial:** `CHECK (estado IN ('BORRADOR', 'VALIDADO'))` garantiza que ningún registro almacene estados arbitrarios.
3. **Unicidad de Título en Dominio:** `UNIQUE (titulo, dominio_id)` evita la duplicación accidental de procedimientos dentro de una misma área de conocimiento.
4. **Optimización de Consulta:** Se crea el índice compuesto `idx_articulo_dominio_estado ON articulo(dominio_id, estado)` para acelerar la recuperación de artículos aprobados.

---

## 4. Ciclo de Vida Editorial y Reglas de Negocio

El módulo `src/base_conocimiento.py` implementa el ciclo de vida del conocimiento:
1. **Registro Obligatorio como Borrador:** Toda llamada a `registrar_articulo(...)` inserta el registro con estado fijo `'BORRADOR'` y la fecha actual en formato ISO.
2. **Validación de Parámetros:** Exige que `titulo`, `contenido` y `fuente` no estén vacíos ni formados exclusivamente por espacios en blanco (`ValueError`).
3. **Consulta Restringida (Publicación Segura):** La función `buscar_articulos(dominio)` aplica un `JOIN` entre `articulo`, `dominio` y `experto` con la condición estricta:
   ```sql
   WHERE d.nombre = ? AND a.estado = 'VALIDADO'
   ```
   Esto asegura que los borradores no sean visibles en la consulta pública ni se tomen como instrucciones aprobadas.
4. **Aprobación Formal:** `validar_articulo(articulo_id)` realiza la transición editorial actualizando el estado a `'VALIDADO'`.

---

## 5. Pruebas Unitarias Automatizadas (`tests/test_base_conocimiento.py`)

Se implementaron **7 pruebas unitarias** utilizando `unittest` y bases de datos aisladas en memoria/directorios temporales (`tempfile.TemporaryDirectory`):

| Nombre de la Prueba | Condición Evaluada | Resultado |
|---|---|:---:|
| `test_solo_articulos_validados` | Verifica que la búsqueda devuelva únicamente artículos en estado `VALIDADO` y que dominios con solo borradores retornen 0 resultados. | **OK** |
| `test_ciclo_registro_validacion` | Verifica que un artículo nuevo nazca en `BORRADOR`, permanezca oculto en la consulta pública, y pase a ser visible inmediatamente tras invocar `validar_articulo()`. | **OK** |
| `test_dato_obligatorio` | Verifica que títulos, contenidos o fuentes vacías o con espacios lancen `ValueError`. | **OK** |
| `test_referencia_dominio_inexistente` | Verifica que asociar un artículo a un `dominio_id=999` dispare `sqlite3.IntegrityError` por fallo de clave foránea. | **OK** |
| `test_referencia_experto_inexistente` | Verifica que asociar un artículo a un `experto_id=888` dispare `sqlite3.IntegrityError`. | **OK** |
| `test_id_no_existente_al_validar` | Verifica que intentar validar un artículo con ID inexistente lance `ValueError`. | **OK** |
| `test_titulo_duplicado_en_mismo_dominio` | Verifica que duplicar el título dentro del mismo dominio viole la restricción `UNIQUE` (`IntegrityError`). | **OK** |

**Resultado de la ejecución:**
```text
Ran 7 tests in 0.670s

OK
Was successful: True, tests run: 7, errors: 0, failures: 0
```

---

## 6. Demostración para Sustentación Obligatoria

Al ejecutar `python src/base_conocimiento.py`, el sistema ejecuta y evidencia de forma interactiva los cinco pasos exigidos:
1. **Inicialización:** Creación del esquema y carga de datos iniciales en `data/conocimiento.db`.
2. **Consulta Inicial:** Muestra los artículos validados en el dominio *Visión por Computador*.
3. **Registro de un Artículo:** Se registra *"Guía de calibración de sensores de barrera"* en el dominio *Control de Acceso Vehicular*.
4. **Comprobación de Estado Inicial:** Se verifica que su estado sea estrictamente `'BORRADOR'` y se demuestra mediante consulta que **no aparece** en la búsqueda de artículos validados.
5. **Validación del Artículo:** Se aprueba formalmente el artículo mediante `validar_articulo()`.
6. **Consulta del Artículo Publicado:** Se vuelve a consultar el dominio y se comprueba que ahora sí aparece en el listado público con su experto responsable y fuente.

---

## 7. Preguntas para la Sustentación con Respuestas Técnicas

1. **¿Qué distingue una base de conocimiento de una base de datos?**  
   *Respuesta:* Una base de datos es un medio tecnológico de persistencia y relaciones; una base de conocimiento es un conjunto organizado de saber organizacional contextualizado, con responsables identificables, fuentes verificables y gobernanza editorial sobre su vigencia y validez.
2. **¿Qué es un dominio de conocimiento?**  
   *Respuesta:* Es un área temática o funcional estable que delimita un conjunto de conceptos, problemas y prácticas (ej. *Visión por Computador* vs. *Control de Acceso Vehicular*).
3. **¿Por qué se relaciona un artículo con un experto?**  
   *Respuesta:* Para asegurar rendición de cuentas, trazabilidad y gobernanza: cada artículo tiene un autor o revisor humano con cargo específico encargado de avalar su exactitud técnica.
4. **¿Qué son las aplicaciones en este modelo?**  
   *Respuesta:* Son los subsistemas de software o procesos operativos donde el conocimiento se pone en práctica (ej. el *Módulo de Reconocimiento OCR* o el *Motor de Reglas IPCS*).
5. **¿Para qué se registran las herramientas?**  
   *Respuesta:* Para identificar los medios tecnológicos (librerías como PyTorch o SQLite) usados para implementar, capturar o ejecutar los procedimientos descritos.
6. **¿Por qué la consulta filtra obligatoriamente por `VALIDADO`?**  
   *Respuesta:* Para evitar que notas en borrador, procedimientos no probados o directrices en revisión se distribuyan o ejecuten como políticas oficiales de seguridad.
7. **¿Por qué `WHERE d.nombre = ?` es mejor que concatenar cadenas SQL?**  
   *Respuesta:* Porque utiliza sentencias preparadas parametrizadas por el motor SQLite, separando el código SQL de los datos y mitigando vulnerabilidades de inyección SQL.
8. **¿Qué ocurre si se registra `dominio_id = 999` y no existe?**  
   *Respuesta:* Al estar activada la directiva `PRAGMA foreign_keys = ON;`, SQLite rechaza la transacción y lanza un error de integridad referencial (`sqlite3.IntegrityError`).
9. **¿Qué demuestra la prueba del ciclo de vida editorial?**  
   *Respuesta:* Demuestra que ningún artículo nuevo se hace público de forma inmediata, comprobando que nace como `BORRADOR` y que únicamente es visible tras su validación explícita.
10. **¿Este programa implementa razonamiento semántico o IA por sí solo?**  
    *Respuesta:* No; es una estructura relacional de ingeniería de conocimiento y gobernanza organizacional, que sirve como insumo de verdad fundamentada para alimentar motores de inferencia, agentes o sistemas híbridos.
