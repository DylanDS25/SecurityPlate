# Semana 08 - Representaciones del reconocimiento

## Objetivo y alcance

SecurityPlate reconoce categorias de caracteres en placas vehiculares. El flujo implementado es: recorte anotado YOLO -> CNN -> prediccion y probabilidad -> evidencia SQLite -> interpretacion mediante ontologia GraphML.

El clasificador opera sobre un recorte de un caracter. La localizacion de placas y caracteres corresponde a la etapa de deteccion previa del proyecto; el clasificador no recibe directamente fotografias completas para leer toda la placa.

## Datos y preprocesamiento

Se usan las particiones oficiales `train`, `valid` y `test` de `data/dataset`. Cada caja YOLO se recorta de su imagen, se convierte a escala de grises, se redimensiona a 32 x 32 y se normaliza al rango [0, 1]. Los nombres/IDs se leen de `data.yaml`; se conservan sus categorias numericas tal como fueron entregadas.

Clases: **50**. Recortes: entrenamiento **11296**, validacion **879**, prueba **323**.

## Red neuronal y validacion

La RNA es una CNN compacta de tres capas convolucionales con ReLU y pooling, seguida de una capa de clasificacion. Usa entropia cruzada, Adam (tasa 0.001), semilla 42 y selecciona el estado con mejor F1 macro en validacion. El conjunto de prueba se evalua al finalizar el entrenamiento.

Ejecucion: `c0398c43-4c29-4990-a25a-14abf36b7eec`. Accuracy de prueba: **0.5015**. F1 macro de prueba: **0.4235**. Perdida de prueba: **1.8684**.

Mejor epoca de validacion: accuracy **0.4846**, F1 macro **0.4247**, perdida **1.7503**. El historial por epoca esta en `artifacts/historial_entrenamiento.csv`.

El estado entrenado se guarda como `artifacts/modelo_caracteres.pt`. La matriz de confusion y las predicciones de prueba quedan en CSV junto con el historial de perdida y F1 por epoca.

## Evidencia SQLite

`artifacts/evidencia_reconocimiento.sqlite3` contiene un registro por prediccion: ID, ejecucion, ruta de imagen analizada, particion, categoria real (cuando existe), clase predicha, probabilidad, modelo y fecha/hora. Las predicciones de prueba se registran al entrenar; las inferencias nuevas tambien se insertan en la misma tabla.

## Ontologia GraphML

`artifacts/ontologia_securityplate.graphml` representa los conceptos Imagen de placa, Placa vehicular, Caracter, Modelo RNA, Prediccion, Evidencia y Verificacion de acceso. Entre sus relaciones estan `contiene`, `esta_compuesta_por`, `analiza`, `genera`, `asigna_categoria_a`, `registra`, `utiliza` y `compara`. El archivo incluye nodos de categorias e instancias enlazadas a las evidencias SQLite.

## Ejecucion

Desde la raiz del repositorio:

```powershell
python src/semana08_reconocimiento.py --epochs 10 --batch-size 64
python src/semana08_reconocimiento.py --predict ruta\al\recorte.jpg
```

La funcion `predict(ruta)` devuelve `class_id`, `class_name` y `probability`; ademas persiste la evidencia y actualiza el GraphML. La entrada debe ser el recorte de un unico caracter.

## Interpretacion y limitaciones

El modelo aprende patrones visuales de forma, trazo y contraste en los recortes. La categoria predicha puede apoyar la lectura y posterior verificacion de la placa; por si sola no autoriza entradas ni salidas.

Los IDs de clase de `data.yaml` no explican por si mismos una letra o digito legible, por lo que la entrega no inventa ese mapeo. El conjunto esta desbalanceado (una de las clases observadas tiene solo tres anotaciones), lo cual puede perjudicar el F1 por clase. La probabilidad softmax no esta calibrada, y el rendimiento depende de la calidad del recorte y del dominio del dataset. La RNA no reconstruye la secuencia completa de la placa.
