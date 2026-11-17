-- ====================================================================
-- Datos Iniciales - Base de Conocimiento SecurityPlate
-- Semana 15: Organizacion de Base de Conocimiento Empresarial
-- ====================================================================

-- 1. Insercion de Dominios de Conocimiento de SecurityPlate
INSERT OR IGNORE INTO dominio (id, nombre) VALUES
    (1, 'Vision por Computador'),
    (2, 'Control de Acceso Vehicular'),
    (3, 'Auditoria y Trazabilidad');

-- 2. Insercion de Aplicaciones y Modulos del Sistema
INSERT OR IGNORE INTO aplicacion (id, nombre, dominio_id) VALUES
    (1, 'Modulo de Reconocimiento OCR', 1),
    (2, 'Detector de Calidad Visual', 1),
    (3, 'Motor de Inferencia y Reglas IPCS', 2),
    (4, 'Controlador de Barrera y Alertas', 2),
    (5, 'Consola de Auditoria y Evidencias', 3);

-- 3. Insercion de Expertos Responsables
INSERT OR IGNORE INTO experto (id, nombre, cargo) VALUES
    (1, 'Yeison Ayala', 'Lider de Vision y Modelos CNN'),
    (2, 'Dylan Duitama', 'Especialista en Sistemas Expertos y Protocolo IPCS'),
    (3, 'Carlos Rodriguez', 'Oficial de Seguridad Fisica y Control de Acceso'),
    (4, 'Mariana Torres', 'Operadora de Monitoreo y Verificacion Manual');

-- 4. Insercion de Herramientas de Desarrollo y Operacion
INSERT OR IGNORE INTO herramienta (id, nombre, finalidad) VALUES
    (1, 'PyTorch y Torchvision', 'Entrenamiento e inferencia de CNN para caracteres 32x32'),
    (2, 'OpenCV y Scikit-Image', 'Preprocesamiento de imagenes, umbral Otsu y descriptores LBP'),
    (3, 'SQLite y Motor Relacional', 'Persistencia transaccional de evidencias y base de conocimiento'),
    (4, 'Motor de Reglas y Red Semantica', 'Encadenamiento hacia adelante y verificacion ontologica'),
    (5, 'Unittest de Python', 'Validacion automatizada de integridad referencial y cobertura');

-- 5. Insercion de Articulos de Procedimientos y Politicas
-- Se incluyen articulos en estado VALIDADO y en estado BORRADOR para evidenciar la regla editorial
INSERT OR IGNORE INTO articulo
    (id, titulo, contenido, dominio_id, aplicacion_id, experto_id, herramienta_id, fuente, fecha_revision, estado)
VALUES
    (1,
     'Procedimiento de captura y preprocesamiento de placas',
     'Al ingresar un vehiculo, la camara captura la placa frontal. Se convierte a escala de grises, se aplica filtro Otsu, Canny y recorte de caracteres normalizados a 32x32 para alimentar la red neuronal CNN.',
     1, 1, 1, 2,
     'Manual de Percepcion Visual SecurityPlate v2.1',
     '2026-10-15',
     'VALIDADO'),

    (2,
     'Umbrales de calidad de imagen y confianza de lectura',
     'Para admitir una lectura automatica valida, la imagen debe registrar calidad >= 0.80 y el OCR una confianza >= 0.85. Valores inferiores disparan alerta de baja calidad y solicitan recaptura.',
     1, 2, 1, 1,
     'Especificacion Tecnica de Umbrales Semanas 08-10',
     '2026-10-20',
     'VALIDADO'),

    (3,
     'Protocolo de autorizacion de salida mediante secuencia IPCS',
     'La autorizacion automatica de salida exige la ejecucion secuencial del protocolo IPCS (Ingreso, Placa, Conductor, Salida), coincidencia de placa, coincidencia del conductor y registro activo.',
     2, 3, 2, 4,
     'Reglas de Inferencia R1-R7 Semana 13',
     '2026-10-25',
     'VALIDADO'),

    (4,
     'Procedimiento de contingencia y derivacion a revision manual',
     'Cuando la placa no coincida con el ingreso o la confianza sea insuficiente, la barrera se bloquea, se emite alerta sonora y se transfiere el caso al operador para inspeccion presencial de documentos.',
     2, 4, 2, 3,
     'Guia de Operaciones en Cabina - Caso de Excepcion',
     '2026-11-02',
     'BORRADOR'),

    (5,
     'Politica de auditoria y resguardo de evidencia fotografica',
     'Toda transaccion de ingreso y salida debe registrar identificador de caso, timestamp ISO, probabilidad calculada, fotografia de placa y decision del sistema en SQLite para trazabilidad.',
     3, 5, 3, 3,
     'Politica Corporativa de Seguridad Fisica e Integridad de Datos',
     '2026-11-10',
     'BORRADOR');
