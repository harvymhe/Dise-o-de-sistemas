"""Demostración ejecutable por casos de uso; operaciones de reservas solo vía Facade."""
from datetime import datetime, date, time, timedelta
from threading import Barrier, Thread
from queue import Queue
import sys
from configuracion import ConfiguracionReglas
from entidades import Estudiante, CapitanEquipo, Administrador, Cancha
from fachada import ReservaUFacade
from objetosdevalor import Sede


AHORA = datetime(2026, 10, 1, 8)


def titulo(texto):
    print(f"\n{'=' * 78}\n{texto}\n{'=' * 78}")


def comprobar(condicion, descripcion):
    if not condicion:
        raise RuntimeError(f"La demostración no cumple: {descripcion}")
    print(f"[VALIDADO] {descripcion}")


def entorno():
    ana = Estudiante('U1', 'Ana', 'ana@u.edu', '0991111111')
    bruno = Estudiante('U2', 'Bruno', 'bruno@u.edu', '0992222222')
    cap = CapitanEquipo('U3', 'Carlos', 'carlos@u.edu', '0993333333', nombre_equipo='Tigres')
    admin = Administrador('A1', 'Andrea', 'admin@u.edu', '0994444444')
    canchas = [Cancha('N1', 'Cancha Norte 1', Sede.NORTE),
               Cancha('N2', 'Cancha Norte 2', Sede.NORTE),
               Cancha('S1', 'Cancha Sur 1', Sede.SUR)]
    return ReservaUFacade([ana, bruno, cap, admin], canchas), ana, bruno, cap, admin, canchas


def horas(dia, inicio=16, fin=17):
    return datetime(2026, 10, dia, inicio), datetime(2026, 10, dia, fin)


def escenario_1():
    titulo('E1 | CU-01: una reserva en cada sede | RF-01, RF-13, RF-14')
    f, ana, _, _, _, _ = entorno()
    norte = f.reservar(ana, 'N1', *horas(5, 6, 7), AHORA)
    sur = f.reservar(ana, 'S1', *horas(5, 22, 23), AHORA)
    comprobar(norte.ok and sur.ok, 'Norte acepta 06-07 y Sur acepta 22-23; avisos por correo y texto.')
    comprobar(norte.datos['politica'] == 'CancelacionEstudiante', 'Factory Method asigna la política al crear.')


def escenario_2():
    titulo('E2 | CU-01, alterno 3a: horario inválido | RF-13')
    f, ana, _, _, _, _ = entorno()
    r = f.reservar(ana, 'S1', *horas(5, 6, 7), AHORA)
    comprobar(not r.ok and not f.consultar_historial(ana).datos['reservas'],
              'Sur rechaza 06-07 sin registrar ninguna reserva.')


def escenario_3():
    titulo('E3 | CU-02: recurrencia completa y rechazo todo o nada | RF-09, RF-10')
    f, ana, _, cap, _, _ = entorno()
    serie = f.reservar_recurrente(cap, 'N1', date(2026, 10, 5), time(14), time(15),
                                 AHORA, semanas=4, equipo=['balones', 'red'], notas='Dejar red montada.')
    comprobar(serie.ok and len(serie.datos['reservas']) == 4, 'Cuatro ocurrencias oficiales y sus políticas asignadas.')
    comprobar(all(r['equipo'] == ('balones', 'red') and r['notas'] == 'Dejar red montada.'
                  for r in serie.datos['reservas']), 'Builder conserva equipo y notas en cada semana.')
    existente = f.reservar(ana, 'S1', *horas(19, 14, 15), AHORA)
    antes = f.consultar_historial(cap).datos['reservas']
    fallida = f.reservar_recurrente(cap, 'S1', date(2026, 10, 5), time(14), time(15), AHORA, semanas=4)
    despues = f.consultar_historial(cap).datos['reservas']
    comprobar(not fallida.ok and fallida.datos['semana'] == 3 and antes == despues,
              'Conflicto en semana 3: cero registros parciales y ninguna reserva oficial nueva.')
    historial = f.consultar_historial(ana).datos['reservas']
    comprobar(existente.ok and historial[0]['estado'] == 'ACTIVA', 'La serie rechazada no desplaza la reserva anterior.')


def escenario_4():
    titulo('E4 | CU-03: tres políticas de cancelación | RF-03, RF-07')
    f, ana, bruno, cap, admin, _ = entorno()
    a = f.reservar(ana, 'N1', *horas(5), AHORA)
    b = f.reservar(cap, 'N2', *horas(5), AHORA)
    c = f.reservar(bruno, 'S1', *horas(5), AHORA)
    normal = f.cancelar(ana, a.datos['id'], datetime(2026, 10, 5, 14))
    tarde = f.cancelar(cap, b.datos['id'], datetime(2026, 10, 5, 8))
    administrativa = f.cancelar(admin, c.datos['id'], datetime(2026, 10, 5, 15, 59), 'Mantenimiento')
    comprobar(normal.datos['estado'] == 'CANCELADA', 'Dos horas exactas: cancelación normal del estudiante.')
    comprobar(tarde.datos['estado'] == 'NO_SHOW', 'Capitán con ocho horas de anticipación: no-show.')
    comprobar(administrativa.datos['estado'] == 'CANCELADA' and
              f.resumen_solicitante(bruno, datetime(2026, 10, 5, 16)).datos['faltas_mes'] == 0,
              'Administrador anula sin penalidad.')
    repetida = f.cancelar(cap, b.datos['id'], datetime(2026, 10, 5, 9))
    comprobar(not repetida.ok and f.resumen_solicitante(cap, datetime(2026, 10, 5, 9)).datos['faltas_mes'] == 1,
              'Cancelar una reserva terminal no duplica faltas.')


def escenario_5():
    titulo('E5 | CU-03 → CU-01: tres no-shows mensuales y suspensión | RF-08')
    f, ana, _, _, _, _ = entorno()
    reservas = [f.reservar(ana, 'N1', *horas(d), AHORA) for d in (10, 11, 12)]
    for dia, r in zip((10, 11, 12), reservas):
        f.cancelar(ana, r.datos['id'], datetime(2026, 10, dia, 15))
    ahora = datetime(2026, 10, 12, 15)
    resumen = f.resumen_solicitante(ana, ahora).datos
    rechazada = f.reservar(ana, 'N1', *horas(22), ahora)
    comprobar(resumen['faltas_mes'] == 3 and resumen['suspendido'] and not rechazada.ok,
              'Tres faltas de octubre activan suspensión y el alterno CU-01.2b.')
    vencimiento = resumen['vence']
    aceptada = f.reservar(ana, 'N1', *horas(22), vencimiento)
    comprobar(aceptada.ok and vencimiento == ahora + timedelta(days=7),
              'En el instante exacto de vencimiento puede volver a reservar.')


def escenario_6():
    titulo('E6 | CU-04: Prototype, bloqueo y anulación sin falta | RF-11, RF-12')
    f, ana, _, _, admin, canchas = entorno()
    r = f.reservar(ana, 'N1', *horas(15), AHORA)
    plantilla = admin.definir_bloqueo('Torneo universitario', time(15), time(18), ['red', 'balones'])
    clon_a = plantilla.clonar(canchas[0], date(2026, 10, 15))
    clon_b = plantilla.clonar(canchas[1], date(2026, 10, 15))
    clon_a.equipo.append('chalecos')
    comprobar(plantilla.equipo == ['red', 'balones'] and clon_b.equipo == ['red', 'balones'],
              'Cambiar un clon no altera plantilla ni otro clon (deepcopy).')
    bloqueos = f.bloquear(admin, plantilla, [('N1', date(2026, 10, 15)), ('N2', date(2026, 10, 15))], AHORA)
    comprobar(bloqueos.ok and bloqueos.datos['bloqueos'] == 2 and bloqueos.datos['anuladas'] == (r.datos['id'],),
              'Dos bloqueos aplicados; la reserva existente fue anulada y notificada.')
    comprobar(f.resumen_solicitante(ana, AHORA).datos['faltas_mes'] == 0,
              'Bloquear no genera penalidad al solicitante.')
    comprobar(not f.reservar(ana, 'N1', *horas(15), AHORA).ok, 'El bloqueo impide nuevas reservas solapadas.')


def escenario_7():
    titulo('E7 | CU-01 concurrente: dos hilos, una confirmación | RNF-04')
    f, ana, bruno, _, _, _ = entorno()
    for actor in (ana, bruno):
        comprobar(f.consultar_disponibilidad(actor, 'N1', *horas(20)).datos['disponible'],
                  f'{actor.nombre} ve inicialmente la franja libre.')
    barrera, resultados = Barrier(3), Queue()

    def solicitar(actor):
        try:
            barrera.wait(timeout=10)
            resultados.put(f.reservar(actor, 'N1', *horas(20), AHORA))
        except Exception as exc:
            resultados.put(exc)

    hilos = [Thread(target=solicitar, args=(actor,), name=actor.nombre, daemon=True) for actor in (ana, bruno)]
    for hilo in hilos:
        hilo.start()
    barrera.wait(timeout=10)
    for hilo in hilos:
        hilo.join(timeout=15)
    comprobar(not any(h.is_alive() for h in hilos), 'Ambos hilos terminan.')
    salidas = [resultados.get_nowait() for _ in hilos]
    for r in salidas:
        if isinstance(r, Exception):
            raise r
    confirmadas = sum(r.ok for r in salidas)
    activas = sum(r['estado'] == 'ACTIVA' for a in (ana, bruno)
                  for r in f.consultar_historial(a).datos['reservas'])
    comprobar(confirmadas == 1 and activas == 1, 'EXACTAMENTE 1 confirmación, 1 rechazo y 1 reserva activa.')


def escenario_8():
    titulo('E8 | CU-05, CU-06, CU-07 y CU-08: completar flujos administrativos')
    f, ana, bruno, _, admin, _ = entorno()
    comprobar(f.gestionar_cancha(admin, 'N3', 'Nueva cancha', sede=Sede.NORTE).ok, 'Administrador registra cancha.')
    f.gestionar_cancha(admin, 'N3', estado='DESHABILITADA')
    comprobar(not f.reservar(ana, 'N3', *horas(20), AHORA).ok, 'Cancha deshabilitada rechaza reservas.')
    f.gestionar_cancha(admin, 'N3', estado='HABILITADA')
    primera = f.reservar(ana, 'N3', *horas(20), AHORA)
    conflicto = f.reservar(bruno, 'N3', *horas(20), AHORA)
    intervencion = f.intervenir_conflicto(admin, conflicto.datos['conflicto'], primera.datos['id'],
                                        'Resolución de disputa por el administrador', AHORA)
    comprobar(intervencion.ok, 'El administrador interviene y CU-06 reutiliza CU-03.')
    comprobar(f.consultar_disponibilidad(bruno, 'N3', *horas(20)).datos['disponible'], 'Se liberó la franja.')
    comprobar(f.consultar_historial(ana).datos['reservas'][0]['motivo'].startswith('Resolución'),
              'El historial conserva estado y motivo de intervención.')


def escenario_9():
    titulo('E9 | Límites y regresiones del PSet 1 | RF-02, RF-03, RF-08, RF-09, RF-15')
    f, ana, bruno, cap, _, _ = entorno()
    anterior = f.reservar(ana, 'N1', *horas(5), AHORA)
    comprobar(f.reservar(cap, 'N1', *horas(5), AHORA).ok, 'Strategy oficial desplaza antes de las 18:00.')
    comprobar(f.consultar_historial(ana).datos['reservas'][0]['estado'] == 'CANCELADA', 'El desplazamiento conserva historial.')
    f.reservar(ana, 'N1', *horas(6, 18, 19), AHORA)
    comprobar(not f.reservar(cap, 'N1', *horas(6, 18, 19), AHORA).ok, 'A las 18:00 no existe prioridad oficial.')
    # Dos solapamientos: no desplazar al primero si el segundo no es desplazable.
    regular = f.reservar(bruno, 'N2', *horas(7, 14, 15), AHORA)
    f.reservar(cap, 'N2', *horas(7, 15, 16), AHORA)
    comprobar(not f.reservar(cap, 'N2', *horas(7, 14, 16), AHORA).ok, 'Se evalúan todos los conflictos antes de desplazar.')
    comprobar(f.consultar_historial(bruno).datos['reservas'][0]['estado'] == 'ACTIVA', 'No hay desplazamientos parciales.')
    r = f.reservar(cap, 'N1', *horas(8), AHORA)
    comprobar(f.cancelar(cap, r.datos['id'], datetime(2026, 10, 7, 16)).datos['estado'] == 'CANCELADA',
              'Veinticuatro horas exactas: cancelación oficial normal.')
    r = f.reservar(ana, 'S1', *horas(8), AHORA)
    comprobar(not f.cancelar(bruno, r.datos['id'], AHORA).ok, 'Un estudiante no cancela reservas ajenas.')
    comprobar(f.cancelar(ana, r.datos['id'], datetime(2026, 10, 8, 14, 1)).datos['estado'] == 'NO_SHOW',
              'Una hora y 59 minutos: no-show regular.')
    reglas = ConfiguracionReglas.obtener()
    comprobar(reglas is ConfiguracionReglas.obtener(), 'Singleton devuelve una única instancia.')
    anterior_umbral = reglas.ventana_regular
    try:
        reglas.ventana_regular = timedelta(hours=3)
        r = f.reservar(bruno, 'S1', *horas(9), AHORA)
        comprobar(f.cancelar(bruno, r.datos['id'], datetime(2026, 10, 9, 13, 30)).datos['estado'] == 'NO_SHOW',
                  'Cambiar la configuración a 3 h modifica la evaluación sin editar la Strategy.')
    finally:
        reglas.ventana_regular = anterior_umbral
    comprobar(not f.reservar_recurrente(cap, 'N1', date(2026, 10, 25), time(10), time(11), AHORA, semanas=9).ok,
              'Builder rechaza 9 semanas.')
    comprobar(f.reservar_recurrente(cap, 'S1', date(2026, 11, 2), time(10), time(11), AHORA).ok,
              'Builder usa 2 semanas cuando se omite el opcional.')


def escenario_10():
    titulo('E10 | Mes calendario, recurrencia máxima y suspensión de capitán | RF-08, RF-09')
    f, ana, _, cap, _, _ = entorno()
    fechas = [datetime(2026, 10, 30, 16), datetime(2026, 10, 31, 16), datetime(2026, 11, 1, 16)]
    reservas = [f.reservar(ana, 'N1', inicio, inicio + timedelta(hours=1), AHORA) for inicio in fechas]
    for inicio, r in zip(fechas, reservas):
        f.cancelar(ana, r.datos['id'], inicio - timedelta(hours=1))
    resumen = f.resumen_solicitante(ana, datetime(2026, 11, 1, 16)).datos
    comprobar(resumen['faltas_mes'] == 1 and not resumen['suspendido'],
              'Dos faltas de octubre y una de noviembre no activan suspensión.')
    serie = f.reservar_recurrente(cap, 'S1', date(2026, 12, 1), time(10), time(11), AHORA, semanas=8)
    comprobar(serie.ok and len(serie.datos['reservas']) == 8, 'Ocho semanas: límite superior admitido.')
    reservas = [f.reservar(cap, 'N2', *horas(d), AHORA) for d in (10, 11, 12, 13)]
    for dia, r in zip((10, 11, 12), reservas[:3]):
        f.cancelar(cap, r.datos['id'], datetime(2026, 10, dia, 8))
    antes = f.resumen_solicitante(cap, datetime(2026, 10, 12, 8)).datos['vence']
    f.cancelar(cap, reservas[3].datos['id'], datetime(2026, 10, 13, 8))
    despues = f.resumen_solicitante(cap, datetime(2026, 10, 13, 8)).datos['vence']
    comprobar(antes == despues, 'La cuarta falta del mes no prolonga la suspensión (SP-04).')
    denegada = f.reservar_recurrente(cap, 'S1', date(2026, 11, 20), time(10), time(11), datetime(2026, 10, 13, 8))
    comprobar(not denegada.ok, 'Un capitán suspendido tampoco crea recurrencias (CU-02.2b).')


def ejecutar_simulacion():
    for escenario in (escenario_1, escenario_2, escenario_3, escenario_4, escenario_5,
                      escenario_6, escenario_7, escenario_8, escenario_9, escenario_10):
        escenario()
    print('\nSIMULACIÓN COMPLETA: todos los escenarios y comprobaciones finalizaron correctamente.')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ejecutar_simulacion()
