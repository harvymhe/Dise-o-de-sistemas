"""Strategy de prioridad heredada y nuevas estrategias de cancelación."""
from abc import ABC, abstractmethod
from configuracion import ConfiguracionReglas
from objetosdevalor import EstadoReserva


class ReglaPrioridad(ABC):
    @abstractmethod
    def tiene_prioridad(self, rango):
        raise NotImplementedError


class PrioridadOficial(ReglaPrioridad):
    def tiene_prioridad(self, rango):
        return rango.es_antes_de(ConfiguracionReglas.obtener().limite_prioridad)


class SinPrioridad(ReglaPrioridad):
    def tiene_prioridad(self, rango):
        return False


class PoliticaCancelacion(ABC):
    @abstractmethod
    def evaluar(self, rango, ahora):
        raise NotImplementedError


class CancelacionEstudiante(PoliticaCancelacion):
    def evaluar(self, rango, ahora):
        return (EstadoReserva.NO_SHOW
                if rango.anticipacion(ahora) < ConfiguracionReglas.obtener().ventana_regular
                else EstadoReserva.CANCELADA)


class CancelacionCapitan(PoliticaCancelacion):
    def evaluar(self, rango, ahora):
        return (EstadoReserva.NO_SHOW
                if rango.anticipacion(ahora) < ConfiguracionReglas.obtener().ventana_oficial
                else EstadoReserva.CANCELADA)


class AnulacionAdministrativa(PoliticaCancelacion):
    def evaluar(self, rango, ahora):
        return EstadoReserva.CANCELADA
