# ReservaU: catálogo de casos de uso

Fuente de nombres, pasos y alternos para diagramas de comportamiento y simulación.

## CU-01: Reservar una cancha

Actor: Estudiante; Capitán por herencia

Requerimientos: RF-01, 02, 06, 08, 13, 14, 15; RNF-04

Precondiciones: Solicitante y cancha registrados; sede y contactos definidos.

### Flujo principal

1. Actor solicita cancha, fecha y franja al sistema.
2. Sistema valida datos y que el solicitante no esté suspendido.
3. Sistema valida el intervalo con los servicios de la sede de la cancha.
4. Sistema comprueba cancha, bloqueos y todos los solapamientos dentro de la sección crítica.
5. Sistema crea y registra la reserva con su política; aplica los desplazamientos autorizados sin penalidad.
6. Sistema notifica por el canal de sede la confirmación y los desplazamientos, si existen.

### Alternos

- **2a (paso 2):** Datos inválidos: rechazar sin crear reserva.
- **2b (paso 2):** Suspensión vigente: informar vencimiento y rechazar.
- **3a (paso 3):** Fuera del horario de sede: rechazar.
- **4a (paso 4):** Cancha deshabilitada, bloqueo o conflicto sin prioridad suficiente: rechazar.
- **4b (paso 4):** Prioridad oficial válida sobre todos los conflictos regulares: preparar desplazamientos y continuar en 5, sin liberar la sección crítica; ninguna anulación se aplica todavía.

Postcondición: Una reserva activa nueva; cualquier rechazo conserva la ocupación previa. Los pasos 4 y 5 comparten la sección crítica; se notifica después de registrar.

## CU-02: Reservar de forma recurrente

Actor: Capitán de equipo oficial

Requerimientos: RF-08, 09, 10, 13, 14, 15; RNF-05

Precondiciones: Capitán y cancha registrados; sede y contactos definidos.

### Flujo principal

1. Capitán solicita cancha, fecha inicial, franja, semanas y opcionales al sistema.
2. Sistema valida rol, datos, 2..8 semanas y ausencia de suspensión; omitir semanas implica 2.
3. Sistema prepara las ocurrencias semanales con equipo y notas.
4. Sistema recorre las semanas en orden y valida en cada una horario de sede, cancha habilitada y ausencia de reservas o bloqueos.
5. Sistema registra todas las ocurrencias y su vínculo a la serie en una sola operación.
6. Sistema notifica la serie por el canal de sede y confirma sus ocurrencias.

### Alternos

- **2a (paso 2):** Actor no capitán, datos inválidos o semanas fuera de rango: rechazar.
- **2b (paso 2):** Suspensión vigente: informar vencimiento y rechazar.
- **4a (paso 4):** Semana inválida o en conflicto: informar primera semana y fecha afectadas; rechazar toda la serie sin registrar ni desplazar reservas.

Postcondición: Se registran todas las semanas o ninguna. Pasos 4 y 5 comparten la sección crítica.

## CU-03: Cancelar una reserva

Actor: Estudiante; Capitán por herencia; Administrador para anular

Requerimientos: RF-03, 07, 08, 14, 15; RNF-01

Precondiciones: Actor y reserva registrados; hora actual disponible.

### Flujo principal

1. Actor solicita cancelar su reserva; administrador solicita anular indicando motivo.
2. Sistema valida propiedad o rol administrador y que la reserva esté activa.
3. Reserva evalúa la política autorizada: regular 2 h, oficial 24 h o anulación administrativa sin penalidad.
4. Sistema cambia ACTIVA a CANCELADA y libera la franja.
5. Sistema conserva resultado y motivo en el historial.
6. Sistema notifica por canal de sede e informa el resultado al actor.

### Alternos

- **2a (paso 2):** Sin propiedad ni rol administrador, reserva inexistente, motivo administrativo ausente o estado terminal: rechazar sin cambios. Fin.
- **3a (paso 3):** Solo para cancelación del solicitante: si faltan menos de 2 h (regular) o 24 h (oficial), sustituir el paso 4 por NO_SHOW y liberar la franja. Estudiante registra una falta fechada; al tercer no-show del mes crea una suspensión de 7 días. Continuar en 5.

Postcondición: Reserva terminal y franja liberada; no-show una sola vez. Igualdad con 2/24 h es cancelación normal.

## CU-04: Bloquear canchas para un evento

Actor: Administrador

Requerimientos: RF-11, 12, 14; RNF-01, 05

Precondiciones: Administrador registrado; canchas y sedes existentes.

### Flujo principal

1. Administrador define motivo, franja y equipo de la plantilla; elige canchas y fechas.
2. Sistema valida rol, datos y destinos antes de aplicar cambios.
3. Sistema clona la plantilla para cada destino con equipo independiente.
4. Sistema toma cada clon, detecta todas sus reservas activas solapadas y registra el bloqueo.
5. Sistema anula sin penalidad las reservas afectadas, conserva el motivo y repite 4-5 para los clones restantes.
6. Sistema notifica cada reserva afectada por su sede y confirma los bloqueos al administrador.

### Alternos

- **2a (paso 2):** Rol o datos inválidos, cancha inexistente o intervalo inválido: rechazar sin aplicar bloqueos. Fin.
- **4a (paso 4):** Clon sin reservas afectadas: no anular ni preparar avisos para ese clon. Repetir 4 para el siguiente clon; si no quedan, continuar en 6.

Postcondición: Bloqueos aplicados sin reservas activas solapadas. Pasos 4 y 5 son indivisibles por bloqueo.

## CU-05: Gestionar canchas

Actor: Administrador

Requerimientos: RF-04

Precondiciones: Administrador registrado; sedes existentes. La existencia de la cancha objetivo se valida en el paso 2.

### Flujo principal

1. Administrador solicita registrar o modificar una cancha y sus datos.
2. Sistema valida rol, identificador y sede.
3. Sistema registra la cancha o aplica los cambios y su estado operativo.
4. Sistema confirma los datos y estado resultantes.

### Alternos

- **2a (paso 2):** Rol inválido, identificador duplicado al crear, cancha inexistente al modificar o sede inválida: rechazar.
- **3a (paso 3):** Deshabilitación: impedir nuevas reservas; conservar las anteriores. Para anularlas se usa CU-03 o CU-04; continuar en 4.

Postcondición: Cancha vinculada a una sede y estado actualizado.

## CU-06: Intervenir en conflictos

Actor: Administrador

Requerimientos: RF-05, 03, 07, 14

Precondiciones: Conflicto informado al administrador; reserva identificable.

### Flujo principal

1. Administrador solicita revisar el conflicto informado.
2. Sistema valida el rol administrador y presenta las reservas involucradas, sus estados y motivos.
3. Administrador selecciona la reserva que anulará y declara el motivo.
4. Sistema ejecuta CU-03 como anulación administrativa.
5. Sistema informa al administrador el resultado de la intervención.

### Alternos

- **2a (paso 2):** Sin autorización o conflicto inexistente: rechazar.
- **3a (paso 3):** No decide anular: cerrar la revisión sin modificar reservas.
- **4a (paso 4):** La reserva ya no está activa: CU-03 rechaza; informar estado actual y continuar en 5.

Postcondición: Si se anula: CANCELADA con motivo, notificación al afectado y cero faltas adicionales.

## CU-07: Consultar disponibilidad

Actor: Estudiante; Capitán por herencia; Administrador

Requerimientos: RF-06, 04, 13

Precondiciones: Actor registrado; sedes y canchas disponibles para consulta.

### Flujo principal

1. Actor consulta sede, cancha, fecha e intervalo.
2. Sistema valida datos de la consulta.
3. Sistema comprueba horario, estado de cancha, reservas activas y bloqueos.
4. Sistema informa disponibilidad y, si corresponde, motivo de indisponibilidad.

### Alternos

- **2a (paso 2):** Cancha o sede inexistente, intervalo inválido: informar error sin cambios.
- **3a (paso 3):** Franja ocupada, bloqueada, cancha deshabilitada o fuera de horario: informar no disponible en el paso 4.

Postcondición: Consulta sin cambios de ocupación. Una respuesta disponible no garantiza una reserva posterior.

## CU-08: Consultar reservas e historial

Actor: Estudiante; Capitán por herencia

Requerimientos: RF-07

Precondiciones: Solicitante registrado e identificado.

### Flujo principal

1. Solicitante pide sus reservas activas e historial.
2. Sistema selecciona solo reservas del solicitante.
3. Sistema presenta sede, cancha, intervalo, estado, motivo y serie cuando corresponda.
4. Sistema finaliza la consulta sin modificar reservas.

### Alternos

- **2a (paso 2):** No hay reservas: informar lista vacía y continuar en 4.

Postcondición: Historial conserva reservas canceladas, desplazadas y en no-show.
