"""Facade: único punto del cliente para operar sobre reservas.

El lock del calendario se conserva entre comprobar y registrar. También protege
cancelaciones, suspensiones y bloqueos. Los avisos se emiten después del cambio.
"""
from dataclasses import dataclass, field
from copy import deepcopy
from datetime import datetime
from itertools import count
from threading import Lock, current_thread
from calendario import CalendarioReservas
from creacion import creador_para, ReservaRecurrenteBuilder
from entidades import Estudiante, CapitanEquipo, Administrador, Cancha
from estrategias import AnulacionAdministrativa
from objetosdevalor import EstadoReserva, RangoHorario, Sede
from sedes import fabrica_para
from flujos import PASOS


@dataclass(frozen=True)
class Resultado:
    ok: bool
    mensaje: str
    datos: dict = field(default_factory=dict)


class ReservaUFacade:
    def __init__(self, usuarios, canchas, salida=print):
        self._usuarios = {u.id_usuario: u for u in usuarios}
        self._canchas = {c.id_cancha: c for c in canchas}
        self._calendario = CalendarioReservas()
        self._familias = {s: fabrica_para(s).crear_familia() for s in Sede}
        self._ids = count(1)
        self._series_ids = count(1)
        self._conflictos = {}
        self._salida = salida
        self._salida_lock = Lock()

    def _paso(self, cu, numero, detalle=""):
        texto = PASOS[cu].get(str(numero), "Verificación semanal" if str(numero).startswith('4.semana-') else "Flujo alterno")
        with self._salida_lock:
            self._salida(f"[{current_thread().name} | {cu}.{numero}] {texto}" + (f" | {detalle}" if detalle else ""))

    def _rechazar(self, cu, alterno, mensaje, **datos):
        self._paso(cu, alterno, f"RECHAZO: {mensaje}")
        return Resultado(False, mensaje, datos)

    def _registrado(self, actor):
        return self._usuarios.get(getattr(actor, 'id_usuario', None)) is actor

    def _es_admin(self, actor):
        return self._registrado(actor) and isinstance(actor, Administrador)

    def _cancha(self, cancha_id):
        if cancha_id not in self._canchas:
            raise ValueError("Cancha inexistente.")
        return self._canchas[cancha_id]

    @staticmethod
    def _validar_ahora(ahora):
        if not isinstance(ahora, datetime) or ahora.tzinfo is not None:
            raise ValueError("Se requiere fecha y hora local institucional.")

    @staticmethod
    def _vista(r):
        return dict(id=r.id_reserva, tipo=type(r).__name__, estado=r.estado.value,
                    cancha=r.cancha.id_cancha, sede=r.cancha.sede.value,
                    solicitante=r.solicitante.id_usuario, rango=str(r.rango_horario),
                    motivo=r.motivo, serie=r.serie_id, equipo=r.equipo_prestado,
                    notas=r.notas, politica=type(r.politica_cancelacion).__name__)

    def _aviso(self, r, evento):
        return self._familias[r.cancha.sede].notificar(
            r.solicitante, f"{evento}: {r.id_reserva}, cancha {r.cancha.id_cancha}, {r.rango_horario}; {r.motivo}")

    def _emitir(self, cu, avisos):
        for aviso in avisos:
            with self._salida_lock:
                self._salida(f"[{current_thread().name} | {cu}.6 AVISO] {aviso}")

    def reservar(self, actor, cancha_id, inicio, fin, ahora):
        cu = 'CU-01'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            try:
                self._validar_ahora(ahora)
                if not self._registrado(actor) or not isinstance(actor, Estudiante):
                    raise ValueError("Solicitante no habilitado como estudiante/capitán registrado.")
                rango, cancha = RangoHorario(inicio, fin), self._cancha(cancha_id)
                creador = creador_para(actor)
            except (ValueError, TypeError, AttributeError) as exc:
                return self._rechazar(cu, '2a', str(exc))
            if actor.esta_suspendido(ahora):
                return self._rechazar(cu, '2b', f"Suspensión hasta {actor.vencimiento_suspension(ahora)}")
            self._paso(cu, 3, cancha.sede.value)
            if not self._familias[cancha.sede].admite(rango):
                return self._rechazar(cu, '3a', f"Fuera del horario de {cancha.sede.value}.")
            self._paso(cu, 4)
            operativa, conflictos = self._calendario.consultar_disponibilidad(cancha, rango)
            desplazables = actor.estrategia_prioridad.tiene_prioridad(rango) and all(
                not r.solicitante.estrategia_prioridad.tiene_prioridad(r.rango_horario) for r in conflictos)
            if not operativa or (conflictos and not desplazables):
                conflicto_id = None
                if conflictos:
                    conflicto_id = f'C{len(self._conflictos)+1:03d}'
                    self._conflictos[conflicto_id] = tuple(r.id_reserva for r in conflictos)
                    for admin in self._usuarios.values():
                        if isinstance(admin, Administrador):
                            self._paso(cu, '4a', self._familias[cancha.sede].notificar(
                                admin, f"Conflicto {conflicto_id}: {', '.join(self._conflictos[conflicto_id])}"))
                return self._rechazar(cu, '4a', "Cancha no disponible.", conflicto=conflicto_id)
            if conflictos:
                self._paso(cu, '4b', "Todos los conflictos son desplazables; plan sin cambios todavía.")
            self._paso(cu, 5)
            reserva = creador.crear_reserva(f'R{next(self._ids):03d}', actor, cancha, rango)
            avisos = []
            for anterior in conflictos:
                anterior.anular("Desplazamiento por prioridad oficial")
                avisos.append(self._aviso(anterior, 'ANULADA SIN PENALIDAD'))
            self._calendario.registrar_individual(reserva)
            avisos.append(self._aviso(reserva, 'CONFIRMADA'))
            datos = self._vista(reserva)
        self._paso(cu, 6)
        self._emitir(cu, avisos)
        return Resultado(True, 'Reserva confirmada.', datos)

    def reservar_recurrente(self, actor, cancha_id, fecha, inicio, fin, ahora,
                           semanas=2, equipo=(), notas=""):
        cu = 'CU-02'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            try:
                self._validar_ahora(ahora)
                if not self._registrado(actor):
                    raise ValueError("Actor no registrado.")
                cancha = self._cancha(cancha_id)
                serie = (ReservaRecurrenteBuilder().para(cancha, actor).desde(fecha, inicio, fin)
                         .durante(semanas).con_equipo(equipo).con_notas(notas).construir())
            except (ValueError, TypeError, AttributeError) as exc:
                return self._rechazar(cu, '2a', str(exc))
            if actor.esta_suspendido(ahora):
                return self._rechazar(cu, '2b', f"Suspensión hasta {actor.vencimiento_suspension(ahora)}")
            self._paso(cu, 3)
            rangos = serie.generar_ocurrencias()
            self._paso(cu, 4)
            for semana, rango in enumerate(rangos, 1):
                operativa, conflictos = self._calendario.consultar_disponibilidad(cancha, rango)
                valida = self._familias[cancha.sede].admite(rango) and operativa and not conflictos
                self._paso(cu, f'4.semana-{semana}', f"{rango}: {'válida' if valida else 'conflicto o franja inválida'}")
                if not valida:
                    return self._rechazar(cu, '4a', f"Semana {semana}, fecha {rango.hora_inicio:%Y-%m-%d}. Cero ocurrencias registradas.", semana=semana)
            self._paso(cu, 5)
            serie.id_serie = f'S{next(self._series_ids):03d}'
            creador = creador_para(actor)
            reservas = tuple(creador.crear_reserva(f'R{next(self._ids):03d}', actor, cancha, rango,
                             serie_id=serie.id_serie, equipo_prestado=serie.equipo_prestado, notas=serie.notas)
                             for rango in rangos)
            self._calendario.registrar_serie(serie, reservas)
            avisos = [self._aviso(r, f'SERIE {serie.id_serie} CONFIRMADA') for r in reservas]
            vistas = tuple(self._vista(r) for r in reservas)
        self._paso(cu, 6)
        self._emitir(cu, avisos)
        return Resultado(True, 'Serie completa confirmada.', dict(serie=serie.id_serie, reservas=vistas))

    def cancelar(self, actor, reserva_id, ahora, motivo=""):
        cu = 'CU-03'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            r = self._calendario.reservas.get(reserva_id)
            admin = self._es_admin(actor)
            try:
                self._validar_ahora(ahora)
                if (not self._registrado(actor) or r is None or not r.esta_activa()
                        or (not admin and r.solicitante is not actor) or (admin and not motivo.strip())):
                    raise ValueError("Reserva inexistente, terminal, ajena o anulación sin motivo.")
            except (ValueError, TypeError, AttributeError) as exc:
                return self._rechazar(cu, '2a', str(exc))
            self._paso(cu, 3)
            politica = AnulacionAdministrativa() if admin else r.politica_cancelacion
            estado = politica.evaluar(r.rango_horario, ahora)
            if estado == EstadoReserva.NO_SHOW:
                self._paso(cu, '3a', 'Anticipación estrictamente menor al umbral; sustituye el paso 4.')
            else:
                self._paso(cu, 4)
            if admin:
                actor.intervenir_conflicto(r, motivo)
            else:
                r.cancelar(ahora, politica)
            if estado == EstadoReserva.NO_SHOW:
                self._paso(cu, '3a', f"Faltas del mes: {r.solicitante.contar_no_shows(ahora.month, ahora.year)}; suspendido={r.solicitante.esta_suspendido(ahora)}; vence={r.solicitante.vencimiento_suspension(ahora)}")
            self._paso(cu, 5, f'{r.id_reserva}: {r.estado.value}')
            vista, avisos = self._vista(r), [self._aviso(r, r.estado.value)]
        self._paso(cu, 6)
        self._emitir(cu, avisos)
        return Resultado(True, 'Cancelación procesada.', vista)

    def bloquear(self, admin, plantilla, destinos, ahora):
        cu = 'CU-04'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            try:
                self._validar_ahora(ahora)
                if not self._es_admin(admin) or not plantilla.motivo.strip() or not destinos:
                    raise ValueError("Administrador, motivo y destinos son obligatorios.")
                datos = [(self._cancha(id_cancha), fecha) for id_cancha, fecha in destinos]
                for cancha, fecha in datos:
                    RangoHorario(datetime.combine(fecha, plantilla.inicio), datetime.combine(fecha, plantilla.fin))
            except (ValueError, TypeError, AttributeError) as exc:
                return self._rechazar(cu, '2a', str(exc))
            self._paso(cu, 3)
            clones = [plantilla.clonar(cancha, fecha) for cancha, fecha in datos]
            avisos, anuladas = [], []
            for clon in clones:
                self._paso(cu, 4, f'{clon.cancha.id_cancha}: {clon.fecha}')
                _, afectadas = self._calendario.consultar_disponibilidad(clon.cancha, clon.rango())
                self._calendario.aplicar_bloqueo(clon)
                if not afectadas:
                    self._paso(cu, '4a', 'Sin afectados para este clon; continuar con el siguiente.')
                    continue
                self._paso(cu, 5)
                for r in afectadas:
                    r.anular(clon.motivo)
                    anuladas.append(r.id_reserva)
                    avisos.append(self._aviso(r, 'ANULADA POR BLOQUEO SIN PENALIDAD'))
            datos = dict(anuladas=tuple(anuladas), bloqueos=len(clones),
                         equipos=tuple(tuple(deepcopy(clon.equipo)) for clon in clones))
        self._paso(cu, 6)
        self._emitir(cu, avisos)
        return Resultado(True, 'Bloqueos aplicados.', datos)

    def gestionar_cancha(self, admin, cancha_id, nombre=None, estado=None, sede=None):
        cu = 'CU-05'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            if not self._es_admin(admin) or estado not in (None, 'HABILITADA', 'DESHABILITADA'):
                return self._rechazar(cu, '2a', 'Rol o estado inválido.')
            if sede is not None:
                if cancha_id in self._canchas or not isinstance(sede, Sede) or not nombre:
                    return self._rechazar(cu, '2a', 'Alta con ID duplicado, nombre ausente o sede inválida.')
                cancha = Cancha(cancha_id, nombre, sede)
            else:
                cancha = self._canchas.get(cancha_id)
                if cancha is None:
                    return self._rechazar(cu, '2a', 'Cancha inexistente.')
            self._paso(cu, 3)
            admin.gestionar_cancha(cancha, nombre, estado)
            self._canchas[cancha_id] = cancha
            if estado == 'DESHABILITADA':
                self._paso(cu, '3a', 'Nuevas reservas impedidas; las anteriores se conservan.')
            self._paso(cu, 4)
            return Resultado(True, 'Cancha gestionada.', dict(cancha=cancha_id, estado=cancha.estado))

    def intervenir_conflicto(self, admin, conflicto_id, reserva_id, motivo, ahora):
        cu = 'CU-06'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            implicadas = self._conflictos.get(conflicto_id)
            if not self._es_admin(admin) or implicadas is None:
                return self._rechazar(cu, '2a', 'Sin autorización o conflicto inexistente.')
            self._paso(cu, 2, f'Reservas: {implicadas}')
            self._paso(cu, 3)
            if reserva_id is None:
                self._paso(cu, '3a', 'Cerrar sin anular.')
                return Resultado(True, 'Revisión sin cambios.')
            if reserva_id not in implicadas:
                return self._rechazar(cu, '2a', 'Reserva no pertenece a este conflicto.')
        self._paso(cu, 4)
        resultado = self.cancelar(admin, reserva_id, ahora, motivo)
        if not resultado.ok:
            self._paso(cu, '4a', 'CU-03 rechazó la anulación; estado actual conservado.')
        self._paso(cu, 5)
        return resultado

    def consultar_disponibilidad(self, actor, cancha_id, inicio, fin):
        cu = 'CU-07'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            try:
                if not self._registrado(actor):
                    raise ValueError('Actor no registrado.')
                cancha, rango = self._cancha(cancha_id), RangoHorario(inicio, fin)
            except (ValueError, TypeError, AttributeError) as exc:
                return self._rechazar(cu, '2a', str(exc))
            self._paso(cu, 3)
            operativa, conflictos = self._calendario.consultar_disponibilidad(cancha, rango)
            disponible = self._familias[cancha.sede].admite(rango) and operativa and not conflictos
            if not disponible:
                self._paso(cu, '3a', 'No disponible por horario, estado, bloqueo o reserva.')
            self._paso(cu, 4, f'disponible={disponible}; la consulta no retiene la franja.')
            return Resultado(True, 'Consulta realizada.', dict(disponible=disponible))

    def consultar_historial(self, actor):
        cu = 'CU-08'
        self._paso(cu, 1)
        with self._calendario.lock:
            self._paso(cu, 2)
            if not self._registrado(actor) or not isinstance(actor, Estudiante):
                return self._rechazar(cu, '2a', 'Solicitante no registrado.')
            reservas = tuple(self._vista(r) for r in self._calendario.reservas.values() if r.solicitante is actor)
            if reservas:
                self._paso(cu, 3, str(reservas))
            else:
                self._paso(cu, '2a', 'Lista vacía; continuar en 4.')
            self._paso(cu, 4)
            return Resultado(True, 'Historial consultado.', dict(reservas=reservas))

    def resumen_solicitante(self, actor, ahora):
        """Lectura de apoyo a la simulación; nunca devuelve la entidad mutable."""
        with self._calendario.lock:
            if not self._registrado(actor) or not isinstance(actor, Estudiante):
                return Resultado(False, 'Solicitante inválido.')
            return Resultado(True, 'Resumen.', dict(faltas_mes=actor.contar_no_shows(ahora.month, ahora.year),
                             suspendido=actor.esta_suspendido(ahora), vence=actor.vencimiento_suspension(ahora)))
