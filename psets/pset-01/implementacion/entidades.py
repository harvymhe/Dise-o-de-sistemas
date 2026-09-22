from abc import ABC
from datetime import datetime, timedelta
from estrategias import ReglaPrioridad, SinPrioridad
from objetosdevalor import EstadoReserva, RangoHorario

class Usuario(ABC):
    def __init__(self, id_usuario: str, nombre: str, correo: str):
        self._id = id_usuario
        self.nombre = nombre
        self.correo = correo

class Estudiante(Usuario):
    LIMITE_FALTAS = 3

    def __init__(self, id_usuario: str, nombre: str, correo: str, estrategia: ReglaPrioridad = None):
        super().__init__(id_usuario, nombre, correo)
        self.estrategia_prioridad = estrategia or SinPrioridad()
        self.contador_no_shows = 0
        self.suspendido = False

    def registrar_no_show(self):
        self.contador_no_shows += 1
        if self.contador_no_shows >= self.LIMITE_FALTAS:
            self.suspendido = True

    def cancelar_reserva(self, reserva: 'Reserva', tiempo_actual: datetime):
        reserva.evaluar_no_show(tiempo_actual)

class CapitanEquipo(Estudiante):
    def __init__(self, id_usuario: str, nombre: str, correo: str, nombre_equipo: str, estrategia: ReglaPrioridad):
        super().__init__(id_usuario, nombre, correo, estrategia)
        self.nombre_equipo = nombre_equipo

class Cancha:
    def __init__(self, id_cancha: str, nombre: str):
        self.id_cancha = id_cancha
        self.nombre = nombre
        self.estado = "Habilitada"
        self.reservas_activas = []

    def cambiar_estado(self, nuevo_estado: str): 
        self.estado = nuevo_estado

    def intentar_reservar(self, nueva_reserva: 'Reserva') -> str:
        for existente in self.reservas_activas:
            if existente.estado == EstadoReserva.ACTIVA:
                se_solapan = (
                    nueva_reserva.rango_horario.hora_inicio < existente.rango_horario.hora_fin and
                    nueva_reserva.rango_horario.hora_fin > existente.rango_horario.hora_inicio
                )
                if se_solapan:
                    nuevo_prioridad = nueva_reserva.solicitante.estrategia_prioridad.tiene_prioridad(nueva_reserva.rango_horario)
                    existente_prioridad = existente.solicitante.estrategia_prioridad.tiene_prioridad(existente.rango_horario)
                    
                    if nuevo_prioridad and not existente_prioridad:
                        existente.estado = EstadoReserva.CANCELADA
                        self.reservas_activas.remove(existente)
                        self.reservas_activas.append(nueva_reserva)
                        return "Conflicto resuelto: El Capitán desplazó al estudiante regular por prioridad oficial."
                    else:
                        return "Conflicto denegado: La cancha está ocupada y el solicitante no tiene prioridad superior."
        
        self.reservas_activas.append(nueva_reserva)
        return "Reserva creada exitosamente sin conflictos."

class Reserva:
    def __init__(self, id_reserva: str, cancha: Cancha, solicitante: Estudiante, rango: RangoHorario):
        self.id_reserva = id_reserva
        self.cancha = cancha
        self.solicitante = solicitante
        self.rango_horario = rango 
        self.estado = EstadoReserva.ACTIVA

    def evaluar_no_show(self, tiempo_actual: datetime):
        if self.estado != EstadoReserva.ACTIVA:
            raise ValueError("Solo se pueden cancelar reservas activas.")
        
        tiempo_faltante = self.rango_horario.hora_inicio - tiempo_actual
        if tiempo_faltante <= timedelta(hours=2):
            self.estado = EstadoReserva.NO_SHOW
            self.solicitante.registrar_no_show()
        else:
            self.estado = EstadoReserva.CANCELADA