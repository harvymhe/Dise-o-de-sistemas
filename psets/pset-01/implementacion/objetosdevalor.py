from enum import Enum
from datetime import datetime

print(">>> Cargando objetos de valor correctamente...")

class EstadoReserva(Enum):
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"
    NO_SHOW = "No-Show"

class RangoHorario:
    def __init__(self, hora_inicio: datetime, hora_fin: datetime):
        if hora_inicio >= hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la de fin.")
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin

    @property
    def hora_inicio(self) -> datetime:
        return self._hora_inicio

    @property
    def hora_fin(self) -> datetime:
        return self._hora_fin

    def es_antes_de_las_seis_pm(self) -> bool:
        return self._hora_inicio.hour < 18