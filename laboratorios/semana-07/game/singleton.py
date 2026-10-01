class GameConfig:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)

        return cls._instancia

    def __init__(self):
        if not hasattr(self, "_inicializado"):
            self.dificultad = "normal"
            self.numero_maximo_turnos = 10
            self._inicializado = True

    def configurar(
        self,
        dificultad: str = "normal",
        numero_maximo_turnos: int = 10
    ):
        dificultades_validas = ["facil", "normal", "dificil"]

        if dificultad not in dificultades_validas:
            raise ValueError(
                "La dificultad debe ser facil, normal o dificil."
            )

        if numero_maximo_turnos <= 0:
            raise ValueError(
                "El número máximo de turnos debe ser mayor a 0."
            )

        self.dificultad = dificultad
        self.numero_maximo_turnos = numero_maximo_turnos

    def multiplicador_enemigo(self) -> float:
        multiplicadores = {
            "facil": 0.8,
            "normal": 1.0,
            "dificil": 1.2
        }

        return multiplicadores[self.dificultad]