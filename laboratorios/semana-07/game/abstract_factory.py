from abc import ABC, abstractmethod
from game.factory import PersonajeFactory


class MundoFactory(ABC):

    @abstractmethod
    def crear_jugador(self):
        pass

    @abstractmethod
    def crear_enemigo(self):
        pass


class FantasyFactory(MundoFactory):

    def crear_jugador(self):
        return PersonajeFactory.crear("guerrero")

    def crear_enemigo(self):
        return PersonajeFactory.crear("dragon")


class SciFiFactory(MundoFactory):

    def crear_jugador(self):
        return PersonajeFactory.crear("soldado")

    def crear_enemigo(self):
        return PersonajeFactory.crear("alien")