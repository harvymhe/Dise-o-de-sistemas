from abc import ABC, abstractmethod
from objetosdevalor import RangoHorario

class ReglaPrioridad(ABC):
    @abstractmethod
    def tiene_prioridad(self, rango: RangoHorario) -> bool:
        pass

class PrioridadOficial(ReglaPrioridad):
    def tiene_prioridad(self, rango: RangoHorario) -> bool:
        return rango.es_antes_de_las_seis_pm()

class SinPrioridad(ReglaPrioridad):
    def tiene_prioridad(self, rango: RangoHorario) -> bool:
        return False