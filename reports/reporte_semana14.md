# Semana 14 - Redes semanticas SecurityPlate

## Objetivo

Representar conceptos propios de SecurityPlate mediante nodos, aristas
dirigidas y triples. La red interpreta frases simples, consulta rutas,
demuestra jerarquia con `es_un`, herencia explicita y control de ciclos.

## Conceptos

moto, vehiculo, placa, foto_placa, comparacion_placa, resultado_visual, personal_seguridad, verificacion_manual.

## Umbral

Una foto se considera adecuada con calidad >= 0.8.

## Relacion y conclusion

Si la foto es adecuada y la placa coincide, el sistema infiere
`placa_corresponde_a_moto`. En otro caso se infiere
`llamar_personal_verificacion_manual`.

## Resultados por caso

| Caso | Placa coincide | Foto adecuada | Conclusion | Estado |
|---|---|---|---|---|
| 1 | True | True | autorizar_salida | Correcto |
| 2 | False | True | llamar_personal_verificacion_manual | Correcto |
| 3 | True | False | llamar_personal_verificacion_manual | Correcto |
| 4 | True | True | llamar_personal_verificacion_manual | Correcto |
| 5 | True | True | llamar_personal_verificacion_manual | Correcto |

## Evidencia de entrada y salida

- Entrada: `data/casos_semana07.csv`.
- JSON: `artifacts/semana14_red_semantica.json`.
- Motor: `src/red_semantica.py`.
- Integracion: `src/semana14_redes_semanticas.py`.

## Limitaciones

- El parser reconoce patrones simples, no lenguaje natural general.
- Una consulta sin evidencia devuelve resultado no demostrado.
- La transitividad se aplica solamente a relaciones `es_un`.
- La revision manual conserva la decision humana como validacion final.
