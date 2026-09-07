from datetime import datetime, timedelta
from objetosdevalor import RangoHorario
from estrategias import PrioridadOficial, SinPrioridad
from entidades import Estudiante, CapitanEquipo, Cancha, Reserva

def ejecutar_simulacion():
    print("=== DEMOSTRACIÓN INTEGRAL DE LOS 8 REQUERIMIENTOS FUNCIONALES (RF) ===\n")
    
    print("[RF-01] Creando usuarios con roles diferenciados...")
    estudiante = Estudiante(id_usuario="U001", nombre="Ana", correo="ana@u.edu", estrategia=SinPrioridad())
    capitan = CapitanEquipo(id_usuario="U002", nombre="Carlos", correo="carlos@u.edu", nombre_equipo="Los Tigres", estrategia=PrioridadOficial())
    print(f" > Usuario registrado: {estudiante.nombre} (Estudiante Regular)")
    print(f" > Usuario registrado: {capitan.nombre} (Capitán de Equipo)\n")
    
    print("[RF-04] Configurando infraestructura de canchas...")
    cancha = Cancha(id_cancha="C1", nombre="Cancha Principal")
    cancha.cambiar_estado("Habilitada")
    print(f" > Cancha '{cancha.nombre}' configurada con estado: {cancha.estado}\n")
    
    print("[RF-05] Validando objetos de valor y rangos horarios...")
    rango_tarde = RangoHorario(datetime(2026, 10, 25, 16, 0), datetime(2026, 10, 25, 17, 0)) # 4:00 PM
    rango_noche = RangoHorario(datetime(2026, 10, 25, 19, 0), datetime(2026, 10, 25, 20, 0)) # 7:00 PM
    print(f" > Rango horario creado correctamente de {rango_tarde.hora_inicio.strftime('%H:%M')} a {rango_tarde.hora_fin.strftime('%H:%M')}\n")
    
    print("[RF-02] Evaluando prioridades horarias mediante Strategy...")
    print(f" > ¿Capitán tiene prioridad a las 4:00 PM (franja oficial < 18:00)?: {capitan.estrategia_prioridad.tiene_prioridad(rango_tarde)}")
    print(f" > ¿Capitán tiene prioridad a las 7:00 PM (fuera de franja)?: {capitan.estrategia_prioridad.tiene_prioridad(rango_noche)}\n")
    
    print("[RF-07] Simulando conflicto por solapamiento de horarios en la misma cancha...")
    reserva_ana = Reserva(id_reserva="R001", cancha=cancha, solicitante=estudiante, rango=rango_tarde)
    print(f" > Ana reserva primero: {cancha.intentar_reservar(reserva_ana)}")
    
    reserva_carlos = Reserva(id_reserva="R002", cancha=cancha, solicitante=capitan, rango=rango_tarde)
    print(f" > Carlos (Capitán) intenta ocupar el mismo espacio: {cancha.intentar_reservar(reserva_carlos)}")
    print(f" > Estado de la reserva de Ana tras el conflicto: [{reserva_ana.estado.value}]\n")
    
    print("[RF-06] Probando cancelación anticipada con más de 2 horas de margen...")
    reserva_anticipada = Reserva(id_reserva="R003", cancha=cancha, solicitante=estudiante, rango=rango_noche)
    tiempo_anticipado = rango_noche.hora_inicio - timedelta(hours=5) # Faltan 5 horas
    estudiante.cancelar_reserva(reserva_anticipada, tiempo_anticipado)
    print(f" > Cancelación con 5h de anticipación procesada. Estado resultante: [{reserva_anticipada.estado.value}]\n")
    
    print("[RF-03 & RF-08] Evaluando penalizaciones automáticas por No-Show y límites de faltas...")
    tiempo_tardio = rango_tarde.hora_inicio - timedelta(hours=1) # Falta 1 hora (menos de 2h)
    
    for i in range(1, 4):
        reserva_strikes = Reserva(id_reserva=f"R00{3+i}", cancha=cancha, solicitante=estudiante, rango=rango_tarde)
        estudiante.cancelar_reserva(reserva_strikes, tiempo_tardio)
        print(f" > Strike {i} aplicado. Reserva mutada a: [{reserva_strikes.estado.value}] | Faltas acumuladas de Ana: {estudiante.contador_no_shows}")
    
    print(f" > Estado de suspensión de Ana tras 3 faltas: Suspendida = {estudiante.suspendido}")
    print("\n=== FIN DE LA SIMULACIÓN DE REQUERIMIENTOS ===")

if __name__ == "__main__":
    ejecutar_simulacion()