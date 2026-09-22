import copy

class Computadora:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.disco = None
        self.gpu = None
        self.wifi = None

    def mostrar(self):
        print('CPU: ', self.cpu)
        print('RAM: ', self.ram)
        print('Disco: ', self.disco)
        print('GPU: ', self.gpu)
        print('WiFi: ', self.wifi)

    def clonar(self):
        return copy.deepcopy(self)

class ComputadoraBuilder:
    def __init__(self):
        self.computadora = Computadora()

    def set_cpu(self, cpu):
        self.computadora.cpu = cpu
        return self

    def set_ram(self, ram):
        self.computadora.ram = ram
        return self

    def set_disco(self, disco):
        self.computadora.disco = disco
        return self

    def set_gpu(self, gpu):
        self.computadora.gpu = gpu
        return self

    def set_wifi(self, wifi):
        self.computadora.wifi = wifi
        return self

    def build(self):
        return self.computadora

def main():
    pc_builder = ComputadoraBuilder()

    pc_builder = pc_builder.set_cpu('i7').set_ram(4).set_disco('1TB').set_gpu('18').set_wifi(True)
    pc = pc_builder.build()
    pc.mostrar()

    pc_work = pc.clonar()
    pc_work.ram = 16
    pc_work.disco = '2TB'
    pc_work.mostrar()

if __name__ == '__main__':
    main()