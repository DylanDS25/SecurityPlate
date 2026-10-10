"""Analisis de placas con Canny, umbral de Otsu y regiones conectadas."""

import argparse
import base64
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import cv2
import numpy as np

if __package__:
    from .semana10_texturas import (
        MAX_UPLOAD_COUNT,
        analizar_cargas_temporales,
        serializar_comparacion_temporal,
    )
else:
    from semana10_texturas import (
        MAX_UPLOAD_COUNT,
        analizar_cargas_temporales,
        serializar_comparacion_temporal,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT_DIR / "data" / "imagen_proyecto.png"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
EVIDENCE_PATH = ARTIFACTS_DIR / "semana09_vision.png"
REPORT_PATH = ROOT_DIR / "reports" / "semana09.md"
MAX_IMAGE_SIDE = 1800
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_WEEK10_REQUEST_BYTES = 28 * 1024 * 1024
SIGMA_COMPARISON = (0.8, 1.6, 3.0)


def preparar_imagen(image: np.ndarray) -> np.ndarray:
    """Valida y limita el tamano de una imagen BGR o en escala de grises."""
    if image is None or image.size == 0:
        raise ValueError("La imagen esta vacia o no pudo decodificarse.")
    if image.ndim not in (2, 3) or (image.ndim == 3 and image.shape[2] not in (3, 4)):
        raise ValueError("La imagen debe tener canales de gris, BGR o BGRA.")

    height, width = image.shape[:2]
    if height < 2 or width < 2:
        raise ValueError("La imagen debe medir al menos 2 x 2 pixeles.")
    largest_side = max(height, width)
    if largest_side > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / largest_side
        image = cv2.resize(
            image,
            (round(width * scale), round(height * scale)),
            interpolation=cv2.INTER_AREA,
        )
    if image.ndim == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def _detectar_bordes(gray: np.ndarray, sigma: float) -> np.ndarray:
    if not 0.1 <= sigma <= 10:
        raise ValueError("Sigma debe estar entre 0.1 y 10.")
    kernel_size = max(3, int(round(sigma * 6)) | 1)
    softened = cv2.GaussianBlur(gray, (kernel_size, kernel_size), sigmaX=sigma)
    return cv2.Canny(softened, threshold1=50, threshold2=150)


def analizar_imagen(image: np.ndarray, sigma: float = 1.6) -> dict[str, object]:
    """Extrae caracteristicas, bordes, mascara Otsu y regiones conectadas."""
    image = preparar_imagen(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    edges = _detectar_bordes(gray, sigma)

    threshold, binary = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    foreground_is_dark = False
    mask = binary

    region_count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask, connectivity=8
    )
    minimum_area = max(30, int(mask.size * 0.0001))
    regions = [
        index
        for index in range(1, region_count)
        if stats[index, cv2.CC_STAT_AREA] >= minimum_area
    ]
    colored_regions = np.zeros((*gray.shape, 3), dtype=np.uint8)
    colors = np.random.default_rng(42).integers(65, 240, size=(region_count, 3), dtype=np.uint8)
    for region_id in regions:
        colored_regions[labels == region_id] = colors[region_id].tolist()
    source_color = image if image.ndim == 3 else cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    region_overlay = cv2.addWeighted(source_color, 0.62, colored_regions, 0.75, 0)

    height, width = gray.shape
    channel_means = cv2.mean(image)[:3] if image.ndim == 3 else (float(gray.mean()),) * 3
    comparison = []
    for comparison_sigma in SIGMA_COMPARISON:
        comparison_edges = _detectar_bordes(gray, comparison_sigma)
        comparison.append(
            {
                "sigma": comparison_sigma,
                "edge_percent": float(np.count_nonzero(comparison_edges) * 100 / comparison_edges.size),
            }
        )

    return {
        "image": image,
        "gray": gray,
        "edges": edges,
        "mask": mask,
        "regions_image": region_overlay,
        "threshold": float(threshold),
        "sigma": float(sigma),
        "foreground_is_dark": foreground_is_dark,
        "region_count": len(regions),
        "raw_region_count": region_count - 1,
        "minimum_area": minimum_area,
        "width": width,
        "height": height,
        "mean_intensity": float(gray.mean()),
        "intensity_std": float(gray.std()),
        "channel_means": channel_means,
        "edge_percent": float(np.count_nonzero(edges) * 100 / edges.size),
        "sigma_comparison": comparison,
    }


def _panel(image: np.ndarray, title: str, size: tuple[int, int] = (640, 420)) -> np.ndarray:
    width, height = size
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    fitted = cv2.resize(image, (width, height - 38), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[:] = (15, 23, 37)
    canvas[38:, :] = fitted
    cv2.putText(canvas, title, (16, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (85, 246, 210), 2, cv2.LINE_AA)
    return canvas


def guardar_evidencia(result: dict[str, object], output_path: Path = EVIDENCE_PATH) -> None:
    """Guarda una comparacion 2 x 2 de los resultados principales."""
    panels = [
        _panel(result["image"], "Imagen del proyecto"),
        _panel(result["edges"], f"Canny | sigma = {result['sigma']:.1f}"),
        _panel(result["mask"], f"Mascara Otsu | umbral = {result['threshold']:.0f}"),
        _panel(result["regions_image"], f"Regiones | {result['region_count']} filtradas"),
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    evidence = np.vstack((np.hstack(panels[:2]), np.hstack(panels[2:])))
    if not cv2.imwrite(str(output_path), evidence):
        raise OSError(f"No se pudo guardar la evidencia en {output_path}.")


def generar_reporte(result: dict[str, object], image_name: str) -> str:
    """Construye el informe Markdown desde las metricas de la ejecucion."""
    polarity = "regiones oscuras sobre fondo claro" if result["foreground_is_dark"] else "regiones claras sobre fondo oscuro"
    image_context = (
        "una fotografia de una motocicleta con placa colombiana"
        if image_name == "data/imagen_proyecto.png"
        else "una imagen proporcionada para el analisis"
    )
    comparison_rows = "\n".join(
        f"| {row['sigma']:.1f} | {row['edge_percent']:.2f}% |"
        for row in result["sigma_comparison"]
    )
    channel_means = result["channel_means"]
    return f"""# Semana 09 - Vision por computador en SecurityPlate

## Imagen y relacion con el proyecto

Se proceso `{image_name}`, {image_context}. Es pertinente para SecurityPlate porque permite analizar intensidad, contraste, bordes y regiones como etapas exploratorias previas a localizar y clasificar caracteres. La imagen procesada mide {result['width']} x {result['height']} pixeles. La intensidad media en gris es {result['mean_intensity']:.2f}, con desviacion estandar {result['intensity_std']:.2f}; las medias BGR son {channel_means[0]:.2f}, {channel_means[1]:.2f} y {channel_means[2]:.2f}.

## Deteccion de contornos con Canny

Se aplico suavizado gaussiano con sigma **{result['sigma']:.1f}** antes de Canny. Los bordes ocupan {result['edge_percent']:.2f}% de los pixeles. Los contornos resaltan cambios de intensidad que pueden delimitar placa, letras y objetos; sombras, perspectiva y texturas del vehiculo tambien producen bordes, por lo que no constituyen por si solos una deteccion de placa.

| Sigma | Pixeles de borde |
|---:|---:|
{comparison_rows}

Al aumentar sigma se suavizan detalles y ruido; puede reducir bordes espurios, pero tambien borrar trazos finos de los caracteres. El efecto depende de la iluminacion y de la resolucion de la imagen.

## Segmentacion por Otsu

**Umbral Otsu obtenido:** {result['threshold']:.0f} en escala de grises de 8 bits. La mascara binaria selecciona {polarity} (pixeles por encima del umbral). Otsu separa intensidades globales y no conoce la ubicacion de la placa; en esta escena compleja puede incluir regiones ajenas al identificador.

## Regiones conectadas

Se encontraron **{result['region_count']} regiones** con area minima de {result['minimum_area']} pixeles, de {result['raw_region_count']} componentes sin filtrar. Son grupos de pixeles de la mascara, no objetos confirmados: una letra puede fragmentarse o unirse a otra y el fondo puede generar componentes. El conteo no debe interpretarse como cantidad de caracteres.

## Evidencia visual

![Original, Canny, mascara de Otsu y regiones conectadas](../artifacts/semana09_vision.png)

El panel muestra la imagen original, los bordes, la mascara y las regiones filtradas por area.

## Limitaciones y aplicacion futura

- La placa ocupa una fraccion pequena de la escena y esta inclinada; no se aislo una region de interes ni se corrigio perspectiva.
- La iluminacion, las sombras, reflejos y texturas generan intensidades y contornos que confunden a los metodos globales.
- El umbral de Otsu supone grupos de intensidad separables; no garantiza segmentar correctamente la placa.
- El etiquetado conectado depende de la mascara y de un area minima, y no equivale a reconocimiento de caracteres.

Como siguiente etapa, la mascara y los contornos pueden apoyar la localizacion de la placa, rectificacion geometrica y extraccion de recortes. Estos recortes podrian alimentar el clasificador CNN de Semana 08, que reconoce categorias de caracteres; esta practica no realiza OCR ni autoriza decisiones de acceso.

## Ejecucion

Desde la raiz del repositorio, `python src/semana09_vision.py` procesa la imagen fija, guarda la evidencia y regenera este informe. Para usar la interfaz de carga, ejecute `python src/semana09_vision.py --serve` y abra `http://127.0.0.1:8000/dashboard/`.
"""


def ejecutar(image_path: Path = IMAGE_PATH, sigma: float = 1.6) -> dict[str, object]:
    """Procesa una imagen y actualiza la evidencia y el informe de la semana."""
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {image_path}")
    result = analizar_imagen(image, sigma=sigma)
    guardar_evidencia(result)
    try:
        image_name = image_path.resolve().relative_to(ROOT_DIR).as_posix()
    except ValueError:
        image_name = image_path.name
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(generar_reporte(result, image_name), encoding="utf-8")
    return result


def _encode_preview(image: np.ndarray) -> str:
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ValueError("No se pudo codificar la vista previa.")
    return "data:image/png;base64," + base64.b64encode(encoded).decode("ascii")


def serializar_resultado(result: dict[str, object]) -> dict[str, object]:
    return {
        "threshold": result["threshold"],
        "region_count": result["region_count"],
        "raw_region_count": result["raw_region_count"],
        "minimum_area": result["minimum_area"],
        "sigma": result["sigma"],
        "edge_percent": result["edge_percent"],
        "mean_intensity": result["mean_intensity"],
        "intensity_std": result["intensity_std"],
        "foreground_is_dark": result["foreground_is_dark"],
        "sigma_comparison": result["sigma_comparison"],
        "previews": {
            "original": _encode_preview(result["image"]),
            "edges": _encode_preview(result["edges"]),
            "mask": _encode_preview(result["mask"]),
            "regions": _encode_preview(result["regions_image"]),
        },
    }


class Semana09Handler(SimpleHTTPRequestHandler):
    """Sirve el dashboard y analiza imagenes cargadas por la interfaz."""

    default_result: dict[str, object] | None = None

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/api/default":
            if self.default_result is None:
                self.send_error(503, "Ejecute el modulo con --serve para cargar el analisis base.")
                return
            payload = json.dumps(serializar_resultado(self.default_result)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def do_POST(self) -> None:
        request = urlsplit(self.path)
        if request.path == "/api/week10/analyze":
            self._analizar_cargas_semana10()
            return
        if request.path != "/api/analyze":
            self.send_error(404)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if not 0 < content_length <= MAX_UPLOAD_BYTES:
                raise ValueError("La imagen debe pesar menos de 20 MB.")
            encoded = self.rfile.read(content_length)
            image = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("No se pudo abrir la imagen. Usa PNG, JPG o una imagen compatible.")
            query = parse_qs(request.query)
            sigma = float(query.get("sigma", ["1.6"])[0])
            result = analizar_imagen(image, sigma=sigma)
            response = serializar_resultado(result)
            payload = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (ValueError, cv2.error) as error:
            payload = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _analizar_cargas_semana10(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if not 0 < content_length <= MAX_WEEK10_REQUEST_BYTES:
                raise ValueError("El total de la solicitud no puede superar 20 MB.")
            if self.headers.get_content_type() != "application/json":
                raise ValueError("La solicitud debe contener imagenes en formato JSON.")

            encoded = self.rfile.read(content_length)
            if len(encoded) != content_length:
                raise ValueError("La solicitud de imagenes esta incompleta.")
            request_data = json.loads(encoded.decode("utf-8"))
            if not isinstance(request_data, dict):
                raise ValueError("La solicitud debe incluir una lista de imagenes.")
            uploads = request_data.get("images")
            if not isinstance(uploads, list) or not 2 <= len(uploads) <= MAX_UPLOAD_COUNT:
                raise ValueError(
                    f"Selecciona entre 2 y {MAX_UPLOAD_COUNT} imagenes para comparar."
                )
            results = analizar_cargas_temporales(uploads)
            payload = json.dumps(
                serializar_comparacion_temporal(results)
            ).encode("utf-8")
            self.send_response(200)
        except (OSError, UnicodeError, ValueError) as error:
            payload = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(400)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def servir(
    host: str = "127.0.0.1",
    port: int = 8000,
    default_result: dict[str, object] | None = None,
) -> None:
    Semana09Handler.default_result = default_result
    handler = partial(Semana09Handler, directory=str(ROOT_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Dashboard disponible en http://{host}:{port}/dashboard/")
    print("Presione Ctrl+C para detener el servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE_PATH, help="Imagen de entrada para generar la evidencia")
    parser.add_argument("--sigma", type=float, default=1.6, help="Suavizado de Canny entre 0.1 y 10")
    parser.add_argument("--serve", action="store_true", help="Genera el reporte y sirve el dashboard con analisis interactivo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    result = ejecutar(args.image, args.sigma)
    print(f"Umbral Otsu: {result['threshold']:.0f}")
    print(f"Regiones conectadas: {result['region_count']} (area minima {result['minimum_area']} px)")
    print(f"Evidencia guardada: {EVIDENCE_PATH.relative_to(ROOT_DIR)}")
    print(f"Reporte generado: {REPORT_PATH.relative_to(ROOT_DIR)}")
    if args.serve:
        servir(args.host, args.port, result)


if __name__ == "__main__":
    main()