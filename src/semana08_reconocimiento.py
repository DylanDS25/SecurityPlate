"""Reconocimiento neuronal de caracteres de placas y registro de evidencia."""

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import random
import sqlite3
import uuid

import networkx as nx
import numpy as np
from PIL import Image, ImageOps
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT_DIR / "data" / "dataset"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "modelo_caracteres.pt"
DATABASE_PATH = ARTIFACTS_DIR / "evidencia_reconocimiento.sqlite3"
ONTOLOGY_PATH = ARTIFACTS_DIR / "ontologia_securityplate.graphml"
METRICS_PATH = ARTIFACTS_DIR / "metricas.json"
CLASS_MAP_PATH = ARTIFACTS_DIR / "mapeo_clases.csv"
REPORT_PATH = ROOT_DIR / "reports" / "semana08.md"
IMAGE_SIZE = 32
RANDOM_SEED = 42


def cargar_clases() -> list[str]:
    """Carga el mapeo de clases del dataset Roboflow."""
    with (DATASET_DIR / "data.yaml").open("r", encoding="utf-8") as archivo:
        configuracion = yaml.safe_load(archivo)
    nombres = configuracion.get("names", [])
    if isinstance(nombres, dict):
        nombres = [nombres[indice] for indice in sorted(nombres)]
    if not nombres:
        raise ValueError("data.yaml no define los nombres de las clases.")
    return [str(nombre) for nombre in nombres]


def guardar_mapeo_clases(class_names: list[str]) -> None:
    """Documenta las clases del dataset sin inventar su significado visual."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with CLASS_MAP_PATH.open("w", encoding="utf-8", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["id_clase", "etiqueta_dataset", "significado", "fuente", "estado"])
        for class_id, class_name in enumerate(class_names):
            writer.writerow(
                [
                    class_id,
                    class_name,
                    "Caracter alfanumerico no identificado",
                    "data/dataset/data.yaml",
                    "requiere mapeo validado",
                ]
            )


class RecortesYOLO(Dataset):
    """Lee cajas YOLO como recortes etiquetados de caracteres individuales."""

    def __init__(self, split: str) -> None:
        if split not in {"train", "valid", "test"}:
            raise ValueError("El split debe ser train, valid o test.")
        image_dir = DATASET_DIR / split / "images"
        label_dir = DATASET_DIR / split / "labels"
        if not image_dir.is_dir() or not label_dir.is_dir():
            raise FileNotFoundError(f"No se encontraron imagenes/labels para {split}.")

        self.samples: list[tuple[Path, int, tuple[float, float, float, float]]] = []
        class_count = len(cargar_clases())
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        for image_path in sorted(image_dir.iterdir()):
            if image_path.suffix.lower() not in valid_extensions:
                continue
            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.exists():
                continue
            for line_number, line in enumerate(
                label_path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if not line.strip():
                    continue
                fields = line.split()
                if len(fields) < 5:
                    raise ValueError(f"Anotacion YOLO invalida en {label_path}:{line_number}.")
                class_id = int(fields[0])
                coordinates = [float(value) for value in fields[1:]]
                if len(coordinates) == 4:
                    center_x, center_y, width, height = coordinates
                elif len(coordinates) >= 6 and len(coordinates) % 2 == 0:
                    points = list(zip(coordinates[::2], coordinates[1::2]))
                    min_x = min(point[0] for point in points)
                    max_x = max(point[0] for point in points)
                    min_y = min(point[1] for point in points)
                    max_y = max(point[1] for point in points)
                    center_x = (min_x + max_x) / 2
                    center_y = (min_y + max_y) / 2
                    width = max_x - min_x
                    height = max_y - min_y
                else:
                    raise ValueError(
                        f"Formato YOLO de caja/poligono invalido en "
                        f"{label_path}:{line_number}."
                    )
                box = (center_x, center_y, width, height)
                if not 0 <= class_id < class_count:
                    raise ValueError(f"ID de clase fuera de rango en {label_path}:{line_number}.")
                if any(value < 0 or value > 1 for value in box):
                    raise ValueError(f"Caja YOLO fuera del rango [0, 1] en {label_path}.")
                self.samples.append((image_path, class_id, box))
        if not self.samples:
            raise ValueError(f"No hay recortes anotados en el split {split}.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int, str]:
        image_path, class_id, (center_x, center_y, width, height) = self.samples[index]
        with Image.open(image_path) as image:
            image = ImageOps.grayscale(image)
            image_width, image_height = image.size
            left = max(0, int((center_x - width / 2) * image_width))
            top = max(0, int((center_y - height / 2) * image_height))
            right = min(image_width, int((center_x + width / 2) * image_width))
            bottom = min(image_height, int((center_y + height / 2) * image_height))
            if right <= left or bottom <= top:
                raise ValueError(f"Caja vacia en {image_path}.")
            crop = image.crop((left, top, right, bottom))
            crop = crop.resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.BILINEAR)
            pixels = np.asarray(crop, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(pixels).unsqueeze(0)
        return tensor, class_id, str(image_path.relative_to(ROOT_DIR))


class RedCaracteres(nn.Module):
    """CNN compacta para clasificar las 50 categorias de caracteres."""

    def __init__(self, class_count: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, class_count)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs).flatten(start_dim=1))


def preparar_ontologia() -> nx.DiGraph:
    """Crea los conceptos y relaciones propios del reconocimiento de placas."""
    graph = nx.DiGraph()
    concepts = {
        "imagen_placa": ("Imagen de placa", "Entrada visual capturada para el sistema."),
        "placa": ("Placa vehicular", "Identificador alfanumerico asociado a un vehiculo."),
        "caracter": ("Caracter", "Unidad visual individual localizada dentro de la placa."),
        "modelo_rna": ("Modelo RNA", "CNN que clasifica recortes de caracteres."),
        "prediccion": ("Prediccion", "Resultado de clase y probabilidad del modelo."),
        "evidencia": ("Evidencia", "Registro persistente de una prediccion."),
        "verificacion": ("Verificacion de acceso", "Compara la placa reconocida con el registro."),
    }
    for node_id, (label, description) in concepts.items():
        graph.add_node(node_id, label=label, tipo="concepto", descripcion=description)
    relations = [
        ("imagen_placa", "contiene", "placa"),
        ("placa", "esta_compuesta_por", "caracter"),
        ("modelo_rna", "analiza", "caracter"),
        ("modelo_rna", "genera", "prediccion"),
        ("prediccion", "asigna_categoria_a", "caracter"),
        ("evidencia", "registra", "prediccion"),
        ("verificacion", "utiliza", "prediccion"),
        ("verificacion", "compara", "placa"),
    ]
    for source, relation, target in relations:
        graph.add_edge(source, target, relacion=relation)
    for class_id, class_name in enumerate(cargar_clases()):
        node_id = f"clase_{class_id}"
        graph.add_node(
            node_id,
            label=f"Clase dataset {class_name}",
            tipo="clase_caracter",
            id_clase=class_id,
            significado="Caracter alfanumerico no identificado",
            fuente="data/dataset/data.yaml",
        )
        graph.add_edge("caracter", node_id, relacion="se_clasifica_como")
    return graph


def cargar_ontologia() -> nx.DiGraph:
    if ONTOLOGY_PATH.exists():
        graph = nx.read_graphml(ONTOLOGY_PATH)
        graph.update(preparar_ontologia())
        return graph
    return preparar_ontologia()


def guardar_ontologia(graph: nx.DiGraph) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, ONTOLOGY_PATH)


def inicializar_base() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS predicciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ejecucion_id TEXT NOT NULL,
                imagen_analizada TEXT NOT NULL,
                particion TEXT NOT NULL,
                categoria_real_id INTEGER,
                categoria_real TEXT,
                prediccion_id INTEGER NOT NULL,
                prediccion TEXT NOT NULL,
                probabilidad REAL NOT NULL,
                modelo TEXT NOT NULL,
                fecha_hora TEXT NOT NULL
            )"""
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_predicciones_ejecucion "
            "ON predicciones(ejecucion_id)"
        )


def registrar_evidencia(
    graph: nx.DiGraph,
    run_id: str,
    image_name: str,
    split: str,
    actual_id: int | None,
    predicted_id: int,
    probability: float,
    class_names: list[str],
) -> int:
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """INSERT INTO predicciones (
                ejecucion_id, imagen_analizada, particion, categoria_real_id,
                categoria_real, prediccion_id, prediccion, probabilidad,
                modelo, fecha_hora
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                image_name,
                split,
                actual_id,
                class_names[actual_id] if actual_id is not None else None,
                predicted_id,
                class_names[predicted_id],
                probability,
                MODEL_PATH.name,
                timestamp,
            ),
        )
        record_id = int(cursor.lastrowid)

    prediction_node = f"prediccion_{record_id}"
    evidence_node = f"evidencia_{record_id}"
    image_node = f"imagen_{record_id}"
    graph.add_node(
        prediction_node,
        label=f"Prediccion {record_id}: {class_names[predicted_id]}",
        tipo="instancia_prediccion",
        probabilidad=probability,
    )
    graph.add_node(
        evidence_node,
        label=f"Registro SQLite {record_id}",
        tipo="instancia_evidencia",
        fecha_hora=timestamp,
        particion=split,
    )
    graph.add_node(image_node, label=image_name, tipo="instancia_imagen")
    graph.add_edge("modelo_rna", prediction_node, relacion="genera")
    graph.add_edge(prediction_node, f"clase_{predicted_id}", relacion="predice_categoria")
    graph.add_edge(evidence_node, prediction_node, relacion="registra")
    graph.add_edge(evidence_node, image_node, relacion="documenta_analisis_de")
    graph.add_edge(image_node, "imagen_placa", relacion="es_una")
    return record_id


def evaluar(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    class_count: int,
) -> dict[str, object]:
    model.eval()
    actual_ids: list[int] = []
    predicted_ids: list[int] = []
    probabilities: list[float] = []
    image_names: list[str] = []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    with torch.inference_mode():
        for images, labels, names in loader:
            images = images.to(device)
            labels = labels.to(device)
            logits = model(images)
            total_loss += criterion(logits, labels).item() * labels.size(0)
            batch_probabilities = torch.softmax(logits, dim=1)
            confidence, predictions = batch_probabilities.max(dim=1)
            actual_ids.extend(labels.cpu().tolist())
            predicted_ids.extend(predictions.cpu().tolist())
            probabilities.extend(confidence.cpu().tolist())
            image_names.extend(names)
    return {
        "loss": total_loss / len(actual_ids),
        "accuracy": accuracy_score(actual_ids, predicted_ids),
        "f1_macro": f1_score(actual_ids, predicted_ids, average="macro", zero_division=0),
        "actual_ids": actual_ids,
        "predicted_ids": predicted_ids,
        "probabilities": probabilities,
        "image_names": image_names,
        "confusion_matrix": confusion_matrix(
            actual_ids, predicted_ids, labels=list(range(class_count))
        ),
    }


def guardar_resultados_test(
    metrics: dict[str, object], class_names: list[str], run_id: str
) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    matrix = metrics["confusion_matrix"]
    with (ARTIFACTS_DIR / "matriz_confusion_test.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["real/predicha", *class_names])
        for class_name, row in zip(class_names, matrix):
            writer.writerow([class_name, *row.tolist()])

    with (ARTIFACTS_DIR / "predicciones_test.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        writer = csv.writer(archivo)
        writer.writerow(
            ["ejecucion_id", "imagen", "categoria_real_id", "prediccion_id", "probabilidad"]
        )
        for image, actual_id, predicted_id, probability in zip(
            metrics["image_names"],
            metrics["actual_ids"],
            metrics["predicted_ids"],
            metrics["probabilities"],
        ):
            writer.writerow([run_id, image, actual_id, predicted_id, f"{probability:.6f}"])


def consultar_evidencia_sqlite() -> tuple[int, list[tuple[object, ...]]]:
    """Obtiene un resumen consultable de la evidencia persistida."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        total = int(connection.execute("SELECT COUNT(*) FROM predicciones").fetchone()[0])
        rows = connection.execute(
            """SELECT id, imagen_analizada, categoria_real, prediccion,
                      probabilidad, fecha_hora
               FROM predicciones
               ORDER BY id DESC
               LIMIT 3"""
        ).fetchall()
    return total, rows


def generar_reporte(
    class_names: list[str],
    sample_counts: dict[str, int],
    metrics: dict[str, object],
    validation_metrics: dict[str, float],
    run_id: str,
) -> None:
    total_records, evidence_rows = consultar_evidencia_sqlite()
    evidence_table = [
        "```sql",
        "SELECT id, imagen_analizada, categoria_real, prediccion,",
        "       probabilidad, fecha_hora",
        "FROM predicciones ORDER BY id DESC LIMIT 3;",
        "```",
        "",
        f"La consulta devuelve **{total_records}** registros en total. Muestra reciente:",
        "",
        "| ID | Imagen | Categoria real | Prediccion | Probabilidad | Fecha |",
        "|---:|---|---|---|---:|---|",
    ]
    evidence_table.extend(
        "| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |"
        for row in evidence_rows
    )
    lineas = [
        "# Semana 08 - Representaciones del reconocimiento",
        "",
        "## Objetivo y alcance",
        "",
        "SecurityPlate reconoce categorias de caracteres en placas vehiculares. "
        "El flujo implementado es: recorte anotado YOLO -> CNN -> prediccion y probabilidad "
        "-> evidencia SQLite -> interpretacion mediante ontologia GraphML.",
        "",
        "El clasificador opera sobre un recorte de un caracter. La localizacion de placas "
        "y caracteres corresponde a la etapa de deteccion previa del proyecto; el clasificador "
        "no recibe directamente fotografias completas para leer toda la placa.",
        "",
        "## Datos y preprocesamiento",
        "",
        "Se usan las particiones oficiales `train`, `valid` y `test` de "
        "`data/dataset`. Cada caja YOLO se recorta de su imagen, se convierte a escala de "
        "grises, se redimensiona a 32 x 32 y se normaliza al rango [0, 1]. Los nombres/IDs "
        "se leen de `data.yaml`; se conservan sus categorias numericas tal como fueron entregadas. "
        "El detalle de trazabilidad queda en `artifacts/mapeo_clases.csv`.",
        "",
        f"Clases: **{len(class_names)}**. Recortes: entrenamiento **{sample_counts['train']}**, "
        f"validacion **{sample_counts['valid']}**, prueba **{sample_counts['test']}**.",
        "",
        "## Red neuronal y validacion",
        "",
        "La RNA es una CNN compacta de tres capas convolucionales con ReLU y pooling, "
        "seguida de una capa de clasificacion. Usa entropia cruzada, Adam (tasa 0.001), "
        "semilla 42 y selecciona el estado con mejor F1 macro en validacion. El conjunto "
        "de prueba se evalua al finalizar el entrenamiento.",
        "",
        f"Ejecucion: `{run_id}`. Accuracy de prueba: **{metrics['accuracy']:.4f}**. "
        f"F1 macro de prueba: **{metrics['f1_macro']:.4f}**. "
        f"Perdida de prueba: **{metrics['loss']:.4f}**.",
        "",
        f"Mejor epoca de validacion: accuracy **{validation_metrics['accuracy']:.4f}**, "
        f"F1 macro **{validation_metrics['f1_macro']:.4f}**, "
        f"perdida **{validation_metrics['loss']:.4f}**. El historial por epoca esta en "
        "`artifacts/historial_entrenamiento.csv`.",
        "",
        "El estado entrenado se guarda como `artifacts/modelo_caracteres.pt`. "
        "La matriz de confusion y las predicciones de prueba quedan en CSV junto con "
        "el historial de perdida y F1 por epoca.",
        "",
        "## Evidencia SQLite",
        "",
        "`artifacts/evidencia_reconocimiento.sqlite3` contiene un registro por prediccion: "
        "ID, ejecucion, ruta de imagen analizada, particion, categoria real (cuando existe), "
        "clase predicha, probabilidad, modelo y fecha/hora. Las predicciones de prueba se "
        "registran al entrenar; las inferencias nuevas tambien se insertan en la misma tabla.",
        "",
        "Consulta de evidencia ejecutada:",
        "",
        *evidence_table,
        "",
        "## Ontologia GraphML",
        "",
        "`artifacts/ontologia_securityplate.graphml` representa los conceptos Imagen de placa, "
        "Placa vehicular, Caracter, Modelo RNA, Prediccion, Evidencia y Verificacion de acceso. "
        "Entre sus relaciones estan `contiene`, `esta_compuesta_por`, `analiza`, `genera`, "
        "`asigna_categoria_a`, `registra`, `utiliza` y `compara`. El archivo incluye nodos "
        "de categorias e instancias enlazadas a las evidencias SQLite. Cada categoria conserva "
        "su ID de dataset y declara si su significado visual aun no esta validado.",
        "",
        "## Ejecucion",
        "",
        "Desde la raiz del repositorio:",
        "",
        "```powershell",
        "python src/semana08_reconocimiento.py --epochs 10 --batch-size 64",
        "python src/semana08_reconocimiento.py --predict ruta\\al\\recorte.jpg",
        "python src/semana08_reconocimiento.py --report",
        "```",
        "",
        "La funcion `predict(ruta)` devuelve `class_id`, `class_name` y `probability`; "
        "ademas persiste la evidencia y actualiza el GraphML. La entrada debe ser el recorte "
        "de un unico caracter. El comando `--report` regenera este archivo desde "
        "`artifacts/metricas.json` y las particiones actuales del dataset, sin reentrenar.",
        "",
        "## Interpretacion y limitaciones",
        "",
        "El modelo aprende patrones visuales de forma, trazo y contraste en los recortes. "
        "La categoria predicha puede apoyar la lectura y posterior verificacion de la placa; "
        "por si sola no autoriza entradas ni salidas.",
        "",
        "Los IDs de clase de `data.yaml` no explican por si mismos una letra o digito legible, "
        "por lo que `artifacts/mapeo_clases.csv` conserva el ID, la fuente y el estado pendiente "
        "de validacion, sin inventar un caracter. El conjunto esta desbalanceado (una de las "
        "clases observadas tiene solo tres anotaciones), lo cual puede perjudicar el F1 por clase. "
        "La probabilidad softmax no esta calibrada, y el rendimiento depende de la calidad del "
        "recorte y del dominio del dataset. La RNA no reconstruye la secuencia completa de la placa.",
    ]
    REPORT_PATH.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def regenerar_reporte() -> None:
    """Regenera el reporte usando las metricas y datos actuales del proyecto."""
    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"No existe {METRICS_PATH.relative_to(ROOT_DIR)}. Ejecute el entrenamiento primero."
        )
    results = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    class_names = cargar_clases()
    guardar_mapeo_clases(class_names)
    guardar_ontologia(cargar_ontologia())
    sample_counts = {
        split: len(RecortesYOLO(split)) for split in ("train", "valid", "test")
    }
    generar_reporte(
        class_names,
        sample_counts,
        results["test"],
        results["validation"],
        results["run_id"],
    )
    print(f"Reporte regenerado en {REPORT_PATH.relative_to(ROOT_DIR)}")


def entrenar(epochs: int = 10, batch_size: int = 64) -> dict[str, object]:
    """Entrena, selecciona con validacion, prueba y genera los artefactos."""
    if epochs < 1 or batch_size < 1:
        raise ValueError("epochs y batch-size deben ser positivos.")
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    torch.manual_seed(RANDOM_SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    class_names = cargar_clases()
    datasets = {split: RecortesYOLO(split) for split in ("train", "valid", "test")}
    loaders = {
        split: DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=(split == "train"),
            num_workers=0,
        )
        for split, dataset in datasets.items()
    }
    model = RedCaracteres(len(class_names)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    best_f1 = -1.0
    best_validation_accuracy = 0.0
    best_validation_loss = 0.0
    best_state: dict[str, torch.Tensor] | None = None
    history: list[dict[str, float | int]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for images, labels, _ in loaders["train"]:
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * labels.size(0)

        validation = evaluar(model, loaders["valid"], device, len(class_names))
        row: dict[str, float | int] = {
            "epoch": epoch,
            "train_loss": train_loss / len(datasets["train"]),
            "validation_loss": float(validation["loss"]),
            "validation_accuracy": float(validation["accuracy"]),
            "validation_f1_macro": float(validation["f1_macro"]),
        }
        history.append(row)
        print(
            f"Epoca {epoch}/{epochs}: loss={row['train_loss']:.4f}, "
            f"accuracy_val={row['validation_accuracy']:.4f}, "
            f"f1_macro_val={row['validation_f1_macro']:.4f}"
        )
        if row["validation_f1_macro"] > best_f1:
            best_f1 = float(row["validation_f1_macro"])
            best_validation_accuracy = float(row["validation_accuracy"])
            best_validation_loss = float(row["validation_loss"])
            best_state = {
                name: tensor.detach().cpu().clone()
                for name, tensor in model.state_dict().items()
            }

    if best_state is None:
        raise RuntimeError("No se obtuvo un estado entrenado para guardar.")
    model.load_state_dict(best_state)
    model.to(device)
    test_metrics = evaluar(model, loaders["test"], device, len(class_names))
    run_id = str(uuid.uuid4())
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": best_state,
            "class_names": class_names,
            "image_size": IMAGE_SIZE,
            "architecture": "RedCaracteres",
        },
        MODEL_PATH,
    )
    with (ARTIFACTS_DIR / "historial_entrenamiento.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        writer = csv.DictWriter(archivo, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)

    inicializar_base()
    graph = cargar_ontologia()
    for image, actual_id, predicted_id, probability in zip(
        test_metrics["image_names"],
        test_metrics["actual_ids"],
        test_metrics["predicted_ids"],
        test_metrics["probabilities"],
    ):
        registrar_evidencia(
            graph, run_id, image, "test", actual_id, predicted_id,
            probability, class_names,
        )
    guardar_ontologia(graph)
    guardar_resultados_test(test_metrics, class_names, run_id)
    sample_counts = {split: len(dataset) for split, dataset in datasets.items()}
    results = {
        "run_id": run_id,
        "model": str(MODEL_PATH.relative_to(ROOT_DIR)),
        "device": str(device),
        "samples": sample_counts,
        "classes": len(class_names),
        "validation": {
            "accuracy": best_validation_accuracy,
            "f1_macro": best_f1,
            "loss": best_validation_loss,
        },
        "test": {
            "loss": float(test_metrics["loss"]),
            "accuracy": float(test_metrics["accuracy"]),
            "f1_macro": float(test_metrics["f1_macro"]),
        },
    }
    (ARTIFACTS_DIR / "metricas.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    regenerar_reporte()
    print(
        f"Test: accuracy={test_metrics['accuracy']:.4f}, "
        f"F1 macro={test_metrics['f1_macro']:.4f}"
    )
    print(f"Artefactos guardados en {ARTIFACTS_DIR.relative_to(ROOT_DIR)}")
    return results


def predict(
    image_path: str | Path,
    model_path: str | Path = MODEL_PATH,
    actual_class_id: int | None = None,
) -> dict[str, object]:
    """Clasifica un recorte y registra resultado y significado asociado."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(model_path, map_location=device, weights_only=True)
    class_names = checkpoint["class_names"]
    model = RedCaracteres(len(class_names)).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    with Image.open(image_path) as image:
        image = ImageOps.grayscale(image).resize(
            (checkpoint["image_size"], checkpoint["image_size"]),
            Image.Resampling.BILINEAR,
        )
        pixels = np.asarray(image, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(pixels).unsqueeze(0).unsqueeze(0).to(device)
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor), dim=1)[0]
    predicted_id = int(probabilities.argmax().item())
    probability = float(probabilities[predicted_id].item())
    if actual_class_id is not None and not 0 <= actual_class_id < len(class_names):
        raise ValueError("actual-class debe ser un ID definido en data.yaml.")

    inicializar_base()
    graph = cargar_ontologia()
    run_id = str(uuid.uuid4())
    image_name = str(Path(image_path).resolve())
    record_id = registrar_evidencia(
        graph, run_id, image_name, "inferencia", actual_class_id,
        predicted_id, probability, class_names,
    )
    guardar_ontologia(graph)
    return {
        "registro_id": record_id,
        "class_id": predicted_id,
        "class_name": class_names[predicted_id],
        "probability": probability,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--predict", type=Path, help="Ruta a un recorte de caracter")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Regenera el reporte desde metricas.json y los datos actuales",
    )
    parser.add_argument("--actual-class", type=int, help="ID real opcional de data.yaml")
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    args = parser.parse_args()
    if args.report:
        regenerar_reporte()
    elif args.predict:
        prediction = predict(args.predict, args.model, args.actual_class)
        print(json.dumps(prediction, ensure_ascii=False, indent=2))
    else:
        entrenar(args.epochs, args.batch_size)


if __name__ == "__main__":
    main()