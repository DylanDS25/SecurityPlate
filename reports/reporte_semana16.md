# Semana 16 - Diseño de Sistemas Inteligentes: Arquitectura y Motor de Referencia en SecurityPlate

## 1. Información General y Objetivos
- **Asignatura:** Inteligencia Artificial · Ingeniería de Sistemas · Décimo Semestre.
- **Proyecto:** SecurityPlate — Sistema Inteligente de Control de Acceso y Reconocimiento de Placas Vehiculares.
- **Integrantes:** Yeison Dario Ayala Beltran, Dylan Leonardo Duitama Soriano.
- **Tema del Sílabo:** Semana 16: Diseño de sistemas inteligentes – Arquitectura de sistemas inteligentes y motor de referencia.

### Objetivo de la Práctica
Diseñar e implementar un motor de referencia determinista aplicado a **SecurityPlate**, capaz de recibir preguntas en lenguaje natural, normalizarlas, consultar una base de conocimiento estructurada y devolver respuestas basadas **exclusivamente en fuentes validadas**, acompañadas de su identificador y trazabilidad de procedencia, absteniéndose formalmente cuando la información no esté aprobada o se encuentre fuera de cobertura.

---

## 2. Arquitectura del Sistema Inteligente (Seis Componentes)

El sistema implementa una arquitectura modular coordinada donde cada componente tiene una responsabilidad bien delimitada:

```text
  [ Usuario / Operador de Seguridad ]
                  │
                  ▼ (1)
       ┌───────────────────────┐
       │   Interfaz (app.py)   │  <-- Captura de consulta por consola
       └───────────────────────┘
                  │
                  ▼ (2)
       ┌───────────────────────┐
       │      Normalizador     │  <-- casefold(), NFD, eliminación de acentos,
       │ (motor_referencia.py) │      extracción de tokens alfanuméricos
       └───────────────────────┘
                  │  (palabras normalizadas: set[str])
                  ▼ (3)
       ┌───────────────────────┐         ┌─────────────────────────┐
       │  Motor de Referencia  │ <-----> │  Base de Conocimiento   │
       │ (motor_referencia.py) │         │ (base_conocimiento.py)  │
       └───────────────────────┘         │ REFERENCIAS validadas   │
                  │                      │ y borradores de control │
                  ▼ (4)                  └─────────────────────────┘
       ┌───────────────────────┐
       │ Generador de Respuesta│  <-- Selección de candidato con mayor
       │ (motor_referencia.py) │      puntuación + ensamblado de metadatos
       └───────────────────────┘
                  │  (resultado: dict)
                  ▼ (5)
       ┌───────────────────────┐
       │   Control de Calidad  │  <-- Gestión de estados: ENCONTRADA,
       │  (test_motor.py)      │      SIN_REFERENCIA, SIN_DATOS
       └───────────────────────┘
                  │
                  ▼ (6)
  [ Salida Formateada con Trazabilidad (ID + Fuente) ]
```

### Relación entre los 6 componentes:
1. **Interfaz de usuario (`app.py`):** Captura la pregunta formulada por el usuario en texto libre y entrega la salida formateada o mensajes de control.
2. **Normalizador de texto (`normalizar` en `motor_referencia.py`):** Convierte el texto a minúsculas, descompone acentos Unicode (`NFD`), retira marcas no espaciadas (`Mn`) y extrae palabras alfanuméricas únicas en un conjunto (`set[str]`).
3. **Base de conocimiento (`base_conocimiento.py`):** Colección estructurada de referencias que contienen ID único, título, palabras clave, respuesta oficial, procedencia formal y estado de validación booleano (`validada: True/False`).
4. **Motor de referencia (`consultar` en `motor_referencia.py`):** Filtra referencias no validadas, calcula la intersección de palabras clave, puntúa candidatos por número de coincidencias y selecciona la referencia óptima.
5. **Generador de respuestas:** Extrae el mensaje prealmacenado del registro seleccionado y le adjunta el identificador y la fuente para su verificación externa.
6. **Control de calidad (`test_motor.py` y manejo de abstención):** Maneja los estados `ENCONTRADA`, `SIN_REFERENCIA` y `SIN_DATOS`, evitando categóricamente fabricar o inventar respuestas cuando falta evidencia.

---

## 3. Diferencia Fundamental: Motor de Referencia vs. Motor de Inferencia

| Criterio | Motor de Referencia (Semana 16) | Motor de Inferencia (Semana 13) |
|---|---|---|
| **Propósito** | Buscar, puntuar y recuperar información preexistente y verificada con su origen. | Deducir hechos nuevos y conclusiones a partir de reglas lógicas. |
| **Entrada** | Pregunta en lenguaje natural del usuario (`"¿Cómo se captura la placa?"`). | Conjunto de hechos iniciales observados (`{placa_coincide, conductor_coincide, ...}`). |
| **Mecanismo** | Intersección de palabras clave normalizadas y ordenamiento determinista. | Encadenamiento hacia adelante (*forward chaining*) hasta alcanzar punto fijo. |
| **Lógica subyacente** | Coincidencia léxica y recuperación de fuentes aprobadas. | Implicaciones formales $P_1 \land P_2 \dots \land P_n \to C$. |
| **Salida** | Texto almacenado + Identificador + Fuente bibliográfica. | Nuevos hechos deducidos + Decisión simbólica (`autorizar_salida`). |
| **Creatividad / Deducción** | **Cero**: No deduce información nueva ni altera los textos guardados. | **Deductiva**: Genera conclusiones que no estaban explícitas inicialmente. |

---

## 4. Estructura de las Referencias de SecurityPlate

A diferencia del ejemplo de aula sobre matrícula universitaria, las referencias corresponden al sistema **SecurityPlate**:

| ID | Título | Palabras Clave | Fuente Formal | Estado |
|:--:|:---|:---|:---|:---:|
| `REF-SEC-001` | Captura y preprocesamiento de placas vehiculares | captura, camara, preprocesamiento, filtro, placa, otsu, canny, recorte | Manual de Percepción Visual SecurityPlate v2.1 | **VALIDADA** |
| `REF-SEC-002` | Criterios de umbral para calidad de imagen y confianza OCR | umbral, calidad, confianza, ocr, imagen, iluminacion, desenfoque | Especificación Técnica de Umbrales Semanas 08-10 | **VALIDADA** |
| `REF-SEC-003` | Protocolo de autorización de salida vehicular IPCS | autorizacion, salida, protocolo, ipcs, secuencia, conductor, coincidencia, ingreso | Reglas de Inferencia R1-R7 Semana 13 | **VALIDADA** |
| `REF-SEC-004` | Auditoría forense y resguardo de evidencia en SQLite | auditoria, evidencia, sqlite, registro, trazabilidad, fotografia, historico | Política Corporativa de Trazabilidad y Evidencias | **VALIDADA** |
| `REF-SEC-005` | Clasificación de caracteres con red neuronal CNN | cnn, caracteres, clasificador, neuronal, pytorch, entrenamiento, prediccion | Arquitectura de Reconocimiento CNN Semana 08 | **VALIDADA** |
| `REF-SEC-006` | Protocolo experimental de apertura de barrera con placas deterioradas | barrera, deteriorada, apertura, manual, forzada, ilegible | Borrador no validado de contingencias v0.1 | **NO VALIDADA** |
| `REF-SEC-007` | Uso de reconocimiento facial en salida sin imagen de ingreso | facial, biometria, rostro, sin_ingreso | Propuesta preliminar de biometría (No aprobada) | **NO VALIDADA** |

---

## 5. Escenarios de Respuesta y Control de Calidad

1. **`ENCONTRADA` (Referencia validada localizada):**  
   Ocurre cuando la consulta normalizada interseca al menos una palabra clave de un registro con `validada: True`. Se entrega el mensaje oficial junto con el ID, la fuente y el número de coincidencias.
2. **`SIN_REFERENCIA` (Exclusión de borradores):**  
   Si una consulta coincide exclusivamente con palabras de referencias con `validada: False` (por ejemplo, `REF-SEC-006`), el motor ignora dichos registros y devuelve `SIN_REFERENCIA`.
3. **`SIN_REFERENCIA` (Fuera de cobertura):**  
   Si la consulta trata de un tema inexistente en la base de conocimiento (por ejemplo, `"¿Dónde pago la matrícula académica?"`), el sistema declara la falta de evidencia y no inventa una respuesta.
4. **`SIN_DATOS` (Consulta vacía):**  
   Si el usuario envía una cadena vacía o compuesta únicamente por espacios (`"   "`), el sistema informa inmediatamente que debe escribirse una pregunta.

---

## 6. Pruebas Funcionales Automatizadas (`tests/test_motor.py`)

Se implementaron **7 pruebas unitarias** con la biblioteca estándar `unittest`:

```text
test_encuentra_referencia_validada ... ok
test_identificacion_fuente_utilizada ... ok
test_ignora_referencia_no_validada ... ok
test_normaliza_mayusculas_y_tildes ... ok
test_pregunta_fuera_del_conocimiento ... ok
test_rechaza_consulta_vacia ... ok
test_seleccion_por_mayor_coincidencia ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.001s
OK
```

---

## 7. Preguntas de Sustentación Oral y Respuestas Esperadas

1. **¿Cuál es la diferencia entre arquitectura y algoritmo?**  
   *Respuesta:* La arquitectura define la estructura global del sistema, sus bloques funcionales y cómo se comunican entre sí. El algoritmo describe el procedimiento secuencial y determinista dentro de un bloque específico (por ejemplo, el cálculo de intersección de conjuntos y ordenamiento dentro del motor de referencia).
2. **¿Qué información guarda cada referencia?**  
   *Respuesta:* Identificador único (`id`), título descriptivo (`titulo`), lista de palabras clave normalizadas (`claves`), texto de respuesta fundamentada (`respuesta`), documento formal de origen (`fuente`) y estado de aprobación humana (`validada`).
3. **¿Qué hace exactamente la función `normalizar()`?**  
   *Respuesta:* Convierte el texto a minúsculas (`casefold`), descompone caracteres acentuados en forma canónica (`NFD`), filtra y remueve marcas diacríticas de acento (`Mn`), y extrae tokens alfanuméricos mediante expresiones regulares (`r"[a-z0-9]+"`), devolviendo un conjunto (`set`).
4. **¿Por qué es crítico el filtro `if not referencia['validada']: continue`?**  
   *Respuesta:* Es la barrera de seguridad del sistema. Impide que directrices en borrador, procedimientos experimentales o notas no aprobadas sean entregadas a los operadores como respuestas autorizadas.
5. **¿Cómo selecciona el motor la mejor respuesta ante múltiples candidatos?**  
   *Respuesta:* Ordena los candidatos de forma determinista mediante una clave doble: primero por el número de palabras clave coincidentes de forma descendente (`-item[0]`), y en caso de empate, por el identificador de la referencia de forma ascendente (`item[1]`).
6. **¿Por qué el motor se abstiene en lugar de generar una respuesta aproximada?**  
   *Respuesta:* Porque en sistemas de seguridad y misión crítica es inaceptable fabricar información ("alucinar"). Declarar `SIN_REFERENCIA` y derivar a revisión humana garantiza integridad y evita decisiones operativas erróneas.
7. **¿El sistema aprende con las consultas realizadas?**  
   *Respuesta:* No en esta etapa. El motor de referencia es completamente determinista y opera sobre una base estructurada estática. No utiliza modelos estadísticos de lenguaje ni aprendizaje por refuerzo.
8. **¿Qué distingue a este motor del motor de inferencia de la Semana 13?**  
   *Respuesta:* El motor de inferencia encadena reglas lógicas hacia adelante sobre hechos para deducir una nueva conclusión (`autorizar_salida` vs. `enviar_a_revision`). El motor de referencia recupera fichas de conocimiento existentes aprobadas con trazabilidad documental.
9. **¿Por qué la puntuación de coincidencias no es un porcentaje de probabilidad?**  
   *Respuesta:* Porque es un conteo discreto de términos léxicos compartidos, no una medida estadística calibrada sobre una distribución de probabilidad.
10. **¿Cómo se relaciona la base de la Semana 15 con el motor de la Semana 16?**  
    *Respuesta:* La Semana 15 organizó las tablas relacionales y el ciclo editorial en SQLite (`conocimiento.db`). La Semana 16 construye sobre ese conocimiento incorporando indexación por palabras clave, recuperación léxica y consulta interactiva con trazabilidad.
