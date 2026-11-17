"""Repositorio de Conocimiento Empresarial - SecurityPlate.

Semana 15: Organizacion de base de conocimiento en la empresa, dominios,
aplicaciones, recursos humanos y herramientas de desarrollo.
"""

from contextlib import contextmanager
from datetime import date
from pathlib import Path
import sqlite3

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "conocimiento.db"


@contextmanager
def conectar(ruta=RUTA_DB):
    """Gestor de contexto para abrir y cerrar conexiones SQLite de forma segura."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar(ruta=RUTA_DB):
    """Crea las tablas a partir del esquema y carga los datos iniciales."""
    with conectar(ruta) as conexion:
        esquema_sql = (RAIZ / "sql" / "esquema.sql").read_text(encoding="utf-8")
        datos_sql = (RAIZ / "sql" / "datos.sql").read_text(encoding="utf-8")
        conexion.executescript(esquema_sql)
        conexion.executescript(datos_sql)


def buscar_articulos(dominio, ruta=RUTA_DB):
    """Consulta articulos aprobados (estado = VALIDADO) pertenecientes a un dominio.

    Aplica SQL JOIN para relacionar articulos con dominios, expertos,
    aplicaciones y herramientas del sistema SecurityPlate.
    """
    consulta = """
        SELECT a.id,
               a.titulo,
               a.contenido,
               d.nombre AS dominio,
               p.nombre AS responsable,
               p.cargo AS cargo_responsable,
               ap.nombre AS aplicacion,
               h.nombre AS herramienta,
               a.fuente,
               a.fecha_revision,
               a.estado
        FROM articulo a
        JOIN dominio d ON d.id = a.dominio_id
        JOIN experto p ON p.id = a.experto_id
        LEFT JOIN aplicacion ap ON ap.id = a.aplicacion_id
        LEFT JOIN herramienta h ON h.id = a.herramienta_id
        WHERE d.nombre = ? AND a.estado = 'VALIDADO'
        ORDER BY a.titulo
    """
    with conectar(ruta) as conexion:
        filas = conexion.execute(consulta, (dominio,)).fetchall()
        return [dict(fila) for fila in filas]


def registrar_articulo(
    titulo,
    contenido,
    dominio_id,
    experto_id,
    fuente,
    aplicacion_id=None,
    herramienta_id=None,
    ruta=RUTA_DB,
):
    """Registra un nuevo articulo con estado inicial obligatorio 'BORRADOR'.

    Valida que titulo, contenido y fuente no sean cadenas vacias o espacios.
    Lanza IntegrityError si las claves foraneas (dominio_id, experto_id) no existen.
    """
    if not titulo or not titulo.strip():
        raise ValueError("El titulo es obligatorio y no puede estar vacio.")
    if not contenido or not contenido.strip():
        raise ValueError("El contenido es obligatorio y no puede estar vacio.")
    if not fuente or not fuente.strip():
        raise ValueError("La fuente es obligatoria y no puede estar vacia.")

    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            """INSERT INTO articulo
               (titulo, contenido, dominio_id, aplicacion_id, experto_id,
                herramienta_id, fuente, fecha_revision, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR')""",
            (
                titulo.strip(),
                contenido.strip(),
                dominio_id,
                aplicacion_id,
                experto_id,
                herramienta_id,
                fuente.strip(),
                date.today().isoformat(),
            ),
        )
        return cursor.lastrowid


def validar_articulo(articulo_id, ruta=RUTA_DB):
    """Aprueba un articulo existente cambiando su estado a 'VALIDADO'."""
    with conectar(ruta) as conexion:
        cursor = conexion.execute(
            "UPDATE articulo SET estado = 'VALIDADO' WHERE id = ?",
            (articulo_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Articulo con id {articulo_id} no encontrado.")


def obtener_articulo(articulo_id, ruta=RUTA_DB):
    """Obtiene cualquier articulo por ID con su detalle y estado actual."""
    consulta = """
        SELECT a.id,
               a.titulo,
               a.contenido,
               d.nombre AS dominio,
               p.nombre AS responsable,
               p.cargo AS cargo_responsable,
               ap.nombre AS aplicacion,
               h.nombre AS herramienta,
               a.fuente,
               a.fecha_revision,
               a.estado
        FROM articulo a
        JOIN dominio d ON d.id = a.dominio_id
        JOIN experto p ON p.id = a.experto_id
        LEFT JOIN aplicacion ap ON ap.id = a.aplicacion_id
        LEFT JOIN herramienta h ON h.id = a.herramienta_id
        WHERE a.id = ?
    """
    with conectar(ruta) as conexion:
        fila = conexion.execute(consulta, (articulo_id,)).fetchone()
        if fila is None:
            raise ValueError(f"Articulo con id {articulo_id} no encontrado.")
        return dict(fila)


def listar_dominios(ruta=RUTA_DB):
    """Retorna los nombres de todos los dominios registrados."""
    with conectar(ruta) as conexion:
        filas = conexion.execute("SELECT nombre FROM dominio ORDER BY id").fetchall()
        return [fila["nombre"] for fila in filas]


# ====================================================================
# Semana 16: Catalogo de Referencias para el Motor de Busqueda
# ====================================================================

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


if __name__ == "__main__":
    print("=" * 70)
    print("SISTEMA DE GESTION DE CONOCIMIENTO - PROYECTO SECURITYPLATE")
    print("Semana 15: Organizacion y Gobernanza del Conocimiento")
    print("=" * 70)

    # 1. Inicializar base de datos
    inicializar()
    print("\n[1] Base de datos inicializada en:", RUTA_DB)

    # 2. Consultar articulos validados iniciales por dominio
    dominios = listar_dominios()
    print(f"\n[2] Dominios registrados en SecurityPlate: {dominios}")

    dominio_demo = "Vision por Computador"
    print(f"\n[3] Articulos VALIDADOS del dominio '{dominio_demo}':")
    validados = buscar_articulos(dominio_demo)
    for art in validados:
        print(f"  * [{art['estado']}] {art['titulo']}")
        print(f"    Responsable: {art['responsable']} ({art['cargo_responsable']})")
        print(f"    Fuente     : {art['fuente']}")
        print(f"    Aplicacion : {art['aplicacion']} | Herramienta: {art['herramienta']}\n")

    # 3. Demostracion de ciclo de vida: Registro -> BORRADOR -> Validacion -> Consulta
    print("-" * 70)
    print("[4] Demostracion del ciclo de vida editorial de un articulo:")
    print("-" * 70)

    dominio_nuevo = "Control de Acceso Vehicular"
    nuevo_id = registrar_articulo(
        titulo="Guia de calibracion de sensores de barrera",
        contenido="Procedimiento de ajuste milimetrico de fotoceldas y lazos inductivos para asegurar la sincronizacion con la camara de salida.",
        dominio_id=2,
        experto_id=3,
        aplicacion_id=4,
        herramienta_id=3,
        fuente="Manual de Mantenimiento de Barreras Físicas 2026",
    )
    articulo_creado = obtener_articulo(nuevo_id)
    print(f"-> Articulo #{nuevo_id} registrado exitosamente.")
    print(f"   Titulo       : '{articulo_creado['titulo']}'")
    print(f"   Estado inicial: '{articulo_creado['estado']}' (Comprobacion de BORRADOR)")

    # Comprobar que aun NO aparece en las busquedas publicas
    articulos_antes = buscar_articulos(dominio_nuevo)
    titulos_antes = [a["titulo"] for a in articulos_antes]
    print(f"\n-> Consulta en '{dominio_nuevo}' antes de validar:")
    print(f"   Total articulos validados visibles: {len(articulos_antes)}")
    print(f"   ¿Aparece el nuevo articulo?: {articulo_creado['titulo'] in titulos_antes} (esperado: False)")

    # 4. Validar el articulo
    print("\n-> Validando el articulo mediante aprobacion de experto...")
    validar_articulo(nuevo_id)
    articulo_validado = obtener_articulo(nuevo_id)
    print(f"   Nuevo estado del articulo #{nuevo_id}: '{articulo_validado['estado']}'")

    # 5. Comprobar que AHORA SI aparece en las busquedas
    articulos_despues = buscar_articulos(dominio_nuevo)
    titulos_despues = [a["titulo"] for a in articulos_despues]
    print(f"\n-> Consulta en '{dominio_nuevo}' despues de validar:")
    print(f"   Total articulos validados visibles: {len(articulos_despues)}")
    print(f"   ¿Aparece el nuevo articulo?: {articulo_creado['titulo'] in titulos_despues} (esperado: True)")

    for art in articulos_despues:
        print(f"   - {art['titulo']} | Responsable: {art['responsable']} | Estado: {art['estado']}")

    print("\n" + "=" * 70)
    print("Demostracion finalizada con exito.")
    print("=" * 70)
