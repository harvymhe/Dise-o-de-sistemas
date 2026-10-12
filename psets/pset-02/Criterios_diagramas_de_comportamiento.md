# Revisión de los diagramas de comportamiento

## Fuentes consultadas

La carpeta `sources/` estaba vacía al revisar. Se consultaron el enunciado del PSet 2 ya leído y estos ejemplos locales del curso, sin modificarlos:

- [Robustez, laboratorio semana 07](<C:/Users/harvy/DisenoSistemas/laboratorios/semana-07/docs/Diagrama de robustez.pdf>): referencia para fronteras, controles, entidades y vínculos numerados.
- [Secuencia, laboratorio semana 07](<C:/Users/harvy/DisenoSistemas/laboratorios/semana-07/docs/Diagrama de secuencia.pdf>): referencia para participantes, mensajes, retornos y alternativas.

Las reglas de conexión ICONIX exigidas en este trabajo provienen explícitamente del enunciado. La notación se contrastó también con documentación primaria del proveedor de Enterprise Architect:

- [Secuencia UML](https://sparxsystems.com/resources/tutorials/uml2/sequence-diagram.html): líneas de vida, mensajes y fragmentos combinados.
- [Actividad UML](https://sparxsystems.com/resources/tutorials/uml2/activity-diagram.html): acciones, decisiones, fusiones y finales de actividad.
- [Estados UML](https://sparxsystems.com/resources/tutorials/uml2/state-diagram.html): estados, eventos, guardas y efectos.

## Qué hacer y qué evitar

| Diagrama | Aplicación en ReservaU | Error que se evita |
|---|---|---|
| Robustez CU-03 | Actor conectado a ConsolaReservaU; fronteras conectadas al control; controles conectados a entidades. Política representada como responsabilidad de control. Reserva conserva su responsabilidad de delegar la evaluación. | Actor llamando a una entidad; frontera modificando Reserva directamente; frontera conteniendo las reglas de negocio. |
| Secuencia CU-01 | Primer mensaje a ReservaUFacade.reservar; alternativas anidadas para datos, suspensión, sede y disponibilidad; creación/registro en región crítica; notificación después de registrar. | Dibujar rechazos y luego continuar incondicionalmente al éxito; proteger solo la escritura; mezclar servicios de sedes. |
| Actividad CU-02 | Bucle con índice semanal, decisión de conflicto, incremento como acción, fusión para regresar y registro único fuera del bucle. | Registrar cada semana mientras se comprueba; dejar las primeras semanas guardadas si falla la tercera; confundir una fusión con sincronización paralela. |
| Estados Reserva | ACTIVA, CANCELADA, NO_SHOW; evento [guarda] / efecto; CANCELADA y NO_SHOW sin transiciones salientes. | Usar acciones como estados; marcar exactamente 2/24 horas como tardío; convertir la suspensión del solicitante en un estado de Reserva. |

Los estados terminales de negocio se conservan como estados nombrados sin transiciones salientes, para que el historial permanezca consultable. No se representan como eliminación de la reserva.

## Trazabilidad de pasos

La fuente de nombres y orden es `Catalogo_casos_de_uso.md`.

| Caso | Correspondencia |
|---|---|
| CU-03, pasos 1-2 | Solicitud por frontera; validación de autorización y estado; 2a rechaza sin cambios. |
| CU-03, pasos 3-4 | Política autorizada; CANCELADA normal o sustitución 3a por NO_SHOW. |
| CU-03, pasos 5-6 | Historial y notificación de resultado; la suspensión mensual se deriva de registrar el no-show. |
| CU-01, pasos 1-3 | Solicitud a Facade; datos y suspensión; horario de sede. |
| CU-01, pasos 4-5 | Comprobar disponibilidad y prioridad; registrar con política; aplicar desplazamientos permitidos dentro del mismo lock. |
| CU-01, paso 6 | Notificar confirmación y afectados solo si hubo registro. |
| CU-02, pasos 1-3 | Solicitud; rol/datos/semanas/suspensión; preparación sin registro. |
| CU-02, pasos 4-5 | Todas las semanas verificadas bajo protección antes de registrar la serie completa. |
| CU-02, paso 6 | Notificar y confirmar la serie después de liberar el lock. |

## Nombres para la implementación siguiente

`ReservaUFacade`, `ConsolaReservaU`, `FamiliaSede`, `CreadorReserva` y `NotificadorSede` son colaboradores de diseño, no nuevas entidades de negocio. La Facade coordina; las entidades conservan reglas, estados y datos. Los métodos y responsabilidades existentes de `Reserva`, `Estudiante`, `CalendarioReservas` y `ConfiguracionReglas` se mantienen.

El parámetro `politica_autorizada` es interno: la Facade verifica autorización antes de usar anulación administrativa. El usuario no puede seleccionar una política para evitar una falta.

## Validación de esta entrega

- Cuatro PDF independientes, cada uno de una página vectorial.
- Revisión visual de las cuatro páginas y reparación de superposiciones detectadas.
- Presencia de los tres rechazos exigidos en fragmentos alt, más datos inválidos.
- Verificación de límites estrictos: menos de 2/24 horas; igualdad permite cancelación normal.
- Ningún flujo de rechazo confirma una reserva o serie.
- Comprobación de las conexiones actor/frontera/control/entidad en robustez.

La validación aquí es documental. La prueba con dos hilos y la ejecución de Docker corresponden al paso de implementación y aún no se han realizado.
