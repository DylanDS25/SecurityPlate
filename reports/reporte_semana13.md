# Semana 13 - Ingenieria del conocimiento SecurityPlate

## 1. Analisis del dominio

**Problema:** determinar si una salida vehicular posee evidencia suficiente
para autorizarla o debe enviarse a revision manual.

**Conceptos principales:** hechos, regla, premisa, conclusion, protocolo
`IPCS`, encadenamiento hacia adelante, punto fijo y trazabilidad.

**Hechos iniciales:** coincidencia de placa, coincidencia de conductor,
confianza OCR, calidad de imagen, registro activo y protocolo observado.

**Conclusion esperada:** `autorizar_salida` solo cuando las siete reglas
pueden encadenarse; de lo contrario, `enviar_a_revision`.

## Alcance

Practica de inferencia limitada al flujo de salida. La entrada es `data/casos_semana07.csv`; no sustituye ni modifica el modelo de Semana 07.

## 2. Reglas logicas

| Regla | Premisas | Conclusion |
|---|---|---|
| R1 | conductor_coincide; placa_coincide | correspondencia_confirmada |
| R2 | confianza_ocr_alta; imagen_suficiente | lectura_visual_suficiente |
| R3 | registro_activo | registro_confirmado |
| R4 | correspondencia_confirmada; lectura_visual_suficiente | identidad_visual_confirmada |
| R5 | identidad_visual_confirmada; registro_confirmado | evidencia_salida_suficiente |
| R6 | evidencia_salida_suficiente; protocolo_aceptado | operacion_salida_habilitada |
| R7 | operacion_salida_habilitada | autorizar_salida |

## Resultados

| Caso | Protocolo | Conclusion | Esperado | Estado |
|---|---|---|---|---|
| 1 | IPCS | autorizar_salida | autorizar_salida | Correcto |
| 2 | IPCS | enviar_a_revision | enviar_a_revision | Correcto |
| 3 | IPC | enviar_a_revision | enviar_a_revision | Correcto |
| 4 | IPSS | enviar_a_revision | enviar_a_revision | Correcto |
| 5 | IPCX | enviar_a_revision | enviar_a_revision | Correcto |

## 3. Pruebas funcionales

- **Caso demostrado:** el caso 1 activa las siete reglas y concluye
  `autorizar_salida`.
- **Caso no demostrado:** la evidencia incompleta concluye
  `enviar_a_revision`; la conclusion positiva no se inventa.
- **Conservacion:** `inferir` copia el conjunto inicial y no lo modifica.
- **Ciclos:** el motor repite hasta punto fijo y evita conclusiones duplicadas.
- **Validacion:** unittest cubre conclusiones, conservacion, duplicados,
  premisas vacias y reglas circulares.

## 4. Trazabilidad por caso

### Caso 1: Salida autorizable con lectura clara y conductor validado

**Hechos iniciales:** conductor_coincide, confianza_ocr_alta, imagen_suficiente, placa_coincide, protocolo_aceptado, registro_activo.

**Trazas:**

- `R1: conductor_coincide, placa_coincide => correspondencia_confirmada`
- `R2: confianza_ocr_alta, imagen_suficiente => lectura_visual_suficiente`
- `R3: registro_activo => registro_confirmado`
- `R4: correspondencia_confirmada, lectura_visual_suficiente => identidad_visual_confirmada`
- `R5: identidad_visual_confirmada, registro_confirmado => evidencia_salida_suficiente`
- `R6: evidencia_salida_suficiente, protocolo_aceptado => operacion_salida_habilitada`
- `R7: operacion_salida_habilitada => autorizar_salida`

**Conclusion:** `autorizar_salida`. **Estado:** Correcto.

### Caso 2: Placa diferente al registro de ingreso

**Hechos iniciales:** conductor_coincide, confianza_ocr_alta, imagen_suficiente, protocolo_aceptado, registro_activo.

**Trazas:**

- `R2: confianza_ocr_alta, imagen_suficiente => lectura_visual_suficiente`
- `R3: registro_activo => registro_confirmado`

**Conclusion:** `enviar_a_revision`. **Estado:** Correcto.

### Caso 3: Imagen borrosa y confianza insuficiente para decidir

**Hechos iniciales:** conductor_coincide, placa_coincide, registro_activo.

**Trazas:**

- `R1: conductor_coincide, placa_coincide => correspondencia_confirmada`
- `R3: registro_activo => registro_confirmado`

**Conclusion:** `enviar_a_revision`. **Estado:** Correcto.

### Caso 4: Conductor no coincide aunque la placa fue reconocida

**Hechos iniciales:** confianza_ocr_alta, imagen_suficiente, placa_coincide, registro_activo.

**Trazas:**

- `R2: confianza_ocr_alta, imagen_suficiente => lectura_visual_suficiente`
- `R3: registro_activo => registro_confirmado`

**Conclusion:** `enviar_a_revision`. **Estado:** Correcto.

### Caso 5: Vehiculo sin registro activo y protocolo desconocido

**Hechos iniciales:** conductor_coincide, confianza_ocr_alta, imagen_suficiente, placa_coincide.

**Trazas:**

- `R1: conductor_coincide, placa_coincide => correspondencia_confirmada`
- `R2: confianza_ocr_alta, imagen_suficiente => lectura_visual_suficiente`
- `R4: correspondencia_confirmada, lectura_visual_suficiente => identidad_visual_confirmada`

**Conclusion:** `enviar_a_revision`. **Estado:** Correcto.

Casos correctos: **5/5**.

## Limite

El motor verifica la aplicacion reproducible de reglas. No valida por si solo que las reglas representen una politica real de autorizacion.
