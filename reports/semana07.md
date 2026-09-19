# Semana 07 - Representaciones del reconocimiento

Reporte generado automáticamente desde `data/casos_semana07.csv`.

## Resultados de los casos de prueba

| Caso | Distancia numérica | Regla simbólica | Autómata | Esperado | Estado |
|---:|---:|---|---|---|---|
| 1 | 0.085 | `autorizar_salida` | Aceptada | Aceptada | Correcto |
| 2 | 0.089 | `enviar_a_revision` | Aceptada | Aceptada | Correcto |
| 3 | 0.564 | `enviar_a_revision` | Rechazada | Rechazada | Correcto |
| 4 | 0.923 | `enviar_a_revision` | Rechazada | Rechazada | Correcto |
| 5 | 1.008 | `enviar_a_revision` | Rechazada | Rechazada | Correcto |

Casos correctos: **5/5**.

## Interpretación

- La distancia numérica compara cada vector con el patrón de salida autorizada.
- La representación simbólica aplica hechos y la regla `autorizar_salida`.
- El autómata acepta únicamente el protocolo `IPCS`.

## Comparación de representaciones

| Representación | Información utilizada | Puede reconocer | Ventaja | Limitación |
|---|---|---|---|---|
| Numérica | Confianza OCR, conductor, imagen y registro | Similitud con un patrón válido | Compara magnitudes | No explica por sí sola la decisión |
| Simbólica | Hechos y regla de autorización | Condiciones explícitas | Es interpretable y auditable | Depende de umbrales manuales |
| Autómata | Símbolos y estados del protocolo | Secuencias válidas | Controla el orden de eventos | No calcula confianza |

## Limitaciones

La distancia depende de características normalizadas y no explica por sí sola una decisión. Los hechos usan umbrales definidos manualmente y el autómata verifica el orden, pero no la calidad de la evidencia.
