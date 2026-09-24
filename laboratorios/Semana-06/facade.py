class Inventario:
    def verificar(self, producto):
        print(f"Verificando disponibilidad del producto: {producto}")
        return True 

class Pago:
    def procesar(self, monto):
        print(f"Procesando pago: {monto}")
        return True

class Envio:
    def crear_envio(self, producto):
        print(f"Preparando envío para el producto: {producto}")
        return True

class Notificacion:
    def enviar(self, mensaje):
        print(f"Notificación: {mensaje}")

class TiendaFacade:
    def __init__(self):
        self.inventario = Inventario()
        self.pago = Pago()
        self.envio = Envio()
        self.notificacion = Notificacion()

    def comprar(self, producto, precio):
        if not self.inventario.verificar(producto):
            print("Producto no disponible en inventario.")
            return

        if not self.pago.procesar(precio):
            print("Error en el procesamiento del pago.")
            return

        if not self.envio.crear_envio(producto):
            print("Error al crear el envío.")
            return

        print("Compra completada exitosamente.")
        self.notificacion.enviar(
            f"Tu compra de {producto} fue enviada correctamente."
        )

def main():

    tienda = TiendaFacade()

    tienda.comprar("Laptop", 1000)

main()