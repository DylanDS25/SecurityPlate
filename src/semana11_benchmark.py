"""Compara clasificadores sobre recortes anotados de caracteres de placas."""

import argparse
import csv
from pathlib import Path
import statistics
from time import perf_counter
from typing import Any
import warnings

import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

if __package__:
    from .semana08_reconocimiento import IMAGE_SIZE, RecortesYOLO, cargar_clases
else:
    from semana08_reconocimiento import IMAGE_SIZE, RecortesYOLO, cargar_clases


ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
BENCHMARK_PATH = ARTIFACTS_DIR / "benchmark.csv"
REPORT_PATH = ROOT_DIR / "reports" / "semana11_adr.md"
DEFAULT_REPEATS = 3
ACCURACY_TOLERANCE = 0.01
BENCHMARK_IMAGE_SIZE = 16


def cargar_datos(split: str) -> tuple[np.ndarray, np.ndarray]:
    """Convierte recortes YOLO de un split oficial en vectores de pixeles."""
    dataset = RecortesYOLO(split)
    features = np.empty(
        (len(dataset), BENCHMARK_IMAGE_SIZE * BENCHMARK_IMAGE_SIZE),
        dtype=np.float32,
    )
    labels = np.empty(len(dataset), dtype=np.int64)
    for index in range(len(dataset)):
        image, class_id, _ = dataset[index]
        pixels = (image.squeeze(0).numpy() * 255).astype(np.uint8)
        resized = Image.fromarray(pixels).resize(
            (BENCHMARK_IMAGE_SIZE, BENCHMARK_IMAGE_SIZE),
            Image.Resampling.BILINEAR,
        )
        features[index] = np.asarray(resized, dtype=np.float32).reshape(-1) / 255
        labels[index] = class_id
    return features, labels


def crear_modelos(seed: int) -> dict[str, Any]:
    """Construye los tres modelos con parámetros reproducibles."""
    return {
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1500, random_state=seed),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            random_state=seed,
            n_jobs=-1,
        ),
        "mlp": make_pipeline(
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=(64,),
                max_iter=100,
                random_state=seed,
            ),
        ),
    }


def ejecutar_benchmark(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    repeats: int = DEFAULT_REPEATS,
) -> list[dict[str, float | int | str | bool]]:
    """Evalúa cada modelo en el mismo split durante al menos tres ejecuciones."""
    if repeats < DEFAULT_REPEATS:
        raise ValueError(f"El benchmark requiere al menos {DEFAULT_REPEATS} ejecuciones.")
    if len(X_train) != len(y_train) or len(X_test) != len(y_test):
        raise ValueError("Cada conjunto de entradas debe tener el mismo tamaño que sus etiquetas.")
    if not len(X_train) or not len(X_test):
        raise ValueError("Los conjuntos de entrenamiento y prueba no pueden estar vacíos.")

    results: list[dict[str, float | int | str | bool]] = []
    for run in range(1, repeats + 1):
        for model_name, model in crear_modelos(seed=41 + run).items():
            start = perf_counter()
            with warnings.catch_warnings(record=True) as fit_warnings:
                warnings.simplefilter("always", ConvergenceWarning)
                model.fit(X_train, y_train)
            fit_seconds = perf_counter() - start
            converged = not any(
                issubclass(warning.category, ConvergenceWarning)
                for warning in fit_warnings
            )
            if not converged:
                warnings.warn(
                    f"{model_name} no convergio en la ejecucion {run}.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            accuracy = accuracy_score(y_test, model.predict(X_test))
            results.append(
                {
                    "modelo": model_name,
                    "ejecucion": run,
                    "accuracy": float(accuracy),
                    "fit_seconds": float(fit_seconds),
                    "convergido": converged,
                }
            )
    return results


def resumir_resultados(
    results: list[dict[str, float | int | str | bool]],
) -> dict[str, dict[str, float]]:
    """Calcula promedios y variación entre ejecuciones para cada modelo."""
    summaries: dict[str, dict[str, float]] = {}
    model_names = sorted({str(result["modelo"]) for result in results})
    for model_name in model_names:
        model_results = [result for result in results if result["modelo"] == model_name]
        accuracies = [float(result["accuracy"]) for result in model_results]
        fit_times = [float(result["fit_seconds"]) for result in model_results]
        summaries[model_name] = {
            "mean_accuracy": statistics.mean(accuracies),
            "std_accuracy": statistics.pstdev(accuracies),
            "mean_fit_seconds": statistics.mean(fit_times),
        }
    return summaries


def guardar_benchmark(results: list[dict[str, float | int | str | bool]]) -> None:
    """Guarda una fila por modelo y ejecución para conservar la variación."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with BENCHMARK_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "modelo",
                "ejecucion",
                "accuracy",
                "fit_seconds",
                "convergido",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    **result,
                    "accuracy": f"{float(result['accuracy']):.8f}",
                    "fit_seconds": f"{float(result['fit_seconds']):.6f}",
                }
            )


def seleccionar_modelo(
    summaries: dict[str, dict[str, float]],
) -> str:
    """Elige el más rápido entre los modelos a un punto porcentual del mejor."""
    if not summaries:
        raise ValueError("No hay resultados para justificar una decisión.")
    best_accuracy = max(item["mean_accuracy"] for item in summaries.values())
    eligible = [
        model_name
        for model_name, item in summaries.items()
        if best_accuracy - item["mean_accuracy"] <= ACCURACY_TOLERANCE
    ]
    return min(eligible, key=lambda name: summaries[name]["mean_fit_seconds"])


def generar_adr(
    results: list[dict[str, float | int | str | bool]],
    train_count: int,
    test_count: int,
    train_class_count: int,
    test_class_count: int,
) -> str:
    """Genera un ADR con resultados medidos y limitaciones del conjunto."""
    summaries = resumir_resultados(results)
    selected_model = seleccionar_modelo(summaries)
    best_accuracy = max(item["mean_accuracy"] for item in summaries.values())
    selected = summaries[selected_model]
    best_model = max(summaries, key=lambda name: summaries[name]["mean_accuracy"])
    score_differences = [
        f"{(summaries[best_model]['mean_accuracy'] - summary['mean_accuracy']) * 100:.2f} "
        f"puntos porcentuales frente a {model_name}"
        for model_name, summary in summaries.items()
        if model_name != best_model
    ]
    convergence_issues = [
        result
        for result in results
        if result.get("convergido", True) is False
    ]
    if convergence_issues:
        non_converged_counts: dict[str, int] = {}
        for result in convergence_issues:
            model_name = str(result["modelo"])
            non_converged_counts[model_name] = (
                non_converged_counts.get(model_name, 0) + 1
            )
        convergence_note = "; ".join(
            f"{name}: {count} ejecucion(es) sin converger"
            for name, count in sorted(non_converged_counts.items())
        )
    else:
        convergence_note = "no se detectaron avisos de falta de convergencia."

    table = [
        "| Modelo | Accuracy promedio | Desv. estándar | Tiempo promedio (s) |",
        "|---|---:|---:|---:|",
    ]
    for model_name, summary in sorted(
        summaries.items(), key=lambda item: item[1]["mean_accuracy"], reverse=True
    ):
        table.append(
            f"| {model_name} | {summary['mean_accuracy']:.4f} | "
            f"{summary['std_accuracy']:.4f} | {summary['mean_fit_seconds']:.4f} |"
        )

    model_descriptions = {
        "logistic_regression": (
            "Línea base lineal; es simple y suele entrenar rápido, pero puede no "
            "representar patrones visuales complejos."
        ),
        "random_forest": (
            "Ensamble de árboles que modela relaciones no lineales; su tamaño puede "
            "aumentar costo de memoria e inferencia y reduce la explicabilidad global."
        ),
        "mlp": (
            "Red neuronal multicapa capaz de aprender fronteras no lineales; requiere "
            "escalado y tiene mayor sensibilidad a configuración y costo de entrenamiento."
        ),
    }
    lines = [
        "# ADR Semana 11 - Selección de modelo para caracteres de placas",
        "",
        "## Contexto",
        "",
        "SecurityPlate necesita clasificar recortes anotados de caracteres de placas "
        "vehiculares. Para que la práctica evalúe datos del proyecto y no copie el "
        "ejemplo de dígitos, se usan las cajas YOLO de `data/dataset`: cada recorte "
        f"se reduce de {IMAGE_SIZE} x {IMAGE_SIZE} a "
        f"{BENCHMARK_IMAGE_SIZE} x {BENCHMARK_IMAGE_SIZE} y se aplana en un vector "
        "de intensidades normalizadas para limitar el costo computacional.",
        "",
        f"Se entrenó con {train_count} recortes del split oficial `train` y se evaluó "
        f"con {test_count} recortes del split oficial `test`. Las mismas particiones "
        f"cubren {train_class_count} clases de entrenamiento y {test_class_count} de "
        "50 clases en prueba. Se conservaron para los tres modelos y en las tres "
        "ejecuciones. Los modelos "
        "estocásticos usan semillas 42, 43 y 44. Se midió accuracy y tiempo de `fit`; "
        "la predicción no se incluye en ese tiempo.",
        "",
        "## Modelos comparados",
        "",
        "- **Logistic Regression:** línea base con `StandardScaler`.",
        "- **Random Forest:** 100 árboles de decisión.",
        "- **MLPClassifier:** una capa oculta de 64 neuronas, hasta 100 iteraciones, "
        "con `StandardScaler`.",
        "",
        "## Resultados",
        "",
        "Cada fila del CSV representa una ejecución individual; la tabla resume media "
        "y desviación estándar de accuracy, además del tiempo medio de entrenamiento.",
        "",
        *table,
        "",
        f"**Diferencias:** {best_model} superó a los otros modelos por "
        f"{' y '.join(score_differences)} en accuracy promedio.",
        "",
        f"**Convergencia:** {convergence_note}",
        "",
        f"El archivo [benchmark.csv](../artifacts/benchmark.csv) conserva "
        f"{len(results)} resultados ({len(summaries)} modelos x "
        f"{len(results) // max(1, len(summaries))} ejecuciones).",
        "",
        "## Decisión",
        "",
        f"Se selecciona provisionalmente **{selected_model}** para la siguiente "
        f"iteración: su accuracy promedio es {selected['mean_accuracy']:.4f} y su "
        f"tiempo de entrenamiento promedio es {selected['mean_fit_seconds']:.4f} s. "
        f"La regla aplicada prioriza el menor tiempo entre los modelos cuya accuracy "
        f"queda a no más de {ACCURACY_TOLERANCE:.0%} del mejor promedio "
        f"({best_model}, {best_accuracy:.4f}).",
        "",
        "Esta es una decisión de prototipado, no una selección definitiva para producción. "
        "Debe confirmarse con más datos etiquetados y con métricas por clase.",
        "",
        "## Ventajas y limitaciones",
        "",
        f"- **{selected_model}:** {model_descriptions[selected_model]}",
        "- El benchmark usa el mismo split, las mismas características y las mismas "
        "tres ejecuciones para comparar las alternativas de forma consistente.",
        f"- El test tiene {test_class_count} de 50 clases representadas; la distribución "
        "por clase es desigual. Accuracy global puede ocultar errores de clases poco "
        "frecuentes, por lo que conviene agregar F1 macro, matriz de confusión y más "
        "ejemplos antes de una decisión productiva.",
        "- El experimento clasifica recortes que ya fueron localizados y anotados. "
        "No detecta la placa, no localiza cada carácter y no reconstruye la cadena OCR.",
        "- Reducir los recortes a 16 x 16 disminuye el costo de cálculo, pero puede "
        "eliminar detalles finos que ayudan a distinguir caracteres visualmente similares.",
        "- Los nombres de las 50 clases del dataset son IDs numéricos; su semántica "
        "alfanumérica requiere validación antes de interpretar predicciones como letras "
        "o números concretos.",
        "- El tiempo depende del hardware y de la carga del equipo; las tres repeticiones "
        "permiten observar variación, pero no equivalen a una evaluación estadística extensa.",
        "",
        "## Aplicación al proyecto final",
        "",
        "El modelo seleccionado podría sustituir o servir como referencia frente a la CNN "
        "de Semana 8 para clasificar los recortes producidos por la etapa de detección. "
        "Cada predicción tendría que mapearse a un carácter validado y combinarse en "
        "secuencia para leer la placa. La autorización de ingreso/salida debe seguir "
        "dependiendo de la verificación del registro, la confianza y las reglas del "
        "sistema híbrido; esta clasificación aislada no debe tomar esa decisión.",
        "",
        "Python y scikit-learn son adecuados para este benchmark reproducible. Si el "
        "servicio final usa otro backend, el clasificador podría exponerse mediante una "
        "API, tras validar latencia, serialización, seguridad y mantenimiento.",
        "",
        "## Reproducibilidad",
        "",
        "Desde la raíz del repositorio, ejecutar `python src/semana11_benchmark.py`. "
        "El script realiza tres ejecuciones por modelo y regenera este ADR y "
        "`artifacts/benchmark.csv`.",
        "",
        "Fuente del conjunto: Roboflow, licencia CC BY 4.0; referencia y atribución "
        "en `data/dataset/README.dataset.txt`.",
        "",
    ]
    return "\n".join(lines)


def imprimir_resumen(results: list[dict[str, float | int | str | bool]]) -> None:
    summaries = resumir_resultados(results)
    print("Modelo                  Accuracy media   Desv. estándar   Fit medio (s)")
    for model_name, summary in sorted(
        summaries.items(), key=lambda item: item[1]["mean_accuracy"], reverse=True
    ):
        print(
            f"{model_name:23} {summary['mean_accuracy']:14.4f} "
            f"{summary['std_accuracy']:15.4f} "
            f"{summary['mean_fit_seconds']:14.4f}"
        )
    non_converged = [
        result for result in results if result.get("convergido", True) is False
    ]
    if non_converged:
        print(f"Aviso: {len(non_converged)} entrenamiento(s) no convergieron.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help="Ejecuciones por modelo (mínimo 3).",
    )
    args = parser.parse_args()
    if args.repeats < DEFAULT_REPEATS:
        parser.error(f"--repeats debe ser al menos {DEFAULT_REPEATS}.")

    print("Cargando recortes anotados del proyecto...")
    X_train, y_train = cargar_datos("train")
    X_test, y_test = cargar_datos("test")
    class_names = cargar_clases()
    results = ejecutar_benchmark(X_train, y_train, X_test, y_test, args.repeats)
    guardar_benchmark(results)
    report = generar_adr(
        results,
        train_count=len(y_train),
        test_count=len(y_test),
        train_class_count=len(np.unique(y_train)),
        test_class_count=len(np.unique(y_test)),
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    imprimir_resumen(results)
    print(f"Clases con nombre configurado: {len(class_names)}")
    print(f"Benchmark guardado: {BENCHMARK_PATH.relative_to(ROOT_DIR)}")
    print(f"ADR generado: {REPORT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
