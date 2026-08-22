import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from pathlib import Path

RANDOM_STATE = 42
IMAGEN_SIZE = (64, 64)

# Rutas
DATASET_PATH = Path("data/dataset")
TRAIN_IMAGES = DATASET_PATH / "train" / "images"
TRAIN_LABELS = DATASET_PATH / "train" / "labels"

# Cargar imágenes y etiquetas
def load_data(images_dir, labels_dir):
    X = []
    y = []
    
    for img_file in os.listdir(images_dir):
        if not img_file.endswith(('.jpg', '.png')):
            continue
        
        # Cargar imagen
        img_path = os.path.join(images_dir, img_file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        
        # Resize
        img = cv2.resize(img, IMAGEN_SIZE)
        X.append(img.flatten())  # Aplanar a vector
        
        # Cargar etiqueta (primera clase de la anotación)
        label_file = img_file.rsplit('.', 1)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    clase = int(lines[0].split()[0])  # Primera clase
                    y.append(clase)
                else:
                    continue
        else:
            continue
    
    return np.array(X), np.array(y)

print("Cargando datos...")
X, y = load_data(str(TRAIN_IMAGES), str(TRAIN_LABELS))

print(f"Imágenes cargadas: {len(X)}")
print(f"Clases únicas: {np.unique(y)}")

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
)

# Modelo (igual que Iris)
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
)

print("Entrenando modelo...")
model.fit(X_train, y_train)

# Predicciones
pred = model.predict(X_test)

# Resultados
print(f"\nMuestras entrenamiento: {len(X_train)}")
print(f"Muestras prueba: {len(X_test)}")
print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")
print("Matriz de confusión:")
print(confusion_matrix(y_test, pred))