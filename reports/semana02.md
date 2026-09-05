# Semana 02 - Fundamentos y clasificación

## Resumen del ejercicio

Modelo de aprendizaje automático aplicado a imágenes de placas vehiculares.

| Elemento | Configuración |
|---|---|
| Entrada | Imágenes de placas en escala de grises |
| Tamaño | 64 x 64 píxeles |
| División | 75% entrenamiento / 25% prueba |
| Modelo | StandardScaler + Logistic Regression |
| Evaluación | Accuracy y matriz de confusión |
| Semilla | 42 |

## Flujo de trabajo

- Cargar imágenes y etiquetas YOLO.
- Redimensionar las imágenes y aplanarlas en vectores.
- Entrenar el modelo de clasificación.
- Evaluar las predicciones con accuracy y matriz de confusión.
