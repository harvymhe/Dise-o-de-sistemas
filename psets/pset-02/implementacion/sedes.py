"""Abstract Factory: familias coherentes, elegidas exclusivamente por la cancha."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time
from objetosdevalor import Sede


@dataclass(frozen=True)
class ValidadorHorario:
    sede: Sede
    apertura: time
    cierre: time

    def admite(self, rango):
        return self.apertura <= rango.hora_inicio.time() < rango.hora_fin.time() <= self.cierre


@dataclass(frozen=True)
class NotificadorSede:
    sede: Sede
    canal: str
    contacto: str

    def mensaje(self, usuario, contenido):
        return f"{self.sede.value} | {self.canal} a {getattr(usuario, self.contacto)} | {contenido}"


@dataclass(frozen=True)
class FamiliaSede:
    _validador: ValidadorHorario
    _notificador: NotificadorSede

    def __post_init__(self):
        if self._validador.sede != self._notificador.sede:
            raise ValueError("No se permite mezclar servicios de distintas sedes.")

    def admite(self, rango):
        return self._validador.admite(rango)

    def notificar(self, usuario, contenido):
        return self._notificador.mensaje(usuario, contenido)


class FabricaSede(ABC):
    @abstractmethod
    def crear_validador(self):
        raise NotImplementedError

    @abstractmethod
    def crear_notificador(self):
        raise NotImplementedError

    def crear_familia(self):
        return FamiliaSede(self.crear_validador(), self.crear_notificador())


class FabricaNorte(FabricaSede):
    def crear_validador(self):
        return ValidadorHorario(Sede.NORTE, time(6), time(22))

    def crear_notificador(self):
        return NotificadorSede(Sede.NORTE, "correo institucional", "correo")


class FabricaSur(FabricaSede):
    def crear_validador(self):
        return ValidadorHorario(Sede.SUR, time(7), time(23))

    def crear_notificador(self):
        return NotificadorSede(Sede.SUR, "mensaje de texto", "telefono")


_FABRICAS = {Sede.NORTE: FabricaNorte(), Sede.SUR: FabricaSur()}


def fabrica_para(sede):
    return _FABRICAS[sede]
