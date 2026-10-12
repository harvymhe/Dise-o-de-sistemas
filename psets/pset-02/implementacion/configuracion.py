"""Singleton: una fuente para los cinco parámetros solicitados por Tecnología."""
from datetime import time, timedelta
from threading import Lock


class ConfiguracionReglas:
    _instancia = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instancia is None:
                obj = super().__new__(cls)
                obj.limite_prioridad = time(18)
                obj.ventana_regular = timedelta(hours=2)
                obj.ventana_oficial = timedelta(hours=24)
                obj.umbral_mensual = 3
                obj.duracion_suspension = timedelta(days=7)
                cls._instancia = obj
            return cls._instancia

    @classmethod
    def obtener(cls):
        return cls()
