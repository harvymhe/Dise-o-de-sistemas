"""Modelo rico: Reserva decide transiciones; Estudiante conoce sus faltas fechadas."""
from abc import ABC
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from configuracion import ConfiguracionReglas
from estrategias import SinPrioridad, PrioridadOficial, AnulacionAdministrativa
from objetosdevalor import EstadoReserva, RangoHorario, Sede


@dataclass(frozen=True)
class RegistroNoShow:
    reserva_id: str
    registrado_en: datetime


@dataclass(frozen=True)
class Suspension:
    inicio: datetime
    fin: datetime
    mes_origen: tuple

    def esta_vigente(self, ahora):
        return self.inicio <= ahora < self.fin


@dataclass
class Usuario(ABC):
    id_usuario: str
    nombre: str
    correo: str
    telefono: str = "0990000000"


@dataclass
class Estudiante(Usuario):
    estrategia_prioridad: object = field(default_factory=SinPrioridad, init=False)
    no_shows: list = field(default_factory=list, init=False)
    suspensiones: list = field(default_factory=list, init=False)

    def contar_no_shows(self, mes, anio):
        return sum((n.registrado_en.year, n.registrado_en.month) == (anio, mes)
                   for n in self.no_shows)

    def registrar_no_show(self, reserva, ahora):
        if any(n.reserva_id == reserva.id_reserva for n in self.no_shows):
            return
        self.no_shows.append(RegistroNoShow(reserva.id_reserva, ahora))
        mes = (ahora.year, ahora.month)
        reglas = ConfiguracionReglas.obtener()
        if (self.contar_no_shows(ahora.month, ahora.year) >= reglas.umbral_mensual
                and not any(s.mes_origen == mes for s in self.suspensiones)):
            self.suspensiones.append(Suspension(ahora, ahora + reglas.duracion_suspension, mes))

    def esta_suspendido(self, ahora):
        return any(s.esta_vigente(ahora) for s in self.suspensiones)

    def vencimiento_suspension(self, ahora):
        return max((s.fin for s in self.suspensiones if s.esta_vigente(ahora)), default=None)


@dataclass
class CapitanEquipo(Estudiante):
    nombre_equipo: str = "Equipo oficial"
    estrategia_prioridad: object = field(default_factory=PrioridadOficial, init=False)


@dataclass
class Administrador(Usuario):
    def gestionar_cancha(self, cancha, nombre=None, estado=None):
        if nombre is not None:
            cancha.nombre = nombre
        if estado is not None:
            cancha.cambiar_estado(estado)

    def intervenir_conflicto(self, reserva, motivo):
        if not motivo.strip():
            raise ValueError("Es obligatorio el motivo de intervención.")
        reserva.anular(motivo)

    def definir_bloqueo(self, motivo, inicio, fin, equipo=()):
        return Bloqueo(motivo, inicio, fin, list(equipo))


@dataclass
class Cancha:
    id_cancha: str
    nombre: str
    sede: Sede
    estado: str = "HABILITADA"

    def cambiar_estado(self, estado):
        if estado not in ("HABILITADA", "DESHABILITADA"):
            raise ValueError("Estado de cancha inválido.")
        self.estado = estado

    def esta_habilitada(self):
        return self.estado == "HABILITADA"


@dataclass
class Reserva:
    id_reserva: str
    cancha: Cancha
    solicitante: Estudiante
    rango_horario: RangoHorario
    politica_cancelacion: object
    estado: EstadoReserva = field(default=EstadoReserva.ACTIVA, init=False)
    motivo: str = field(default="", init=False)
    serie_id: str | None = None
    equipo_prestado: tuple = ()
    notas: str = ""

    def esta_activa(self):
        return self.estado == EstadoReserva.ACTIVA

    def cancelar(self, ahora, politica_autorizada=None):
        if not self.esta_activa():
            raise ValueError("Reserva terminal: no admite otra cancelación.")
        politica = politica_autorizada or self.politica_cancelacion
        self.estado = politica.evaluar(self.rango_horario, ahora)
        self.motivo = "Cancelación tardía" if self.estado == EstadoReserva.NO_SHOW else "Cancelación del solicitante"
        if self.estado == EstadoReserva.NO_SHOW:
            self.solicitante.registrar_no_show(self, ahora)
        return self.estado

    def anular(self, motivo):
        if not self.esta_activa():
            raise ValueError("Solo se puede anular una reserva activa.")
        self.estado = AnulacionAdministrativa().evaluar(self.rango_horario, None)
        self.motivo = motivo


class ReservaRegular(Reserva):
    pass


class ReservaEquipoOficial(Reserva):
    pass


@dataclass
class ReservaRecurrente:
    cancha: Cancha
    inicio: date
    franja_inicio: time
    franja_fin: time
    solicitante: CapitanEquipo
    semanas: int = 2
    equipo_prestado: tuple = ()
    notas: str = ""
    id_serie: str = ""

    def validar_datos(self):
        if not isinstance(self.solicitante, CapitanEquipo):
            raise ValueError("La recurrencia requiere capitán.")
        if type(self.semanas) is not int or not 2 <= self.semanas <= 8:
            raise ValueError("Semanas debe ser entero entre 2 y 8.")
        if self.cancha is None or not isinstance(self.inicio, date):
            raise ValueError("Faltan cancha o fecha inicial.")
        RangoHorario(datetime.combine(self.inicio, self.franja_inicio),
                     datetime.combine(self.inicio, self.franja_fin))

    def generar_ocurrencias(self):
        self.validar_datos()
        return tuple(RangoHorario(datetime.combine(self.inicio + timedelta(weeks=i), self.franja_inicio),
                                  datetime.combine(self.inicio + timedelta(weeks=i), self.franja_fin))
                     for i in range(self.semanas))


@dataclass
class Bloqueo:
    motivo: str
    inicio: time
    fin: time
    equipo: list = field(default_factory=list)
    cancha: Cancha | None = None
    fecha: date | None = None

    def clonar(self, cancha, fecha):
        # Prototype: deepcopy separa la lista y sus elementos mutables.
        clon = deepcopy(self)
        # La cancha sigue siendo la entidad canónica, no una copia de infraestructura.
        clon.cancha, clon.fecha = cancha, fecha
        return clon

    def rango(self):
        return RangoHorario(datetime.combine(self.fecha, self.inicio),
                            datetime.combine(self.fecha, self.fin))

    def se_solapa(self, rango):
        return self.rango().se_solapa(rango)
