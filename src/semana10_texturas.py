"""Extrae caracteristicas de placas con Otsu, regiones conectadas y LBP."""

from dataclasses import dataclass
from io import BytesIO
from itertools import combinations
from pathlib import Path
from threading import Lock
from typing import Sequence
import base64
import binascii
import re

import matplotlib
import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage import color, io, measure, transform, util
from skimage.feature import local_binary_pattern
from skimage.filters import threshold_otsu

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
REPORT_PATH = ROOT_DIR / "reports" / "semana10.md"
FEATURES_PATH = ARTIFACTS_DIR / "semana10_features.npy"
FIGURE_PATH = ARTIFACTS_DIR / "semana10_histograma.png"

MAX_IMAGE_SIDE = 1200
MAX_IMAGE_PIXELS = 20_000_000
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_UPLOAD_COUNT = 4
INTENSITY_BINS = 32
LBP_RADIUS = 2
LBP_POINTS = 8 * LBP_RADIUS
PLOT_LOCK = Lock()


@dataclass(frozen=True)
class ImageSpec:
    path: Path
    title: str
    description: str


@dataclass(frozen=True)
class ImageAnalysis:
    source: str
    title: str
    description: str
    gray: np.ndarray
    mask: np.ndarray
    filtered_labels: np.ndarray
    lbp: np.ndarray
    threshold: float
    minimum_area: int
    raw_region_count: int
    region_count: int
    area_mean: float
    area_std: float
    intensity_histogram: np.ndarray
    lbp_histogram: np.ndarray
    features: np.ndarray


IMAGE_SPECS = (
    ImageSpec(
        ROOT_DIR
        / "data"
        / "dataset"
        / "test"
        / "images"
        / "plate_1677361962348_Screenshot-2023-02-05-at-12-27-46-AM_png_jpg.rf.d9JVDwlw2brvnOx9gIKk.jpg",
        "Placa A · caracteres claros",
        "Placa colombiana de fondo oscuro con caracteres claros, anotada en el conjunto de prueba.",
    ),
    ImageSpec(
        ROOT_DIR
        / "data"
        / "dataset"
        / "test"
        / "images"
        / "plate_1677361962434_Screenshot-2023-02-05-at-12-27-04-AM_png_jpg.rf.TwbpUZbY11NUMFfgA3NA.jpg",
        "Placa B · caracteres oscuros",
        "Placa colombiana clara con caracteres oscuros, anotada en el conjunto de prueba.",
    ),
)


def cargar_imagen_gris(image_path: Path) -> np.ndarray:
    """Lee una imagen y la prepara como intensidades uint8 en escala de grises."""
    if not image_path.is_file():
        raise FileNotFoundError(f"No se encontro la imagen: {image_path}")

    image = io.imread(image_path)
    return preparar_imagen_gris(image)


def preparar_imagen_gris(image: np.ndarray) -> np.ndarray:
    """Normaliza una imagen RGB, RGBA o gris y limita sus dimensiones."""
    if image.size == 0:
        raise ValueError("La imagen esta vacia o no pudo decodificarse.")

    if image.ndim == 3:
        if image.shape[2] == 4:
            image = color.rgba2rgb(image)
        elif image.shape[2] != 3:
            raise ValueError(f"Numero de canales no compatible: {image.shape[2]}")
        image = color.rgb2gray(image)
    elif image.ndim != 2:
        raise ValueError("La imagen debe ser gris, RGB o RGBA.")

    gray = util.img_as_ubyte(image)
    height, width = gray.shape
    largest_side = max(height, width)
    if largest_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / largest_side
        resized = transform.resize(
            gray,
            (max(1, round(height * scale)), max(1, round(width * scale))),
            preserve_range=True,
            anti_aliasing=True,
        )
        gray = np.clip(resized, 0, 255).astype(np.uint8)
    return gray


def analizar_imagen_subida(data_url: str, title: str) -> ImageAnalysis:
    """Decodifica una imagen subida y la analiza sin escribir archivos."""
    image_bytes = decodificar_imagen_subida(data_url)
    image = leer_imagen_subida(image_bytes, title)
    gray = preparar_imagen_gris(image)
    return analizar_imagen(
        gray,
        title=title,
        description="Imagen subida para esta comparacion temporal.",
        source=title,
    )


def decodificar_imagen_subida(data_url: str) -> bytes:
    """Valida el formato de una imagen codificada y limita su tamano."""
    match = re.fullmatch(
        r"data:image/(?:png|jpeg|webp);base64,([A-Za-z0-9+/]*={0,2})",
        data_url,
    )
    if match is None:
        raise ValueError("Usa imagenes PNG, JPG o WebP validas.")

    try:
        image_bytes = base64.b64decode(match.group(1), validate=True)
    except binascii.Error as error:
        raise ValueError("No se pudo decodificar una de las imagenes.") from error
    if not image_bytes:
        raise ValueError("El archivo de imagen esta vacio.")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError("Cada imagen debe pesar menos de 20 MB.")
    return image_bytes


def leer_imagen_subida(image_bytes: bytes, title: str) -> np.ndarray:
    """Decodifica una imagen compatible con limites de formato y resolucion."""
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            if image.format not in {"PNG", "JPEG", "WEBP"}:
                raise ValueError(f"Formato no compatible en {title}. Usa PNG, JPG o WebP.")
            width, height = image.size
            if width < 2 or height < 2:
                raise ValueError(f"La imagen {title} debe medir al menos 2 x 2 pixeles.")
            if width * height > MAX_IMAGE_PIXELS:
                raise ValueError(f"La imagen {title} supera el limite de 20 megapixeles.")
            image.thumbnail(
                (MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS
            )
            return np.asarray(image.convert("RGB"))
    except (Image.DecompressionBombError, OSError, UnidentifiedImageError) as error:
        raise ValueError(f"No se pudo decodificar la imagen {title}.") from error


def analizar_cargas_temporales(uploads: object) -> list[ImageAnalysis]:
    """Valida y procesa de dos a cuatro imagenes recibidas por la interfaz."""
    if not isinstance(uploads, list) or not 2 <= len(uploads) <= MAX_UPLOAD_COUNT:
        raise ValueError(
            f"Selecciona entre 2 y {MAX_UPLOAD_COUNT} imagenes para comparar."
        )

    results = []
    total_bytes = 0
    for upload in uploads:
        if not isinstance(upload, dict):
            raise ValueError("Cada archivo debe incluir nombre e imagen.")
        title = upload.get("name")
        data_url = upload.get("data")
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError("Cada imagen debe tener un nombre valido.")
        if not isinstance(data_url, str):
            raise ValueError("Faltan los datos de una imagen.")

        image_bytes = decodificar_imagen_subida(data_url)
        total_bytes += len(image_bytes)
        if total_bytes > MAX_UPLOAD_BYTES:
            raise ValueError("El tamano total de las imagenes no puede superar 20 MB.")
        image = leer_imagen_subida(image_bytes, title)
        gray = preparar_imagen_gris(image)
        results.append(
            analizar_imagen(
                gray,
                title=title.strip(),
                description="Imagen subida para esta comparacion temporal.",
                source=title.strip(),
            )
        )
    return results


def analizar_imagen(
    image: np.ndarray,
    title: str,
    description: str,
    source: str = "imagen en memoria",
) -> ImageAnalysis:
    """Segmenta una imagen y calcula caracteristicas de regiones, intensidad y LBP."""
    if image.ndim != 2 or image.size == 0:
        raise ValueError("La imagen debe ser una matriz gris no vacia.")
    if image.dtype != np.uint8:
        image = util.img_as_ubyte(image)

    threshold = float(threshold_otsu(image))
    mask = image > threshold
    labels = measure.label(mask, connectivity=2)
    regions = measure.regionprops(labels)
    minimum_area = max(10, int(image.size * 0.0001))
    retained_regions = [region for region in regions if region.area >= minimum_area]
    retained_labels = [region.label for region in retained_regions]
    filtered_labels = np.where(np.isin(labels, retained_labels), labels, 0)
    areas = np.asarray([region.area for region in retained_regions], dtype=np.float32)
    area_mean = float(areas.mean()) if areas.size else 0.0
    area_std = float(areas.std()) if areas.size else 0.0

    intensity_counts, _ = np.histogram(
        image.ravel(), bins=INTENSITY_BINS, range=(0, 256)
    )
    intensity_histogram = intensity_counts.astype(np.float32)
    intensity_histogram /= intensity_histogram.sum()

    lbp = local_binary_pattern(
        image, LBP_POINTS, LBP_RADIUS, method="uniform"
    )
    lbp_counts, _ = np.histogram(
        lbp.ravel(), bins=np.arange(0, LBP_POINTS + 3)
    )
    lbp_histogram = lbp_counts.astype(np.float32)
    lbp_histogram /= lbp_histogram.sum()

    features = np.concatenate(
        (
            np.asarray(
                [area_mean, area_std, len(retained_regions)], dtype=np.float32
            ),
            intensity_histogram,
            lbp_histogram,
        )
    )
    return ImageAnalysis(
        source=source,
        title=title,
        description=description,
        gray=image,
        mask=mask,
        filtered_labels=filtered_labels,
        lbp=lbp,
        threshold=threshold,
        minimum_area=minimum_area,
        raw_region_count=len(regions),
        region_count=len(retained_regions),
        area_mean=area_mean,
        area_std=area_std,
        intensity_histogram=intensity_histogram,
        lbp_histogram=lbp_histogram,
        features=features,
    )


def guardar_evidencia(results: Sequence[ImageAnalysis]) -> None:
    """Guarda comparaciones de imagen, mascara, regiones e histogramas."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with PLOT_LOCK:
        figure = crear_figura_comparativa(results)
        try:
            figure.savefig(FIGURE_PATH, dpi=160)
        finally:
            plt.close(figure)


def crear_figura_comparativa(results: Sequence[ImageAnalysis]) -> plt.Figure:
    """Crea la figura de comparacion sin decidir donde se persiste."""
    figure, axes = plt.subplots(
        len(results), 6, figsize=(18, 4.2 * len(results)), squeeze=False
    )
    for row, result in enumerate(results):
        image_axis, mask_axis, regions_axis, intensity_axis, lbp_axis, lbp_hist_axis = axes[row]
        image_axis.imshow(result.gray, cmap="gray", vmin=0, vmax=255)
        image_axis.set_title(f"{result.title}\nImagen en escala de grises")
        mask_axis.imshow(result.mask, cmap="gray")
        mask_axis.set_title(f"Máscara Otsu · umbral {result.threshold:.0f}")
        regions_axis.imshow(result.filtered_labels, cmap="nipy_spectral")
        regions_axis.set_title(f"Regiones filtradas · {result.region_count}")

        intensity_centers = np.linspace(0, 256, INTENSITY_BINS + 1)[:-1] + (
            256 / (2 * INTENSITY_BINS)
        )
        intensity_axis.plot(intensity_centers, result.intensity_histogram)
        intensity_axis.set_title("Histograma de intensidad")
        intensity_axis.set_xlabel("Intensidad (0–255)")
        intensity_axis.set_ylabel("Proporción")

        lbp_axis.imshow(result.lbp, cmap="magma")
        lbp_axis.set_title("Patrones locales LBP")
        lbp_hist_axis.bar(
            np.arange(result.lbp_histogram.size), result.lbp_histogram
        )
        lbp_hist_axis.set_title("Histograma LBP")
        lbp_hist_axis.set_xlabel("Código LBP uniforme")
        lbp_hist_axis.set_ylabel("Proporción")

        for axis in (image_axis, mask_axis, regions_axis, lbp_axis):
            axis.set_axis_off()

    figure.tight_layout()
    return figure


def serializar_comparacion_temporal(
    results: Sequence[ImageAnalysis],
) -> dict[str, object]:
    """Devuelve metricas y vista previa para la interfaz, sin guardar resultados."""
    if not 2 <= len(results) <= MAX_UPLOAD_COUNT:
        raise ValueError(
            f"Selecciona entre 2 y {MAX_UPLOAD_COUNT} imagenes para comparar."
        )

    buffer = BytesIO()
    with PLOT_LOCK:
        figure = crear_figura_comparativa(results)
        try:
            figure.savefig(buffer, format="png", dpi=100)
        finally:
            plt.close(figure)

    comparisons = [
        {
            "first": first.title,
            "second": second.title,
            "lbp_distance": float(
                np.abs(first.lbp_histogram - second.lbp_histogram).sum()
            ),
        }
        for first, second in combinations(results, 2)
    ]
    return {
        "images": [
            {
                "name": result.title,
                "threshold": result.threshold,
                "selected_percent": float(
                    np.count_nonzero(result.mask) * 100 / result.mask.size
                ),
                "region_count": result.region_count,
                "raw_region_count": result.raw_region_count,
                "minimum_area": result.minimum_area,
                "area_mean": result.area_mean,
                "area_std": result.area_std,
            }
            for result in results
        ],
        "comparisons": comparisons,
        "preview": (
            "data:image/png;base64,"
            + base64.b64encode(buffer.getvalue()).decode("ascii")
        ),
    }


def generar_reporte(results: Sequence[ImageAnalysis]) -> str:
    """Genera el informe semanal usando las metricas calculadas."""
    if len(results) < 2:
        raise ValueError("El informe requiere al menos dos imagenes.")

    image_rows = "\n".join(
        f"| {result.title} | `{result.source}` | {result.description} |"
        for result in results
    )
    metric_rows = "\n".join(
        (
            f"| {result.title} | {result.threshold:.2f} | "
            f"{np.count_nonzero(result.mask) * 100 / result.mask.size:.2f}% | "
            f"{result.minimum_area} | {result.raw_region_count} | "
            f"{result.region_count} | "
            f"{result.area_mean:.2f} | {result.area_std:.2f} |"
        )
        for result in results
    )
    comparison_rows = "\n".join(
        (
            f"| {first.title} vs. {second.title} | "
            f"{np.abs(first.lbp_histogram - second.lbp_histogram).sum():.4f} |"
        )
        for first, second in combinations(results, 2)
    )
    feature_length = results[0].features.size
    image_count = len(results)

    return f"""# Semana 10 - Segmentacion, regiones y texturas en SecurityPlate

## Objetivo y relacion con el proyecto

Se analizaron {image_count} imagenes de placas colombianas del conjunto de prueba de SecurityPlate. Este paso complementa la exploracion de bordes y regiones de Semana 09 y describe numericamente la intensidad, el tamano de componentes conectados y la textura local. Los descriptores pueden servir como evidencia exploratoria para priorizar recortes o comparar condiciones visuales antes del reconocimiento de caracteres de Semana 08; por si solos no localizan una placa ni realizan OCR.

Las imagenes proceden del conjunto de placas colombianas usado por el proyecto, distribuido bajo licencia CC BY 4.0. Fuente: [Roboflow Universe - placas colombianas](https://universe.roboflow.com/dylan-leonardo-duitama-soriano/placas-colombianas-ohtrf).

## Imagenes seleccionadas

| Imagen | Archivo | Que representa |
|---|---|---|
{image_rows}

## Segmentacion por intensidad y regiones

Para cada imagen se calculo un histograma de 32 intervalos sobre intensidades de 0 a 255. El umbral de Otsu se calcula automaticamente a partir de ese histograma y la mascara selecciona los pixeles **por encima** del umbral. Esta separacion global permite observar grupos de intensidades, pero no identifica semantica: los pixeles claros pueden pertenecer a letras, bordes de la placa o al fondo.

Se etiquetaron componentes con `measure.label(..., connectivity=2)`. `regionprops()` midio las regiones y se conservaron las de area igual o mayor al umbral minimo relativo indicado para cada imagen (0.01% del area, con minimo de 10 pixeles).

| Imagen | Umbral Otsu | Pixeles seleccionados | Area minima (px) | Regiones antes del filtro | Regiones conservadas | Area media (px) | Desviacion estandar (px) |
|---|---:|---:|---:|---:|---:|---:|
{metric_rows}

El area media resume el tamano de las regiones que superan el filtro y la desviacion estandar expresa su variabilidad. Las componentes son grupos de pixeles conectados, no objetos ni caracteres confirmados.

## Comparacion de texturas LBP

Se calculo LBP uniforme con radio {LBP_RADIUS} y {LBP_POINTS} vecinos por pixel. El histograma resume la frecuencia relativa de cada codigo. La distancia L1 entre histogramas de cada par se muestra abajo; valores cercanos a 0 indican distribuciones mas parecidas y valores mayores indican una diferencia mas marcada.

| Comparacion | Distancia L1 LBP |
|---|---:|
{comparison_rows}

Las diferencias observadas describen los patrones locales de claro y oscuro presentes en cada imagen. No implican por si solas que una placa sea mas legible: el encuadre, el contraste, la iluminacion, los reflejos y la escala tambien alteran los codigos LBP.

## Vector de caracteristicas y evidencia

Cada imagen se representa con {feature_length} valores en este orden: area media, desviacion estandar del area, cantidad de regiones conservadas, histograma de intensidad de {INTENSITY_BINS} intervalos e histograma LBP de {results[0].lbp_histogram.size} codigos. `artifacts/semana10_features.npy` contiene una matriz de forma ({image_count}, {feature_length}); cada fila corresponde a una imagen en el mismo orden de las tablas. Los histogramas se normalizan a proporciones para que sean comparables aunque cambie el numero de pixeles.

La figura compara por imagen la escala de grises, mascara de Otsu, etiquetas filtradas, histograma de intensidad, mapa LBP e histograma LBP.

![Comparacion de histogramas, segmentacion, regiones y textura LBP](../artifacts/semana10_histograma.png)

## Limitaciones y aplicacion futura

- Otsu usa un unico umbral global y no distingue la placa del fondo. Reflejos, sombras y variaciones de iluminacion pueden invertir o fragmentar las regiones.
- El umbral de area elimina componentes pequenos, pero puede descartar trazos delgados de caracteres o conservar ruido grande.
- La cantidad y el area de regiones dependen del tamano, contraste y resolucion de la imagen; no equivalen a una deteccion de objetos.
- LBP resume patrones locales y pierde su ubicacion. Diferencias de escala, rotacion, enfoque y contraste afectan la comparacion.
- El vector es un descriptor exploratorio, no un clasificador ni una lectura de matricula. La autorizacion de acceso requiere las etapas de reconocimiento y reglas del sistema.

En una etapa posterior, estos valores podrian combinarse con calidad de imagen o predicciones de la CNN para analizar recortes de placa. Primero se debe validar esa utilidad con datos etiquetados y una evaluacion separada; esta practica no modifica el modelo ni decide accesos.

## Ejecucion reproducible

Desde la raiz del repositorio, ejecute `python src/semana10_texturas.py`. El script procesa las dos imagenes preseleccionadas y regenera `artifacts/semana10_features.npy`, `artifacts/semana10_histograma.png` y este informe.
"""


def ejecutar(image_specs: Sequence[ImageSpec] = IMAGE_SPECS) -> list[ImageAnalysis]:
    """Procesa las imagenes seleccionadas y guarda los entregables semanales."""
    if len(image_specs) < 2:
        raise ValueError("La Semana 10 requiere analizar al menos dos imagenes.")

    results = [
        analizar_imagen(
            cargar_imagen_gris(spec.path),
            title=spec.title,
            description=spec.description,
            source=spec.path.relative_to(ROOT_DIR).as_posix(),
        )
        for spec in image_specs
    ]

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    np.save(FEATURES_PATH, np.stack([result.features for result in results]))
    guardar_evidencia(results)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(generar_reporte(results), encoding="utf-8")

    for result in results:
        print(
            f"{result.title}: Otsu={result.threshold:.0f}, "
            f"regiones={result.region_count}/{result.raw_region_count}, "
            f"area_media={result.area_mean:.2f}, area_std={result.area_std:.2f}"
        )
    print(f"Dimension de la matriz de caracteristicas: ({len(results)}, {results[0].features.size})")
    print(f"Guardado: {FEATURES_PATH.relative_to(ROOT_DIR).as_posix()}")
    print(f"Guardado: {FIGURE_PATH.relative_to(ROOT_DIR).as_posix()}")
    print(f"Guardado: {REPORT_PATH.relative_to(ROOT_DIR).as_posix()}")
    return results


if __name__ == "__main__":
    ejecutar()
