"""Base de conocimiento y catalogo de referencias tecnicas de SecurityPlate.

Semana 16: Diseño de sistemas inteligentes - Arquitectura y motor de referencia.
Integra y extiende el conocimiento de la Semana 15 con metadatos de palabras clave
y fuentes verificadas para recuperacion de informacion con trazabilidad.
"""

from pathlib import Path
import sys

# Permitir acceso a las utilidades SQLite de la Semana 15 si se ubica en src/
RAIZ = Path(__file__).resolve().parent
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

try:
    from base_conocimiento import (
        buscar_articulos,
        conectar,
        inicializar,
        obtener_articulo,
        registrar_articulo,
        validar_articulo,
    )
except ImportError:
    pass


# Catalogo estructurado de referencias para el motor de recuperacion
# Contiene identificador unico, titulo, palabras clave normalizadas, respuesta, fuente y estado de validacion.
REFERENCIAS = [
    {
        "id": "REF-SEC-001",
        "titulo": "Captura y preprocesamiento de placas vehiculares",
        "claves": ["captura", "camara", "preprocesamiento", "filtro", "placa", "otsu", "canny", "recorte"],
        "respuesta": "Al ingresar un vehiculo, la camara captura la placa frontal; se convierte a escala de grises, se aplica umbralizacion Otsu y deteccion Canny, y se recortan los caracteres normalizados a 32x32 pixeles para el OCR.",
        "fuente": "Manual de Percepcion Visual SecurityPlate v2.1",
        "validada": True,
    },
    {
        "id": "REF-SEC-002",
        "titulo": "Criterios de umbral para calidad de imagen y confianza OCR",
        "claves": ["umbral", "calidad", "confianza", "ocr", "imagen", "iluminacion", "desenfoque"],
        "respuesta": "Se requiere un factor de calidad_imagen >= 0.80 y confianza_ocr >= 0.85 para admitir una lectura automatica. Valores inferiores suspenden la decision automatica y disparan alerta de baja calidad.",
        "fuente": "Especificacion Tecnica de Umbrales Semanas 08-10",
        "validada": True,
    },
    {
        "id": "REF-SEC-003",
        "titulo": "Protocolo de autorizacion de salida vehicular IPCS",
        "claves": ["autorizacion", "salida", "protocolo", "ipcs", "secuencia", "conductor", "coincidencia", "ingreso"],
        "respuesta": "La autorizacion automatica exige la ejecucion secuencial del protocolo IPCS (Ingreso, Placa, Conductor, Salida), registro de ingreso activo, coincidencia total de placa y conductor verificado mediante reglas R1 a R7.",
        "fuente": "Reglas de Inferencia R1-R7 Semana 13",
        "validada": True,
    },
    {
        "id": "REF-SEC-004",
        "titulo": "Auditoria forense y resguardo de evidencia en SQLite",
        "claves": ["auditoria", "evidencia", "sqlite", "registro", "trazabilidad", "fotografia", "historico"],
        "respuesta": "Toda transaccion de ingreso y salida almacena en SQLite el identificador de caso, marca de tiempo ISO, probabilidad calculada, recorte de placa y decision del sistema para facilitar auditorias.",
        "fuente": "Politica Corporativa de Trazabilidad y Evidencias",
        "validada": True,
    },
    {
        "id": "REF-SEC-005",
        "titulo": "Clasificacion de caracteres con red neuronal CNN",
        "claves": ["cnn", "caracteres", "clasificador", "neuronal", "pytorch", "entrenamiento", "prediccion"],
        "respuesta": "El reconocimiento optico utiliza una red convolucional compacta de 3 capas con pooling y ReLU implementada en PyTorch, clasificada sobre 50 categorias de caracteres de placas.",
        "fuente": "Arquitectura de Reconocimiento CNN Semana 08",
        "validada": True,
    },
    {
        "id": "REF-SEC-006",
        "titulo": "Protocolo experimental de apertura de barrera con placas deterioradas",
        "claves": ["barrera", "deteriorada", "apertura", "manual", "forzada", "ilegible"],
        "respuesta": "Procedimiento borrador experimental no aprobado: apertura provisional de barrera con confirmacion verbal del conductor.",
        "fuente": "Borrador no validado de contingencias v0.1",
        "validada": False,
    },
    {
        "id": "REF-SEC-007",
        "titulo": "Uso de reconocimiento facial en salida sin imagen de ingreso",
        "claves": ["facial", "biometria", "rostro", "sin_ingreso"],
        "respuesta": "Propuesta no aprobada: permitir salida comparando con documento de identidad externo sin respaldo de imagen de ingreso.",
        "fuente": "Propuesta preliminar de biometria (No aprobada)",
        "validada": False,
    },
]
