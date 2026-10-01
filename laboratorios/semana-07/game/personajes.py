from abc import ABC


class Personaje(ABC):
    def __init__(self, nombre: str, vida: int, ataque: int):
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.estrategia = None

    def recibir_danio(self, cantidad: int):
        self.vida = max(0, self.vida - cantidad)

    def esta_vivo(self) -> bool:
        return self.vida > 0

    def cambiar_estrategia(self, estrategia):
        self.estrategia = estrategia

    def atacar(self, objetivo) -> int:
        if self.estrategia is None:
            raise ValueError("El personaje no tiene una estrategia de ataque.")

        danio = self.estrategia.calcular_danio(self.ataque)
        objetivo.recibir_danio(danio)

        return danio


class Guerrero(Personaje):
    def __init__(self):
        super().__init__(
            nombre="Guerrero",
            vida=100,
            ataque=20
        )


class Dragon(Personaje):
    def __init__(self):
        super().__init__(
            nombre="Dragón",
            vida=120,
            ataque=15
        )


class Soldado(Personaje):
    def __init__(self):
        super().__init__(
            nombre="Soldado",
            vida=100,
            ataque=20
        )


class Alien(Personaje):
    def __init__(self):
        super().__init__(
            nombre="Alien",
            vida=110,
            ataque=18
        )