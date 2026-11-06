# ADR Semana 11 - Selección de modelo para caracteres de placas

## Contexto

SecurityPlate necesita clasificar recortes anotados de caracteres de placas vehiculares. Para que la práctica evalúe datos del proyecto y no copie el ejemplo de dígitos, se usan las cajas YOLO de `data/dataset`: cada recorte se reduce de 32 x 32 a 16 x 16 y se aplana en un vector de intensidades normalizadas para limitar el costo computacional.

Se entrenó con 11296 recortes del split oficial `train` y se evaluó con 323 recortes del split oficial `test`. Las mismas particiones cubren 50 clases de entrenamiento y 48 de 50 clases en prueba. Se conservaron para los tres modelos y en las tres ejecuciones. Los modelos estocásticos usan semillas 42, 43 y 44. Se midió accuracy y tiempo de `fit`; la predicción no se incluye en ese tiempo.

## Modelos comparados

- **Logistic Regression:** línea base con `StandardScaler`.
- **Random Forest:** 100 árboles de decisión.
- **MLPClassifier:** una capa oculta de 64 neuronas, hasta 100 iteraciones, con `StandardScaler`.

## Resultados

Cada fila del CSV representa una ejecución individual; la tabla resume media y desviación estándar de accuracy, además del tiempo medio de entrenamiento.

| Modelo | Accuracy promedio | Desv. estándar | Tiempo promedio (s) |
|---|---:|---:|---:|
| random_forest | 0.6883 | 0.0117 | 10.4571 |
| mlp | 0.6522 | 0.0114 | 24.9662 |
| logistic_regression | 0.6161 | 0.0000 | 27.2502 |

**Diferencias:** random_forest superó a los otros modelos por 7.22 puntos porcentuales frente a logistic_regression y 3.61 puntos porcentuales frente a mlp en accuracy promedio.

**Convergencia:** mlp: 3 ejecucion(es) sin converger

El archivo [benchmark.csv](../artifacts/benchmark.csv) conserva 9 resultados (3 modelos x 3 ejecuciones).

## Decisión

Se selecciona provisionalmente **random_forest** para la siguiente iteración: su accuracy promedio es 0.6883 y su tiempo de entrenamiento promedio es 10.4571 s. La regla aplicada prioriza el menor tiempo entre los modelos cuya accuracy queda a no más de 1% del mejor promedio (random_forest, 0.6883).

Esta es una decisión de prototipado, no una selección definitiva para producción. Debe confirmarse con más datos etiquetados y con métricas por clase.

## Ventajas y limitaciones

- **random_forest:** Ensamble de árboles que modela relaciones no lineales; su tamaño puede aumentar costo de memoria e inferencia y reduce la explicabilidad global.
- El benchmark usa el mismo split, las mismas características y las mismas tres ejecuciones para comparar las alternativas de forma consistente.
- El test tiene 48 de 50 clases representadas; la distribución por clase es desigual. Accuracy global puede ocultar errores de clases poco frecuentes, por lo que conviene agregar F1 macro, matriz de confusión y más ejemplos antes de una decisión productiva.
- El experimento clasifica recortes que ya fueron localizados y anotados. No detecta la placa, no localiza cada carácter y no reconstruye la cadena OCR.
- Reducir los recortes a 16 x 16 disminuye el costo de cálculo, pero puede eliminar detalles finos que ayudan a distinguir caracteres visualmente similares.
- Los nombres de las 50 clases del dataset son IDs numéricos; su semántica alfanumérica requiere validación antes de interpretar predicciones como letras o números concretos.
- El tiempo depende del hardware y de la carga del equipo; las tres repeticiones permiten observar variación, pero no equivalen a una evaluación estadística extensa.

## Aplicación al proyecto final

El modelo seleccionado podría sustituir o servir como referencia frente a la CNN de Semana 8 para clasificar los recortes producidos por la etapa de detección. Cada predicción tendría que mapearse a un carácter validado y combinarse en secuencia para leer la placa. La autorización de ingreso/salida debe seguir dependiendo de la verificación del registro, la confianza y las reglas del sistema híbrido; esta clasificación aislada no debe tomar esa decisión.

Python y scikit-learn son adecuados para este benchmark reproducible. Si el servicio final usa otro backend, el clasificador podría exponerse mediante una API, tras validar latencia, serialización, seguridad y mantenimiento.

## Reproducibilidad

Desde la raíz del repositorio, ejecutar `python src/semana11_benchmark.py`. El script realiza tres ejecuciones por modelo y regenera este ADR y `artifacts/benchmark.csv`.

Fuente del conjunto: Roboflow, licencia CC BY 4.0; referencia y atribución en `data/dataset/README.dataset.txt`.


| Alternativa | Fortalezas | Debilidades | Oportunidades | Amenazas |
| --- | --- | --- | --- | --- |
| **Node.js / Express** | Curva nula, RAM baja | Latencia moderada | Integración npm | Dependencias inseguras |
| **Python / FastAPI** | Rendimiento alto | Curva alta | Analítica futura | RAM alta |
| **Node.js / NestJS** | Alta mantenibilidad | Configuración compleja | Estandarización | Retraso temporal|