from game.personajes import Guerrero, Dragon, Soldado, Alien


class PersonajeFactory:

    @staticmethod
    def crear(tipo: str):
        tipo = tipo.lower()

        personajes = {
            "guerrero": Guerrero,
            "dragon": Dragon,
            "soldado": Soldado,
            "alien": Alien
        }

        if tipo not in personajes:
            raise ValueError(
                f"Tipo de personaje no válido: {tipo}"
            )

        return personajes[tipo]()