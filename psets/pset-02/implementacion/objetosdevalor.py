"""Intervalos inmutables y estados; se conserva el objeto de valor del PSet 1."""
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum


class EstadoReserva(Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"


class Sede(Enum):
    NORTE = "Campus Norte"
    SUR = "Campus Sur"

    @property
    def nombre(self):
        return self.value

    @property
    def apertura(self):
        from sedes import fabrica_para
        return fabrica_para(self).crear_validador().apertura

    @property
    def cierre(self):
        from sedes import fabrica_para
        return fabrica_para(self).crear_validador().cierre

    @property
    def canal(self):
        from sedes import fabrica_para
        return fabrica_para(self).crear_notificador().canal

    def admite(self, rango):
        from sedes import fabrica_para
        return fabrica_para(self).crear_familia().admite(rango)


@dataclass(frozen=True)
class RangoHorario:
    hora_inicio: datetime
    hora_fin: datetime

    def __post_init__(self):
        if self.hora_inicio.tzinfo or self.hora_fin.tzinfo:
            raise ValueError("Usar la misma hora local institucional, sin mezclar zonas.")
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("Inicio debe ser anterior al fin.")
        if self.hora_inicio.date() != self.hora_fin.date():
            raise ValueError("La franja debe quedar dentro del mismo día.")

    def se_solapa(self, otro):
        return self.hora_inicio < otro.hora_fin and otro.hora_inicio < self.hora_fin

    def anticipacion(self, ahora):
        return self.hora_inicio - ahora

    def es_antes_de(self, limite: time):
        return self.hora_inicio.time() < limite

    def es_antes_de_las_seis_pm(self):
        """Nombre heredado; el valor ya se obtiene de la configuración."""
        from configuracion import ConfiguracionReglas
        return self.es_antes_de(ConfiguracionReglas.obtener().limite_prioridad)

    def __str__(self):
        return f"{self.hora_inicio:%Y-%m-%d %H:%M}-{self.hora_fin:%H:%M}"
