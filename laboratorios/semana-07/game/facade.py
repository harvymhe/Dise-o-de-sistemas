from game.abstract_factory import FantasyFactory, SciFiFactory
from game.strategy import AtaqueNormal, AtaqueFuerte
from game.singleton import GameConfig


class GameFacade:

    def __init__(self):
        self.config = GameConfig()

        self.mundo_factory = None
        self.jugador = None
        self.enemigo = None

        self.turno_actual = 1

    def iniciar(self):
        self.mostrar_titulo()

        self.seleccionar_mundo()
        self.crear_personajes()

        # El enemigo siempre utiliza ataque normal.
        self.enemigo.cambiar_estrategia(AtaqueNormal())

        self.mostrar_personajes()

        while (
            self.jugador.esta_vivo()
            and self.enemigo.esta_vivo()
            and self.turno_actual <= self.config.numero_maximo_turnos
        ):
            self.ejecutar_turno()

        self.determinar_resultado()

    def mostrar_titulo(self):
        print("=" * 45)
        print("       VIDEOJUEGO DE COMBATE POR TURNOS")
        print("=" * 45)

        print(
            f"Dificultad: {self.config.dificultad.capitalize()}"
        )

        print(
            f"Máximo de turnos: "
            f"{self.config.numero_maximo_turnos}"
        )

    def seleccionar_mundo(self):
        while True:
            print("\nSeleccione un mundo:")
            print("1. Fantasía")
            print("2. Ciencia ficción")

            opcion = input("> ").strip()

            if opcion == "1":
                self.mundo_factory = FantasyFactory()

                print("\nMundo seleccionado: Fantasía")
                return

            if opcion == "2":
                self.mundo_factory = SciFiFactory()

                print("\nMundo seleccionado: Ciencia ficción")
                return

            print("Opción no válida. Intente nuevamente.")

    def crear_personajes(self):
        self.jugador = self.mundo_factory.crear_jugador()
        self.enemigo = self.mundo_factory.crear_enemigo()

    def mostrar_personajes(self):
        print("\n--- PERSONAJES ---")

        print(
            f"Jugador: {self.jugador.nombre} | "
            f"Vida: {self.jugador.vida} | "
            f"Ataque: {self.jugador.ataque}"
        )

        print(
            f"Enemigo: {self.enemigo.nombre} | "
            f"Vida: {self.enemigo.vida} | "
            f"Ataque: {self.enemigo.ataque}"
        )

    def seleccionar_estrategia(self):
        while True:
            print("\nSeleccione una estrategia de ataque:")
            print("1. Ataque normal")
            print("2. Ataque fuerte")

            opcion = input("> ").strip()

            if opcion == "1":
                self.jugador.cambiar_estrategia(
                    AtaqueNormal()
                )

                return

            if opcion == "2":
                self.jugador.cambiar_estrategia(
                    AtaqueFuerte()
                )

                return

            print("Opción no válida. Intente nuevamente.")

    def ejecutar_turno(self):
        print("\n" + "=" * 45)
        print(f"TURNO {self.turno_actual}")
        print("=" * 45)

        print(
            f"{self.jugador.nombre}: "
            f"{self.jugador.vida} HP"
        )

        print(
            f"{self.enemigo.nombre}: "
            f"{self.enemigo.vida} HP"
        )

        self.seleccionar_estrategia()

        self.ejecutar_ataque_jugador()

        if self.enemigo.esta_vivo():
            self.ejecutar_ataque_enemigo()

        self.turno_actual += 1

    def ejecutar_ataque_jugador(self):
        danio = self.jugador.atacar(self.enemigo)

        print(
            f"\n{self.jugador.nombre} ataca a "
            f"{self.enemigo.nombre}."
        )

        print(
            f"{self.enemigo.nombre} recibe "
            f"{danio} de daño."
        )

        print(
            f"Vida restante de {self.enemigo.nombre}: "
            f"{self.enemigo.vida}"
        )

    def ejecutar_ataque_enemigo(self):
        danio_base = self.enemigo.estrategia.calcular_danio(
            self.enemigo.ataque
        )

        danio = int(
            danio_base
            * self.config.multiplicador_enemigo()
        )

        self.jugador.recibir_danio(danio)

        print(
            f"\n{self.enemigo.nombre} responde al ataque."
        )

        print(
            f"{self.jugador.nombre} recibe "
            f"{danio} de daño."
        )

        print(
            f"Vida restante de {self.jugador.nombre}: "
            f"{self.jugador.vida}"
        )

    def determinar_resultado(self):
        print("\n" + "=" * 45)
        print("RESULTADO DE LA PARTIDA")
        print("=" * 45)

        if not self.enemigo.esta_vivo():
            print(
                f"¡{self.jugador.nombre} ha ganado!"
            )

        elif not self.jugador.esta_vivo():
            print(
                f"¡{self.enemigo.nombre} ha ganado!"
            )

        else:
            print(
                "Se alcanzó el número máximo de turnos."
            )

            print("La partida termina en empate.")

        print(
            f"\nTurnos jugados: "
            f"{self.turno_actual - 1}"
        )