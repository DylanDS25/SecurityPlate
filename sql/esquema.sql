-- ====================================================================
-- Esquema de Base de Datos - Base de Conocimiento SecurityPlate
-- Semana 15: Organizacion de Base de Conocimiento Empresarial
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. Tabla: dominio
-- Representa las areas de conocimiento especializadas en el proyecto.
CREATE TABLE IF NOT EXISTS dominio (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

-- 2. Tabla: aplicacion
-- Modulos, subsistemas o procesos de SecurityPlate donde se aplica el conocimiento.
CREATE TABLE IF NOT EXISTS aplicacion (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id)
);

-- 3. Tabla: experto
-- Talento humano responsable de generar, revisar y auditar los articulos.
CREATE TABLE IF NOT EXISTS experto (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL
);

-- 4. Tabla: herramienta
-- Tecnologias, frameworks o medios utilizados en desarrollo, captura u operacion.
CREATE TABLE IF NOT EXISTS herramienta (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    finalidad TEXT NOT NULL
);

-- 5. Tabla: articulo
-- Procedimientos, guias tecnicas y politicas operativas del sistema.
CREATE TABLE IF NOT EXISTS articulo (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    dominio_id INTEGER NOT NULL REFERENCES dominio(id),
    aplicacion_id INTEGER REFERENCES aplicacion(id),
    experto_id INTEGER NOT NULL REFERENCES experto(id),
    herramienta_id INTEGER REFERENCES herramienta(id),
    fuente TEXT NOT NULL,
    fecha_revision TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'BORRADOR'
        CHECK (estado IN ('BORRADOR', 'VALIDADO')),
    UNIQUE (titulo, dominio_id)
);

-- Indice para optimizar consultas de articulos validados por dominio
CREATE INDEX IF NOT EXISTS idx_articulo_dominio_estado
ON articulo(dominio_id, estado);
