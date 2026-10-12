"""Pasos copiados del catálogo aprobado; mismos números y nombres."""
PASOS = {'CU-01': {'1': 'Actor solicita cancha, fecha y franja al sistema.',
           '2': 'Sistema valida datos y que el solicitante no esté suspendido.',
           '3': 'Sistema valida el intervalo con los servicios de la sede de la cancha.',
           '4': 'Sistema comprueba cancha, bloqueos y todos los solapamientos dentro de la sección '
                'crítica.',
           '5': 'Sistema crea y registra la reserva con su política; aplica los desplazamientos '
                'autorizados sin penalidad.',
           '6': 'Sistema notifica por el canal de sede la confirmación y los desplazamientos, si '
                'existen.'},
 'CU-02': {'1': 'Capitán solicita cancha, fecha inicial, franja, semanas y opcionales al sistema.',
           '2': 'Sistema valida rol, datos, 2..8 semanas y ausencia de suspensión; omitir semanas '
                'implica 2.',
           '3': 'Sistema prepara las ocurrencias semanales con equipo y notas.',
           '4': 'Sistema recorre las semanas en orden y valida en cada una horario de sede, cancha '
                'habilitada y ausencia de reservas o bloqueos.',
           '5': 'Sistema registra todas las ocurrencias y su vínculo a la serie en una sola '
                'operación.',
           '6': 'Sistema notifica la serie por el canal de sede y confirma sus ocurrencias.'},
 'CU-03': {'1': 'Actor solicita cancelar su reserva; administrador solicita anular indicando '
                'motivo.',
           '2': 'Sistema valida propiedad o rol administrador y que la reserva esté activa.',
           '3': 'Reserva evalúa la política autorizada: regular 2 h, oficial 24 h o anulación '
                'administrativa sin penalidad.',
           '4': 'Sistema cambia ACTIVA a CANCELADA y libera la franja.',
           '5': 'Sistema conserva resultado y motivo en el historial.',
           '6': 'Sistema notifica por canal de sede e informa el resultado al actor.'},
 'CU-04': {'1': 'Administrador define motivo, franja y equipo de la plantilla; elige canchas y '
                'fechas.',
           '2': 'Sistema valida rol, datos y destinos antes de aplicar cambios.',
           '3': 'Sistema clona la plantilla para cada destino con equipo independiente.',
           '4': 'Sistema toma cada clon, detecta todas sus reservas activas solapadas y registra '
                'el bloqueo.',
           '5': 'Sistema anula sin penalidad las reservas afectadas, conserva el motivo y repite '
                '4-5 para los clones restantes.',
           '6': 'Sistema notifica cada reserva afectada por su sede y confirma los bloqueos al '
                'administrador.'},
 'CU-05': {'1': 'Administrador solicita registrar o modificar una cancha y sus datos.',
           '2': 'Sistema valida rol, identificador y sede.',
           '3': 'Sistema registra la cancha o aplica los cambios y su estado operativo.',
           '4': 'Sistema confirma los datos y estado resultantes.'},
 'CU-06': {'1': 'Administrador solicita revisar el conflicto informado.',
           '2': 'Sistema valida el rol administrador y presenta las reservas involucradas, sus '
                'estados y motivos.',
           '3': 'Administrador selecciona la reserva que anulará y declara el motivo.',
           '4': 'Sistema ejecuta CU-03 como anulación administrativa.',
           '5': 'Sistema informa al administrador el resultado de la intervención.'},
 'CU-07': {'1': 'Actor consulta sede, cancha, fecha e intervalo.',
           '2': 'Sistema valida datos de la consulta.',
           '3': 'Sistema comprueba horario, estado de cancha, reservas activas y bloqueos.',
           '4': 'Sistema informa disponibilidad y, si corresponde, motivo de indisponibilidad.'},
 'CU-08': {'1': 'Solicitante pide sus reservas activas e historial.',
           '2': 'Sistema selecciona solo reservas del solicitante.',
           '3': 'Sistema presenta sede, cancha, intervalo, estado, motivo y serie cuando '
                'corresponda.',
           '4': 'Sistema finaliza la consulta sin modificar reservas.'}}
