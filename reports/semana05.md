# Semana 05 - Sistema hibrido

## Consulta 1
- Entrada: placa coincide, conductor coincide y confianza alta para autorizar salida
- Reglas: R1 - Autorizar salida con coincidencia completa
- Accion: Autorizar la salida y registrar la trazabilidad.
- Evidencia: ENTRADA 5
Tema: Confianza del reconocimiento
Enunciado: Cada lectura de placa debe conservar un valor de confianza. Una confianza alta permite continuar con la validación; una confianza media debe marcarse como revisión preventiva; y una confianza baja impide tomar una decisión automática.
- Similitud: 0.355
- Clase: autorizado

## Consulta 2
- Entrada: placa no coincide con el registro de ingreso
- Reglas: R2 - Bloquear placa no coincidente
- Accion: Bloquear la salida y generar una alerta para el personal de seguridad.
- Evidencia: ENTRADA 7
Tema: Vehículo no registrado
Enunciado: Si una placa detectada en la salida no tiene un registro de ingreso activo, el sistema debe clasificar el caso como vehículo no registrado, bloquear la autorización automática y enviar la situación a un encargado.
- Similitud: 0.431
- Clase: alerta

## Consulta 3
- Entrada: imagen borrosa, iluminacion deficiente y confianza baja
- Reglas: R3 - Solicitar nueva captura por baja calidad
- Accion: Solicitar una nueva captura antes de decidir.
- Evidencia: ENTRADA 5
Tema: Confianza del reconocimiento
Enunciado: Cada lectura de placa debe conservar un valor de confianza. Una confianza alta permite continuar con la validación; una confianza media debe marcarse como revisión preventiva; y una confianza baja impide tomar una decisión automática.
- Similitud: 0.341
- Clase: revision

