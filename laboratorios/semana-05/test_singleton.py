from singleton import GestorDeConfiguracion, reserva_permitida

def test_rechaza_reserva():
    config = GestorDeConfiguracion.obtener_objeto()
    config.modo_mantenimiento = True

    assert reserva_permitida(config) is False

    # LIMPIEZA BÁSICA: Devolvemos el valor a su estado original
    config.modo_mantenimiento = False

def test_reserva_aceptada():
    config = GestorDeConfiguracion.obtener_objeto()

    # Ahora sí pasará, porque la prueba anterior dejó la casa limpia
    assert reserva_permitida(config) is True