from abc import ABC, abstractmethod

class EstrategiaDescuento(ABC):
    @abstractmethod
    def aplicar(self, precio_base):
        pass

class SinDescuento(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base

class DescuentoVip(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.8  # 20% de descuento

class DescuentoEstudiante(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.95  # 50% de descuento

class DescuentoEmpleado(EstrategiaDescuento):
    def aplicar(self, precio_base):
        return precio_base * 0.75  # 25% de descuento

class Compra:
    def __init__(self, estrategiaDesceunto):
        self.estrategiaDesceunto = estrategiaDesceunto

    def calcular_total(self, precio):
        return self.estrategiaDesceunto.aplicar(precio)

def main ():

    sin_descuento = SinDescuento()
    vip_descuento = DescuentoVip()
    estudiante_descuento = DescuentoEstudiante()
    empleado_descuento = DescuentoEmpleado()

    compra_1 = Compra(sin_descuento)
    print("Precio final sin descuento: ", compra_1.calcular_total(100))

    compra_2 = Compra(vip_descuento)
    print("Precio final con descuento VIP: ", compra_2.calcular_total(100))

    compra_3 = Compra(estudiante_descuento)
    print("Precio final con descuento Estudiante: ", compra_3.calcular_total(100))

    compra_4 = Compra(empleado_descuento)
    print("Precio final con descuento Empleado: ", compra_4.calcular_total(100))

main()

