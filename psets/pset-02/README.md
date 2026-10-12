# ReservaU - PSet 2

Extensión en Python del PSet 1 con siete patrones y exclusión de doble reserva concurrente. Se conservan las entidades, el objeto de valor de horario y la Strategy de prioridad; se añaden sedes, políticas de cancelación, recurrencia, bloqueos y suspensión mensual. Las operaciones se demuestran en memoria, sin servidor, base de datos, API ni interfaz gráfica.

## Ejecutar

Requisito: Python 3.11 o posterior. Solo se utiliza la biblioteca estándar.

```console
cd psets/pset-02/implementacion
python simulacion.py
```

Desde esa misma carpeta, con el motor Docker iniciado:

```console
docker build -t reservau-v2 .
docker run reservau-v2
```

El contenedor ejecuta `simulacion.py`. No necesita puertos, volúmenes, Compose ni instalar paquetes. El programa termina con el mensaje `SIMULACIÓN COMPLETA` y código 0 si todas las comprobaciones demostrativas se cumplen. Una comprobación fallida detiene la demostración con un error; no hay una suite de pruebas adicional.

## Organización y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `implementacion/configuracion.py` | Configuración única de los cinco valores de negocio. |
| `implementacion/objetosdevalor.py` | Intervalo inmutable, estados y sede; horarios y canal provienen de las fábricas de sede. |
| `implementacion/estrategias.py` | Prioridad y políticas de cancelación intercambiables. |
| `implementacion/entidades.py` | Modelo de dominio: solicitantes, administrador, reservas, series, bloqueos, faltas y suspensión. |
| `implementacion/creacion.py` | Factory Method y Builder. |
| `implementacion/sedes.py` | Abstract Factory y familias compatibles. |
| `implementacion/calendario.py` | Ocupación compartida y lock común. |
| `implementacion/fachada.py` | Coordinación de casos de uso; devuelve copias de los resultados, no reservas mutables. |
| `implementacion/flujos.py` | Textos de los pasos del catálogo aprobado, conservando CU y numeración. |
| `implementacion/simulacion.py` | Escenarios E1-E10 ordenados por casos de uso. |

`Reserva` protege transiciones y delega la cancelación en una política, sin consultar el tipo de creador. `Estudiante` conoce sus faltas fechadas, cuenta las del mes y crea la suspensión; `CapitanEquipo` hereda ese comportamiento. `CalendarioReservas` conoce los solapamientos y conserva el historial de las reservas que dejan de estar activas.

El modelo muestra conceptos; algunas representaciones concretas se precisan aquí: `Sede` es un enum con propiedades de horario y canal derivadas de su fábrica; `Suspensión` se escribe `Suspension` en Python. `estrategia_prioridad` mantiene el nombre heredado del PSet 1 para el atributo conceptual `regla_prioridad`. `Reserva.rango_horario` y `politica_cancelacion` corresponden a rango y política del diagrama. Las fábricas y la Facade son colaboradores de implementación, no entidades adicionales del negocio.

## Tabla de patrones y concurrencia

| Patrón | Requerimiento que lo justifica | Problema que resuelve | Clases y métodos |
|---|---|---|---|
| Factory Method | RF-01, RF-03 | Crear el tipo correcto con su política ya asignada, sin repartir decisiones de tipo por el sistema. | `CreadorReserva.crear_reserva()` llama al método polimórfico `_instanciar()`; `CreadorRegular` y `CreadorOficial` producen las dos reservas. `creador_para()` es el único punto de selección. |
| Abstract Factory | RF-13, RF-14; RNF-06 | Mantener compatibles validador y notificador de cada sede. | `FabricaSede`, `FabricaNorte`, `FabricaSur`, `crear_familia()`, `FamiliaSede`. |
| Builder | RF-09 | Construir una serie con obligatorios y opcionales sin registrar datos incompletos. | `ReservaRecurrenteBuilder.para().desde().durante().con_equipo().con_notas().construir()`. |
| Prototype | RF-11 | Replicar una plantilla sin reconstruir todos los datos ni compartir equipo mutable. | `Bloqueo.clonar(cancha, fecha)`. |
| Singleton | RF-15; RNF-07 | Mantener una fuente compartida de parámetros de negocio. | `ConfiguracionReglas.obtener()` / `__new__()`. |
| Strategy | RF-02, RF-03, RF-08 | Variar prioridad y cancelación por composición. | `ReglaPrioridad`, `PrioridadOficial`, `SinPrioridad`; `PoliticaCancelacion`, `CancelacionEstudiante`, `CancelacionCapitan`, `AnulacionAdministrativa`. |
| Facade | RF-01, RF-03, RF-09, RF-10, RF-12 | Dar al cliente una entrada para coordinar calendario, entidades, creación, sede y avisos. | `ReservaUFacade.reservar()`, `reservar_recurrente()`, `cancelar()`, `bloquear()`. |
| Locking pesimista | RNF-04, RNF-05 | Evitar que dos solicitantes verifiquen y escriban sobre el mismo estado disponible; proteger también series y bloqueos. | `CalendarioReservas.lock` (`RLock`) y operaciones de `ReservaUFacade`. |

### Factory Method y Abstract Factory

La selección por tipo del solicitante está centralizada en el registro de creadores. El método de fábrica se sobreescribe en las subclases: no es simplemente un `if` en Reserva. Los productos salen con `CancelacionEstudiante` o `CancelacionCapitan` asignada.

La Facade recibe usuarios y canchas, pero no acepta validadores ni notificadores del cliente. Deriva la familia de la sede de la cancha y conserva la pareja internamente. Además, `FamiliaSede` es inmutable y rechaza la construcción con productos de sedes diferentes. Esto protege el uso de la API pública; no pretende impedir reflexión o acceso deliberado a atributos internos de Python.

### Prototype: por qué `copy.deepcopy`

Se usa `deepcopy` porque el equipo de un bloqueo es una lista mutable: una copia superficial compartiría esa lista con la plantilla. Tras copiar, se asigna la cancha canónica y la fecha del destino; así se independizan los datos de la plantilla sin duplicar la identidad de una cancha. E6 modifica un clon y verifica que la plantilla y otro clon mantienen su equipo original.

### Singleton: beneficio y costo

Una instancia compartida centraliza prioridad, ventanas de cancelación y suspensión, evitando valores duplicados. El costo es estado global mutable y mayor dependencia entre ejecuciones: E9 restaura el parámetro que modifica mediante `finally`. Los cambios de configuración se realizan entre operaciones, sin modificaciones concurrentes mientras se evalúan reglas.

### Concurrencia: elección y alcance

Se eligió locking pesimista con un `RLock` compartido por el calendario. Hay muchas más consultas que reservas, por lo que una consulta informativa libera pronto el lock y no retiene la cancha; al reservar se vuelve a verificar dentro de la sección protegida. En los picos de escritura del inicio de semestre se prefiere esperar brevemente a tener reintentos y conflictos de versión: la misma protección abarca la comprobación final y el registro.

El costo aceptado es serializar también operaciones sobre canchas independientes. Para este programa en memoria y un solo proceso, el lock global simplifica los bloqueos de varias canchas y las series de todo o nada; en un sistema distribuido se necesitaría otro mecanismo. El `RLock` permite que la Facade mantenga la sección crítica mientras invoca métodos del calendario que también se protegen.

La recurrencia construye todos sus productos antes de incorporarlos, verifica todas las semanas con el lock retenido y solo entonces registra el conjunto. Las anulaciones y bloqueos usan ese mismo lock. Los avisos se preparan al confirmar el resultado y se imprimen fuera de la sección crítica; no hay servicios externos reales.

## Escenarios y evidencia

| Escenario | Caso / resultado observable |
|---|---|
| E1 | CU-01 en Norte 06-07 y Sur 22-23; validación por sede y avisos por correo/texto. |
| E2 | CU-01.3a: Sur rechaza 06-07 y el historial permanece vacío. |
| E3 | CU-02 confirma cuatro semanas; otra serie falla en la tercera y deja cero registros parciales, sin desplazar la reserva existente. |
| E4 | CU-03: regular a dos horas exactas CANCELADA; oficial con ocho horas NO_SHOW; administrador sin penalidad; repetición rechazada. |
| E5 | CU-03 registra la tercera falta mensual; CU-01.2b rechaza durante suspensión; se admite en el vencimiento exacto. |
| E6 | CU-04: plantilla, clones independientes, dos canchas bloqueadas, anulación y aviso a afectado; nueva reserva bloqueada se rechaza. |
| E7 | Dos hilos reales sincronizados con `Barrier`; ambos consultaron libre; exactamente una confirmación, un rechazo y una reserva activa. |
| E8 | CU-05 crea/deshabilita/habilita; CU-06 resuelve un conflicto vía CU-03; CU-07 confirma liberación y CU-08 conserva motivo. |
| E9 | Prioridad antes de 18:00, ausencia a las 18:00, varios solapamientos sin cambios parciales, 24 h exactas, 1 h 59 min, propiedad, configuración y Builder. |
| E10 | Faltas de distintos meses, ocho semanas, cuarta falta sin extensión y capitán suspendido sin recurrencia. |

Cada línea de operación se etiqueta `CU-xx.paso`; sus textos principales proceden del catálogo. Los alternos mantienen número y letra. Las líneas de revisión por semana y avisos detallan el paso al que pertenecen. En E7 puede variar el ganador y se pueden intercalar líneas de los hilos; dentro de cada solicitud se conserva el orden del caso de uso.

`simulacion.py` no importa el calendario, las fábricas ni estrategias de reserva: todas las operaciones sobre reservas y las consultas pasan por la Facade. La creación inicial de usuarios/canchas y la demostración de clonación de una plantilla son preparación de datos y evidencia de Prototype.

## Matriz de trazabilidad

| Requisito (numeración del documento) | Caso | Diagrama | Implementación | Evidencia |
|---|---|---|---|---|
| RF-01 Solicitud individual | CU-01 | Secuencia, estados | `ReservaUFacade.reservar`, creadores | E1, E7 |
| RF-02 Prioridad oficial | CU-01.4b | Secuencia, estados | `PrioridadOficial.tiene_prioridad`, plan completo de conflictos | E9 |
| RF-03 Cancelación/anulación | CU-03 | Robustez, estados | `Reserva.cancelar`, `Reserva.anular`, tres políticas | E4, E9 |
| RF-04 Gestión de canchas | CU-05 | Flujo CU-05 | `gestionar_cancha`, `Administrador`, `Cancha.cambiar_estado` | E8 |
| RF-05 Intervención en conflictos | CU-06 | Flujo CU-06, robustez CU-03 | Registro/aviso de conflicto; `intervenir_conflicto` y `cancelar` | E8 |
| RF-06 Disponibilidad | CU-07 | Flujo CU-07, secuencia | `consultar_disponibilidad` de Facade y calendario | E7, E8 |
| RF-07 Reservas e historial | CU-08 | Flujo CU-08, estados | `consultar_historial`; reservas terminales conservadas | E3, E4, E8 |
| RF-08 Suspensión mensual | CU-03.3a, CU-01.2b, CU-02.2b | Robustez, secuencia, actividad, estados | `Estudiante.registrar_no_show`, `contar_no_shows`, `Suspension.esta_vigente` | E5, E10 |
| RF-09 Solicitud recurrente | CU-02 | Actividad | Builder y `ReservaRecurrente` | E3, E9, E10 |
| RF-10 Todo o nada | CU-02.4a | Actividad | `reservar_recurrente`, `registrar_serie` | E3 |
| RF-11 Plantillas/clones | CU-04 | Flujo CU-04 | `Bloqueo.clonar` | E6 |
| RF-12 Aplicar bloqueo/anular | CU-04 | Flujo CU-04, estados | `bloquear`, `aplicar_bloqueo`, `Reserva.anular` | E6 |
| RF-13 Horario de sede | CU-01.3, CU-02.4, CU-07 | Secuencia, actividad | `ValidadorHorario.admite` | E1, E2 |
| RF-14 Canal por sede | CU-01/02/03/04.6 | Secuencia, robustez, actividad | `FamiliaSede.notificar`, `NotificadorSede` | E1, E4, E6 |
| RF-15 Configuración | CU-01/02/03 | Modelo y políticas | `ConfiguracionReglas.obtener` y estrategias | E5, E9 |
| RNF-01 Integridad | CU-03.2a | Estados | Guarda de reserva activa; faltas únicas | E4 |
| RNF-04 Concurrencia | CU-01 | Secuencia: critical | Lock común; verificación y registro | E7 |
| RNF-05 Atomicidad | CU-02, CU-04 | Actividad | Mismo lock para series y bloqueos | E3, E6 |
| RNF-06 Coherencia de sede | CU-01.3/6 | Secuencia | Familias inmutables y pareja validada | E1, E2 |
| RNF-07 Modificabilidad | Reglas de CU-01/03 | Modelo | Parámetros únicos leídos al evaluar | E9 |

Los anteriores RNF-02 y RNF-03 fueron reclasificados como RE-01 (trazabilidad) y RE-02 (entrega ejecutable); no se reutilizan. RF-05 sigue siendo conflictos y RF-07 sigue siendo historial: los patrones nunca reemplazan sus significados.

### Recorrido completo de los tres no-shows

**RF-08 → CU-03.3a → robustez y estados → Strategy + Singleton → `Reserva.cancelar()` / `Estudiante.registrar_no_show()` → E5.** La consecuencia se completa con **CU-01.2b → secuencia → `Estudiante.esta_suspendido()` → rechazo de la nueva solicitud**; CU-02.2b y la actividad aplican el mismo control a la recurrencia.

| Pregunta de revisión | Respuesta verificable |
|---|---|
| ¿Qué requerimiento la define? | RF-08, «Suspensión por no-shows mensuales»: tres faltas en el mismo mes suspenden durante siete días. RF-15 define los parámetros compartidos. SP-04 precisa el inicio, el vencimiento y que una cuarta falta no prolonga la suspensión. |
| ¿En qué caso de uso aparece? | CU-03, alterno 3a, registra la cancelación tardía y la falta. CU-01.2b y CU-02.2b rechazan nuevas reservas mientras la suspensión esté vigente. |
| ¿En qué diagramas aparece? | [Robustez de cancelación](04_Robustez_cancelar_reserva.pdf): registro de falta y suspensión; [estados](07_Estados_de_reserva.pdf): efecto de entrar en NO_SHOW; [secuencia](05_Secuencia_reservar_cancha.pdf): rechazo por suspensión; [actividad recurrente](06_Actividad_reserva_recurrente.pdf): validación y alterno 2b. |
| ¿Qué entidad lleva la cuenta? | `Estudiante` conserva registros fechados en `no_shows`; `contar_no_shows(mes, anio)` cuenta solo el mes y año solicitados. `CapitanEquipo` hereda esta responsabilidad. |
| ¿Qué método aplica la suspensión? | `Reserva.cancelar()` delega en `PoliticaCancelacion.evaluar()` y, si el resultado es NO_SHOW, llama a `Estudiante.registrar_no_show(reserva, ahora)`. Este evita duplicar la falta, cuenta el mes y agrega una `Suspension`; `esta_suspendido()` consulta `Suspension.esta_vigente()`. |
| ¿Qué valores lee de la configuración? | `ConfiguracionReglas.obtener().umbral_mensual = 3` y `.duracion_suspension = timedelta(days=7)`. Las políticas leen además `.ventana_regular = 2 horas` o `.ventana_oficial = 24 horas` para determinar si corresponde NO_SHOW. |
| ¿Dónde se observa en la salida? | En [salida_simulacion.txt](salida_simulacion.txt), E5: línea 174 muestra dos faltas sin suspensión; línea 182 muestra la tercera y su vencimiento; línea 188 rechaza la nueva reserva. La línea 197 confirma que se permite reservar en el instante de vencimiento. |

Extractos de la ejecución guardada (los números identifican líneas del archivo, no pasos nuevos del caso de uso):

```text
174: [MainThread | CU-03.3a] Flujo alterno | Faltas del mes: 2; suspendido=False; vence=None
182: [MainThread | CU-03.3a] Flujo alterno | Faltas del mes: 3; suspendido=True; vence=2026-10-19 15:00:00
188: [MainThread | CU-01.2b] Flujo alterno | RECHAZO: Suspensión hasta 2026-10-19 15:00:00
```

### Recorrido y necesidad de cada patrón

Los diagramas identificados abajo representan el comportamiento que el patrón implementa. No todos muestran explícitamente la clase del patrón: por ejemplo, el flujo de bloqueo documenta la clonación, mientras la clase concreta `Bloqueo` la realiza en Python.

| Patrón / decisión | Requerimiento → caso de uso → diagrama → clase / método → simulación | Si se quitara sin sustituir su responsabilidad |
|---|---|---|
| Factory Method | RF-01, RF-03 → CU-01.5 y CU-03.3 → secuencia (creación) y estados (cancelación) → `CreadorReserva.crear_reserva()` / `_instanciar()` → E1, E4. | Cada ruta de creación individual o recurrente tendría que elegir la clase concreta y asignarle su política. Volverían las decisiones por tipo y el riesgo de crear una reserva oficial con política regular. |
| Abstract Factory | RF-13, RF-14; RNF-06 → CU-01.3/6 → secuencia (validar sede y notificar) → `FabricaSede.crear_familia()` / `FamiliaSede` → E1, E2. | El cliente tendría que elegir por separado validador y notificador con condiciones por sede; podría mezclar el horario de Norte con el canal de Sur. |
| Builder | RF-09 → CU-02.1/2 → actividad (datos y validación de la serie) → `ReservaRecurrenteBuilder.construir()` → E3, E9, E10. | Los llamadores tendrían que repetir el armado de obligatorios, valores por defecto y opcionales en constructores extensos. La validación del dominio seguiría siendo necesaria; el Builder centraliza la construcción. |
| Prototype | RF-11 → CU-04.3 → flujo CU-04 en [casos de uso y flujos](03_Casos_de_uso_y_flujos.pdf) → `Bloqueo.clonar()` → E6. | El bucle por cancha y fecha tendría que reconstruir manualmente motivo, horario y equipo. Una copia superficial compartiría el equipo mutable entre plantilla y clones. |
| Singleton | RF-15; RNF-07 → CU-01.4, CU-03.3/3a → secuencia, robustez y estados → `ConfiguracionReglas.obtener()` → E5, E9. | Si cada regla crease su propia configuración, podrían divergir sus valores. Se aceptó estado global compartido; inyectar una única configuración sería una alternativa válida, pero exigiría cambiar cómo se suministra a los colaboradores. |
| Strategy | RF-02, RF-03, RF-08 → CU-01.4 y CU-03.3/3a → secuencia, robustez y estados → `ReglaPrioridad.tiene_prioridad()` / `PoliticaCancelacion.evaluar()` → E4, E9. | La reserva o el coordinador necesitaría condicionales por tipo de solicitante para decidir prioridad y ventanas de cancelación; agregar una política obligaría a modificar esas ramas. |
| Facade | RF-01, RF-03, RF-09, RF-10, RF-12 → CU-01/02/03/04 → secuencia, actividad, robustez y flujo CU-04 → las cuatro operaciones de `ReservaUFacade` → E1–E7. | `simulacion.py` tendría que conocer el calendario, las fábricas, las políticas, los registros y los notificadores; repetiría el orden de coordinación y podría omitir validaciones. |
| Locking pesimista | RNF-04, RNF-05 → CU-01.4/5, CU-02.4/5 → secuencia (`critical`) y actividad (todo o nada) → `CalendarioReservas.lock` retenido por la Facade durante verificación y registro → E7, E3. | Dos hilos podrían observar la misma franja libre antes de registrar ambos. Proteger solo el registro no basta: volvería la carrera entre consulta y escritura y podrían aparecer resultados parciales en series. |

Esta revisión distingue los patrones de las reglas de negocio: el umbral de tres faltas pertenece a RF-08 y a `Estudiante`; Strategy decide si la cancelación genera una falta, Singleton aporta parámetros y Facade coordina la operación.

## Supuestos conservados

- Hora local institucional homogénea, sin zonas mezcladas. Los escenarios usan fechas fijas y pasan `ahora` explícitamente.
- Intervalos del mismo día `[inicio, fin)`; intervalos contiguos no se solapan. Se admite apertura exacta y cierre exacto.
- La prioridad oficial usa el inicio y el límite configurado; se conserva el desplazamiento individual del PSet 1. Una serie nunca desplaza: cualquier conflicto la rechaza.
- El mes del no-show es el de su registro. La suspensión empieza al tercero del mes, termina exactamente siete días después y no se prolonga por la cuarta falta del mismo mes. Cambiar de mes no cancela una suspensión vigente.
- Las ocurrencias de una serie se cancelan individualmente. Equipos/notas no implican inventario.
- Deshabilitar una cancha impide nuevas reservas; los bloqueos y la intervención administrativa anulan las existentes cuando corresponde.
- Las familias implementan los dos campus conocidos; el cambio de configuración se realiza entre operaciones. No se implementa autenticación de red ni se envían correos/SMS reales.

## Correcciones del PSet 1

Se incorpora `Administrador`; los umbrales usan `<` y no `<=`; el ejecutable y Docker apuntan a `simulacion.py`; la salida sigue CU y no una numeración RF inventada. Se validan propiedad, estado terminal, suspensión, cancha deshabilitada y todos los solapamientos antes de desplazar. El PSet 1 permanece separado.

## Evidencia de ejecución

`salida_simulacion.txt` contiene una ejecución local completa. `salida_docker.txt` conserva la ejecución completa dentro del contenedor: 10 escenarios, 42 comprobaciones y salida 0. Tanto `docker build -t reservau-v2 .` como `docker run reservau-v2` terminaron correctamente. Los detalles se registran en [VALIDACION.md](VALIDACION.md).
