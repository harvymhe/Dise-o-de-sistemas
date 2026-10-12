"""Factory Method y Builder: crear productos completos antes del registro."""
from abc import ABC, abstractmethod
from entidades import (Estudiante, CapitanEquipo, ReservaRegular,
                       ReservaEquipoOficial, ReservaRecurrente)
from estrategias import CancelacionEstudiante, CancelacionCapitan


class CreadorReserva(ABC):
    def crear_reserva(self, id_reserva, solicitante, cancha, rango, **opcionales):
        return self._instanciar(id_reserva, cancha, solicitante, rango, **opcionales)

    @abstractmethod
    def _instanciar(self, id_reserva, cancha, solicitante, rango, **opcionales):
        raise NotImplementedError


class CreadorRegular(CreadorReserva):
    def _instanciar(self, id_reserva, cancha, solicitante, rango, **opcionales):
        return ReservaRegular(id_reserva, cancha, solicitante, rango,
                              CancelacionEstudiante(), **opcionales)


class CreadorOficial(CreadorReserva):
    def _instanciar(self, id_reserva, cancha, solicitante, rango, **opcionales):
        return ReservaEquipoOficial(id_reserva, cancha, solicitante, rango,
                                    CancelacionCapitan(), **opcionales)


_CREADORES = {Estudiante: CreadorRegular(), CapitanEquipo: CreadorOficial()}


def creador_para(solicitante):
    """Único punto de selección del creador; el producto lo decide su Factory Method."""
    try:
        return _CREADORES[type(solicitante)]
    except KeyError:
        raise ValueError("El actor no puede solicitar reservas.") from None


class ReservaRecurrenteBuilder:
    def __init__(self):
        self._datos = {}

    def para(self, cancha, solicitante):
        self._datos.update(cancha=cancha, solicitante=solicitante)
        return self

    def desde(self, fecha, inicio, fin):
        self._datos.update(inicio=fecha, franja_inicio=inicio, franja_fin=fin)
        return self

    def durante(self, semanas=2):
        self._datos['semanas'] = semanas
        return self

    def con_equipo(self, equipo=()):
        self._datos['equipo_prestado'] = tuple(equipo)
        return self

    def con_notas(self, notas=""):
        self._datos['notas'] = notas
        return self

    def construir(self):
        obligatorios = {'cancha', 'solicitante', 'inicio', 'franja_inicio', 'franja_fin'}
        if not obligatorios <= self._datos.keys():
            raise ValueError("Faltan datos obligatorios de la recurrencia.")
        serie = ReservaRecurrente(**self._datos)
        serie.validar_datos()
        return serie
