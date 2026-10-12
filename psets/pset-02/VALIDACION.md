# Validación de ReservaU v2

## Ejecución local: correcta

Desde `psets/pset-02/implementacion/`, ejecutar:

```console
python simulacion.py
```

La ejecución completa terminó sin errores: 10 escenarios y 42 comprobaciones marcadas como `VALIDADO`. La salida se conserva en `../salida_simulacion.txt`. Estas comprobaciones forman parte de la demostración ejecutable; no se incorpora una suite de pruebas automatizadas.

La simulación demuestra las dos familias de sede, el rechazo de horarios inválidos, la recurrencia exitosa y el rechazo completo por conflicto en la semana 3, las tres políticas de cancelación, la suspensión al tercer no-show mensual, los bloqueos clonados y la carrera entre dos hilos. En esta última se obtuvo exactamente una confirmación, un rechazo y una reserva activa.

También demuestra los límites exactos de 2 y 24 horas, la expiración exacta de la suspensión, la prioridad antes de las 18:00, la ausencia de desplazamientos parciales, las acciones del administrador, la conservación del historial y las recurrencias de 2 y 8 semanas.

## Comprobaciones adicionales: correctas

Se comprobó directamente que una familia con validador Norte y notificador Sur se rechaza, que el Builder rechaza la ausencia de datos obligatorios y que una carrera entre reserva y bloqueo no deja reservas activas en la franja bloqueada. Estas comprobaciones no agregan archivos de pruebas a la entrega.

## Docker: construcción y ejecución correctas

Se ejecutaron los comandos solicitados con Docker Desktop (motor Linux):

```console
docker build -t reservau-v2 .
docker run reservau-v2
```

Ambos terminaron con código 0. La imagen se construyó desde `python:3.11-slim`; el contenedor `9930b3b11580` ejecutó `["python", "simulacion.py"]` y terminó en estado `Exited (0)`. Su salida íntegra está en `salida_docker.txt`: 597 líneas, 42 comprobaciones `VALIDADO` y el mensaje final `SIMULACIÓN COMPLETA`.

La prueba concurrente confirmó exactamente una reserva, rechazó la otra y conservó una sola reserva activa. La comprobación anterior que estaba pendiente por falta de acceso al motor queda resuelta con esta ejecución.

## Alcance del paquete

El paquete incluye la implementación, el README con patrones y trazabilidad, la evidencia de ejecución y las fuentes y diagramas preparados anteriormente. La entrega se ubica en `C:/Users/harvy/DisenoSistemas/psets/pset-02/`, conserva el PSet 1 y contiene los siete PDF solicitados. Se incluyen también la fuente LaTeX y los catálogos como material editable de apoyo.
