"""Calendario compartido: toda lectura/escritura de ocupación usa su RLock."""
from threading import RLock


class CalendarioReservas:
    def __init__(self):
        self.lock = RLock()
        self.reservas = {}
        self.series = {}
        self.bloqueos = []

    def consultar_disponibilidad(self, cancha, rango):
        with self.lock:
            conflictos = [r for r in self.reservas.values()
                          if r.cancha.id_cancha == cancha.id_cancha
                          and r.esta_activa() and r.rango_horario.se_solapa(rango)]
            bloqueada = any(b.cancha.id_cancha == cancha.id_cancha and b.se_solapa(rango)
                            for b in self.bloqueos)
            return cancha.esta_habilitada() and not bloqueada, conflictos

    def registrar_individual(self, reserva):
        with self.lock:
            self.reservas[reserva.id_reserva] = reserva

    def registrar_serie(self, serie, reservas):
        with self.lock:
            nuevas = {r.id_reserva: r for r in reservas}
            self.reservas.update(nuevas)
            self.series[serie.id_serie] = serie

    def aplicar_bloqueo(self, bloqueo):
        with self.lock:
            self.bloqueos.append(bloqueo)
